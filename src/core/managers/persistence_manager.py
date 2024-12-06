import json
import os
import logging
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from src.core.managers.json_file_handler import get_json_path

@dataclass
class MonitoringTask:
    url: str
    interval: int

file_path = get_json_path('Actived_tasks.json')
class PersistenceManager:
    def __init__(self, file_path=file_path):
        self.file_path = file_path
        self.logger = logging.getLogger(__name__)

    def load_active_tasks(self) -> List[MonitoringTask]:
        """Load active monitoring tasks from file"""
        try:
            if not os.path.exists(self.file_path):
                return []
                
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            
            tasks = [MonitoringTask(
                url=item['url'],
                interval=item['interval']
            ) for item in data]
            
            self.logger.info(f"Loaded {len(tasks)} tasks")
            return tasks
        except Exception as e:
            self.logger.error(f"Error loading tasks: {e}")
            return []
