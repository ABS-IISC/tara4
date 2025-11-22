"""
Thread Pool Task Manager - Replacement for Celery
Simple, efficient task queue using ThreadPoolExecutor
"""

from concurrent.futures import ThreadPoolExecutor, Future
import uuid
import time
from typing import Dict, Callable, Any, Optional
import threading
import traceback
from datetime import datetime

class TaskManager:
    """
    Simple task manager using ThreadPoolExecutor

    Replaces Celery with a simpler in-memory solution.
    Perfect for I/O-bound tasks like Bedrock API calls.

    Features:
    - Non-blocking task submission
    - Task status polling (compatible with existing frontend)
    - Automatic cleanup of old tasks
    - Thread pool management
    - Error handling and recovery
    """

    def __init__(self, max_workers: int = 10, cleanup_interval: int = 300):
        """
        Initialize task manager

        Args:
            max_workers: Maximum number of concurrent threads
            cleanup_interval: Cleanup interval in seconds (default 5 minutes)
        """
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix='aiprism_worker'
        )
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
        self.max_workers = max_workers
        self.cleanup_interval = cleanup_interval

        # Start cleanup thread
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_old_tasks,
            daemon=True,
            name='task_cleanup'
        )
        self._cleanup_thread.start()

        print(f"✅ TaskManager initialized with {max_workers} workers")

    def submit_task(self, func: Callable, *args, **kwargs) -> str:
        """
        Submit a task for execution

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            task_id: Unique identifier for the task
        """
        task_id = str(uuid.uuid4())

        # Wrap function to capture exceptions
        def wrapped_func():
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"❌ Task {task_id[:8]} failed: {str(e)}")
                traceback.print_exc()
                raise

        future = self.executor.submit(wrapped_func)

        with self.lock:
            self.tasks[task_id] = {
                'future': future,
                'created': time.time(),
                'status': 'PENDING',
                'function': func.__name__,
                'started': None,
                'completed': None
            }

        print(f"📤 Task {task_id[:8]} submitted: {func.__name__}")
        return task_id

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get status of a task

        Args:
            task_id: Task identifier

        Returns:
            Dictionary with status, result, or error
        """
        with self.lock:
            if task_id not in self.tasks:
                return {
                    'status': 'NOT_FOUND',
                    'error': f'Task {task_id} not found'
                }

            task_info = self.tasks[task_id]
            future = task_info['future']

            if future.done():
                if task_info['completed'] is None:
                    task_info['completed'] = time.time()

                try:
                    result = future.result()
                    task_info['status'] = 'SUCCESS'

                    duration = task_info['completed'] - task_info['created']

                    return {
                        'status': 'SUCCESS',
                        'result': result,
                        'duration': round(duration, 2),
                        'function': task_info['function']
                    }
                except Exception as e:
                    task_info['status'] = 'FAILURE'
                    return {
                        'status': 'FAILURE',
                        'error': str(e),
                        'error_type': type(e).__name__,
                        'function': task_info['function']
                    }
            else:
                # Mark as started if not already
                if task_info['started'] is None:
                    task_info['started'] = time.time()

                return {
                    'status': 'PENDING',
                    'function': task_info['function'],
                    'elapsed': round(time.time() - task_info['created'], 2)
                }

    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all tasks"""
        with self.lock:
            return {
                task_id: {
                    'status': self.get_task_status(task_id)['status'],
                    'function': task_info['function'],
                    'created': task_info['created'],
                    'age': time.time() - task_info['created']
                }
                for task_id, task_info in self.tasks.items()
            }

    def cancel_task(self, task_id: str) -> bool:
        """
        Attempt to cancel a task

        Args:
            task_id: Task identifier

        Returns:
            True if cancelled, False otherwise
        """
        with self.lock:
            if task_id not in self.tasks:
                return False

            future = self.tasks[task_id]['future']
            cancelled = future.cancel()

            if cancelled:
                self.tasks[task_id]['status'] = 'CANCELLED'
                print(f"❌ Task {task_id[:8]} cancelled")

            return cancelled

    def get_stats(self) -> Dict[str, Any]:
        """Get task manager statistics"""
        with self.lock:
            total = len(self.tasks)
            statuses = {}

            for task_info in self.tasks.values():
                status = task_info['status']
                statuses[status] = statuses.get(status, 0) + 1

            return {
                'total_tasks': total,
                'max_workers': self.max_workers,
                'statuses': statuses,
                'active_tasks': statuses.get('PENDING', 0),
                'completed_tasks': statuses.get('SUCCESS', 0),
                'failed_tasks': statuses.get('FAILURE', 0)
            }

    def _cleanup_old_tasks(self):
        """
        Background thread to remove completed tasks older than 1 hour
        Runs every cleanup_interval seconds
        """
        while True:
            try:
                time.sleep(self.cleanup_interval)
                current_time = time.time()

                with self.lock:
                    to_remove = []

                    for task_id, task_info in self.tasks.items():
                        future = task_info['future']

                        # Remove if done and older than 1 hour
                        if future.done():
                            age = current_time - task_info['created']
                            if age > 3600:  # 1 hour
                                to_remove.append(task_id)

                    for task_id in to_remove:
                        del self.tasks[task_id]

                    if to_remove:
                        print(f"🧹 Cleaned up {len(to_remove)} old tasks")

            except Exception as e:
                print(f"⚠️ Cleanup error: {e}")

    def shutdown(self, wait: bool = True):
        """
        Graceful shutdown of task manager

        Args:
            wait: Wait for pending tasks to complete
        """
        print("🛑 Shutting down TaskManager...")
        self.executor.shutdown(wait=wait)
        print("✅ TaskManager shut down")


# Global singleton instance
_task_manager: Optional[TaskManager] = None
_manager_lock = threading.Lock()

def get_task_manager(max_workers: int = 10) -> TaskManager:
    """
    Get or create the global task manager instance

    Args:
        max_workers: Maximum number of concurrent threads

    Returns:
        TaskManager instance
    """
    global _task_manager

    with _manager_lock:
        if _task_manager is None:
            _task_manager = TaskManager(max_workers=max_workers)

        return _task_manager


# Graceful shutdown on exit
import atexit

def _shutdown_task_manager():
    """Shutdown task manager on program exit"""
    global _task_manager
    if _task_manager is not None:
        _task_manager.shutdown(wait=False)

atexit.register(_shutdown_task_manager)
