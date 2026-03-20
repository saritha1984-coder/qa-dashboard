import requests
import os
from datetime import datetime
from base64 import b64encode
from azure.storage.blob import BlobClient

# Configuration
ORG = "thinkfinance-vsts"
PROJECT = "Think"
PAT = os.getenv('PAT_TOKEN')
STORAGE_KEY = os.getenv('STORAGE_KEY')

# Create auth header
auth = b64encode((':' + PAT).encode()).decode()
headers = {'Authorization': f'Basic {auth}'}

# WIQL query to fetch bugs
wiql = {
    'query': 'SELECT [System.Id], [System.Title], [System.State] FROM workitems WHERE [System.WorkItemType] = "Bug" AND [System.AreaPath] UNDER "Think\\AppDev" ORDER BY [System.Id] DESC'
}

try:
    # Fetch defects from Azure DevOps
    url = f'https://dev.azure.com/{ORG}/{PROJECT}/_apis/wit/wiql?api-version=7.0'
    response = requests.post(url, json=wiql, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        defect_count = len(data.get('workItems', []))
        
        # Generate HTML dashboard
        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>QA Defects Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        h1 {{ color: #333; }}
        .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f0f0f0; padding: 15px; border-radius: 5px; flex: 1; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .timestamp {{ color: #999; font-size: 12px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>QA Defects Dashboard</h1>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{defect_count}</div>
                <div class="stat-label">Total Defects</div>
            </div>
        </div>
        <p>This dashboard auto-refreshes every 6 hours from Azure DevOps.</p>
        <div class="timestamp">Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S CST')}</div>
    </div>
</body>
</html>'''
        
        # Upload to Azure Blob Storage
        conn_str = f'DefaultEndpointsProtocol=https;AccountName=tlmpqastorage;AccountKey={STORAGE_KEY};EndpointSuffix=core.windows.net'
        blob = BlobClient.from_connection_string(
            conn_str,
            container_name='qa-dashboards',
            blob_name='QA_Defects_Dashboard.html'
        )
        blob.upload_blob(html_content, overwrite=True)
        print('Dashboard updated successfully!')
        print(f'Total defects: {defect_count}')
    else:
        print(f'Error fetching defects: {response.status_code}')
        print(f'Response: {response.text}')
        
except Exception as e:
    print(f'Error: {str(e)}')
