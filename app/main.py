import os
import logging
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from azure.identity import DefaultAzureCredential
from azure_scanner import scan_full_environment, scan_targeted_resource
from risk_analyzer import analyze_for_risks_and_dependencies
from visualizer import create_graph_visualization

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(title='Agentic Azure Visualizer')
templates = Jinja2Templates(directory='app/templates')
os.makedirs('reports', exist_ok=True)
app.mount('/reports', StaticFiles(directory='reports'), name='reports')

job_status = {'status': 'idle', 'message': 'Ready to start.', 'report_path': None}

def run_full_scan_and_generate_report():
    try:
        job_status.update({'status': 'running', 'message': 'Initializing Azure credentials...'})
        credential = DefaultAzureCredential()
        job_status['message'] = 'Scanning all Azure resources... This may take several minutes.'
        (all_resources, subscriptions) = scan_full_environment(credential)
        job_status['message'] = f'Scan complete. Found {len(all_resources)} resources. Analyzing dependencies and risks...'
        analyzed_graph = analyze_for_risks_and_dependencies(all_resources, subscriptions)
        job_status['message'] = 'Generating interactive visualization...'
        report_filename = create_graph_visualization(analyzed_graph)
        job_status.update({'status': 'complete', 'message': f'Report generated successfully.', 'report_path': f'/reports/{report_filename}'})
    except Exception as e:
        logging.error(f'Full scan failed: {e}', exc_info=True)
        job_status.update({'status': 'error', 'message': f'An error occurred: {str(e)}'})

@app.get('/', response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.post('/scan/full')
async def trigger_full_scan(background_tasks: BackgroundTasks):
    if job_status['status'] == 'running':
        return JSONResponse(status_code=409, content={'message': 'A scan is already in progress.'})
    background_tasks.add_task(run_full_scan_and_generate_report)
    return JSONResponse(status_code=202, content={'message': 'Full environment scan initiated.'})

@app.get('/status')
async def get_status():
    return JSONResponse(content=job_status)
