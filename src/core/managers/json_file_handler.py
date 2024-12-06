import os
import sys
import json
import shutil
import logging

class JsonFileHandler:
    def __init__(self):
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Initialize paths
        self.app_data_dir = self._get_app_data_path()
        self.source_data_dir = self._get_source_data_dir()
        
        # List of required JSON files
        self.json_files = [
            'chromedriver_config.json',
            'chat_ids.json',
            'telegram_config.json',
            'Actived_tasks.json'
        ]
        
        # Ensure files are set up properly
        self.initialize_files()

    def _get_app_data_path(self):
        """Get the AppData directory path and create it if it doesn't exist"""
        app_folder = os.path.join(os.getenv('APPDATA'), 'TikTok_Bot')
        os.makedirs(app_folder, exist_ok=True)
        self.logger.info(f"AppData directory: {app_folder}")
        return app_folder

    def _get_source_data_dir(self):
        """Get the source data directory path based on whether running as exe or script"""
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            source_dir = os.path.join(sys._MEIPASS, 'data')
        else:
            # Running as script
            source_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
        
        self.logger.info(f"Source data directory: {source_dir}")
        return source_dir

    def initialize_files(self):
        """Initialize JSON files in AppData directory"""
        try:
            for filename in self.json_files:
                app_data_file = os.path.join(self.app_data_dir, filename)
                source_file = os.path.join(self.source_data_dir, filename)
                
                if not os.path.exists(app_data_file):
                    if os.path.exists(source_file):
                        shutil.copy2(source_file, app_data_file)
                        self.logger.info(f"Successfully copied {filename} to AppData")
                    else:
                        self.logger.error(f"Source file not found: {source_file}")
                        # Create default file structure
                        self._create_default_file(filename)
        except Exception as e:
            self.logger.error(f"Error initializing files: {str(e)}")
            raise

    def _create_default_file(self, filename):
        """Create a default JSON file with basic structure"""
        default_structures = {
            'chromedriver_config.json': {'driver_path': ''},
            'chat_ids.json': [],
            'telegram_config.json': {'bot_token': '', 'chat_ids': []},
            'Actived_tasks.json': []
        }
        
        file_path = os.path.join(self.app_data_dir, filename)
        with open(file_path, 'w') as f:
            json.dump(default_structures.get(filename, {}), f, indent=4)
        self.logger.info(f"Created default file: {filename}")

    def get_file_path(self, filename):
        """Get the full path to a JSON file in the AppData directory"""
        return os.path.join(self.app_data_dir, filename)

    def read_json(self, filename):
        """Read and return JSON file contents"""
        try:
            with open(self.get_file_path(filename), 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error reading {filename}: {str(e)}")
            return None

    def write_json(self, filename, data):
        """Write data to a JSON file"""
        try:
            with open(self.get_file_path(filename), 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            self.logger.error(f"Error writing {filename}: {str(e)}")
            return False
        
# In json_file_handler.py

# First, we keep our JsonFileHandler class as shown before...

# Then add this standalone function at the bottom of the file:
# def get_json_path(filename):
#     # Create a JsonFileHandler instance (it will initialize files if needed)
#     handler = JsonFileHandler()
#     # Use the class's get_file_path method
#     return handler.get_file_path(filename)




def get_app_data_path():
    """Get the path where we can safely store and update our JSON files"""
    # Use AppData on Windows, which is ideal for app data storage
    app_folder = os.path.join(os.getenv('APPDATA'), 'TikTok_Bot') if os.name == 'nt' else os.path.expanduser('~/.tiktok_bot')
    
    # Create the directory if it doesn't exist
    if not os.path.exists(app_folder):
        os.makedirs(app_folder)
    
    return app_folder

def setup_json_files():
    """Set up JSON files in the correct location for read/write access"""
    app_data = get_app_data_path()

    # Determine the original data directory
    original_data_dir = os.path.join(sys._MEIPASS, 'data') if hasattr(sys, '_MEIPASS') else 'data'

    print(f"App Data Directory: {app_data}")
    print(f"Original Data Directory: {original_data_dir}")

    json_files = [
        'chromedriver_config.json',
        'chat_ids.json',
        'telegram_config.json',
        'Actived_tasks.json',
    ]

    for filename in json_files:
        print(f"Checking {filename}...")
        app_data_file = os.path.join(app_data, filename)
        original_file = os.path.join(original_data_dir, filename)

        if not os.path.exists(app_data_file):
            if os.path.exists(original_file):
                shutil.copy2(original_file, app_data_file)
                print(f"Copied {filename} to app data directory.")
            else:
                print(f"Error: {original_file} not found. Ensure the file is bundled correctly.")

    return app_data


# Function to get the correct path for any JSON file
def get_json_path(filename):
    return os.path.join(get_app_data_path(), filename)