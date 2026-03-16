"""
Simple task queue for async report generation
Uses threading and a queue to handle concurrent analysis jobs
"""

import threading
import queue
import uuid
import logging
from typing import Dict, Callable, Any

class Task:
    """Represents a processing task"""
    def __init__(self, task_id: str, job_type: str, params: Dict):
        self.task_id = task_id
        self.job_type = job_type
        self.params = params
        self.status = 'queued'  # queued, processing, completed, failed
        self.result = None
        self.error = None
        self.progress = 0

class TaskQueue:
    """Async task queue with threading"""
    def __init__(self, max_workers: int = 2, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
        self.queue = queue.Queue()
        self.tasks: Dict[str, Task] = {}
        self.max_workers = max_workers
        self.workers = []
        self.handlers: Dict[str, Callable] = {}
        self.running = False
        
        self.logger.info(f"✅ TaskQueue initialized (max_workers={max_workers})")
    
    def register_handler(self, job_type: str, handler: Callable):
        """Register a handler for a job type"""
        self.handlers[job_type] = handler
        self.logger.info(f"   Registered handler for: {job_type}")
    
    def submit_task(self, job_type: str, params: Dict) -> str:
        """Submit a new task and return task_id"""
        task_id = str(uuid.uuid4())[:8]
        task = Task(task_id, job_type, params)
        self.tasks[task_id] = task
        self.queue.put(task)
        self.logger.info(f"📌 Task queued: {task_id} ({job_type})")
        return task_id
    
    def get_task(self, task_id: str) -> Task:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def start(self):
        """Start worker threads"""
        if self.running:
            return
        self.running = True
        for i in range(self.max_workers):
            w = threading.Thread(target=self._worker, daemon=True, name=f"worker-{i}")
            w.start()
            self.workers.append(w)
        self.logger.info(f"✅ Started {self.max_workers} worker threads")
    
    def stop(self):
        """Stop all workers"""
        self.running = False
        for w in self.workers:
            w.join(timeout=1)
        self.logger.info("✅ All workers stopped")
    
    def _worker(self):
        """Worker thread that processes tasks from queue"""
        while self.running:
            try:
                task = self.queue.get(timeout=1)
                self._process_task(task)
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"❌ Worker error: {e}")
    
    def _process_task(self, task: Task):
        """Process a single task"""
        try:
            task.status = 'processing'
            task.progress = 0
            self.logger.info(f"🔄 Processing: {task.task_id}")
            
            handler = self.handlers.get(task.job_type)
            if not handler:
                raise ValueError(f"No handler for job type: {task.job_type}")
            
            result = handler(task.params)
            task.result = result
            task.status = 'completed'
            task.progress = 100
            self.logger.info(f"✅ Completed: {task.task_id}")
            
        except Exception as e:
            task.error = str(e)
            task.status = 'failed'
            self.logger.error(f"❌ Failed: {task.task_id} - {e}")
