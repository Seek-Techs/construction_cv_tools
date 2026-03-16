"""
Construction CV Inspector - Phase 5 Web Application
Complete Flask app with async task queue, file upload, and report download
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import logging
from pathlib import Path
from utils import load_config, setup_logging
from site_comparator import SiteComparator
from task_queue import TaskQueue
from datetime import datetime

# Initialize app
app = Flask(__name__, template_folder='templates')
config = load_config()
logger = setup_logging(config.get('log_level', 'INFO'))

# Configuration
UPLOAD_FOLDER = config.get('upload_dir', 'uploads')
REPORT_FOLDER = config.get('report_output_dir', 'reports')
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf', 'gif', 'bmp'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize services
comparator = SiteComparator(config, logger)
task_queue = TaskQueue(max_workers=2, logger=logger)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_photos_handler(params):
    """Handler for photo analysis task"""
    site_photo = params.get('site_photo')
    pdf_photo = params.get('pdf_photo')
    
    logger.info(f"🔄 Handler: Starting analysis for {site_photo} vs {pdf_photo}")
    
    # Run analysis (Phases 1-3 + Phase 4)
    report = comparator.match_and_analyze(site_photo, pdf_photo)
    
    if report is None:
        raise ValueError("Analysis failed - no report generated")
    
    # Get generated report files
    pdf_file = os.path.basename(os.path.join(REPORT_FOLDER, 'analysis_report.pdf'))
    csv_file = os.path.basename(os.path.join(REPORT_FOLDER, 'analysis_report.csv'))
    
    logger.info(f"✅ Handler: Analysis complete, reports: {pdf_file}, {csv_file}")
    
    return {
        'pdf': pdf_file,
        'csv': csv_file,
        'summary': report.get('summary', {})
    }

# Register handler
task_queue.register_handler('analyze_photos', analyze_photos_handler)
task_queue.start()

# Routes

@app.route('/')
def index():
    """Serve main web UI"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """Upload files and submit analysis task"""
    try:
        # Get files
        site_file = request.files.get('sitePhoto')
        pdf_file = request.files.get('pdfPhoto')
        
        if not site_file or not pdf_file:
            return jsonify({'error': 'Missing files'}), 400
        
        if not allowed_file(site_file.filename) or not allowed_file(pdf_file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Save uploaded files
        site_filename = secure_filename(site_file.filename)
        pdf_filename = secure_filename(pdf_file.filename)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        site_path = os.path.join(UPLOAD_FOLDER, timestamp + site_filename)
        pdf_path = os.path.join(UPLOAD_FOLDER, timestamp + pdf_filename)
        
        site_file.save(site_path)
        pdf_file.save(pdf_path)
        
        logger.info(f"✅ Files uploaded: {site_path}, {pdf_path}")
        
        # Submit task to queue
        task_id = task_queue.submit_task('analyze_photos', {
            'site_photo': site_path,
            'pdf_photo': pdf_path
        })
        
        return jsonify({'task_id': task_id, 'status': 'queued'}), 202
    
    except Exception as e:
        logger.error(f"❌ Upload error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks with status"""
    tasks = []
    for task_id, task in task_queue.tasks.items():
        tasks.append({
            'task_id': task.task_id,
            'job_type': task.job_type,
            'status': task.status,
            'progress': task.progress,
            'result': task.result,
            'error': task.error
        })
    return jsonify({'tasks': tasks})

@app.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get single task status"""
    task = task_queue.get_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify({
        'task_id': task.task_id,
        'job_type': task.job_type,
        'status': task.status,
        'progress': task.progress,
        'result': task.result,
        'error': task.error
    })

@app.route('/reports', methods=['GET'])
def list_reports():
    """List available reports"""
    if not os.path.isdir(REPORT_FOLDER):
        return jsonify({'reports': []})
    files = [f for f in os.listdir(REPORT_FOLDER) if f.endswith(('.pdf', '.csv'))]
    return jsonify({'reports': sorted(files, reverse=True)})

@app.route('/reports/<filename>', methods=['GET'])
def get_report(filename):
    """Download report file"""
    return send_from_directory(REPORT_FOLDER, secure_filename(filename), as_attachment=True)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'tasks_total': len(task_queue.tasks),
        'queue_size': task_queue.queue.qsize()
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    try:
        logger.info("🚀 Starting Construction CV Inspector Web App")
        logger.info(f"   Upload folder: {UPLOAD_FOLDER}")
        logger.info(f"   Report folder: {REPORT_FOLDER}")
        logger.info("   Open http://localhost:5000 in your browser")
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        logger.info("⏹️  Shutting down...")
        task_queue.stop()
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        raise
