import sys
import logging
import os
import json
import traceback
from PyQt6.QtWidgets import QApplication
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from src.ui.main_window import MainWindow
from src.ui.components.table_widget import TableWidget
from webdriver_manager.chrome import ChromeDriverManager as WDManager
from src.core.product_monitor import ProductMonitorWorker
import threading
from src.core.notifications import telegram_bot
import asyncio
import nest_asyncio
from src.core.managers.json_file_handler import JsonFileHandler

def setup_logging():
    """Configure and initialize application-wide logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

class ChromeDriverManager:
    def __init__(self, file_handler):
        """Initialize ChromeDriver manager with file handling capabilities"""
        self.file_handler = file_handler
        self.logger = logging.getLogger(__name__)

    def save_driver_path(self, driver_path):
        """Save ChromeDriver path using the file handler"""
        try:
            self.logger.info('New Driver is installing')
            return self.file_handler.write_json(
                "chromedriver_config.json", 
                {"driver_path": driver_path}
            )
        except Exception as e:
            self.logger.error(f"Error saving driver path: {e}")
            raise

    def load_driver_path(self):
        """Load ChromeDriver path using the file handler"""
        try:
            data = self.file_handler.read_json("chromedriver_config.json")
            if data:
                return data.get("driver_path")
        except Exception as e:
            self.logger.error(f"Error loading driver path: {e}")
        return None

    def initialize_driver_path(self):
        """Initialize and verify ChromeDriver installation"""
        try:
            # Check for existing driver
            saved_path = self.load_driver_path()
            if saved_path and os.path.isfile(os.path.join(saved_path, "chromedriver.exe")):
                self.logger.info(f"Using existing ChromeDriver at: {saved_path}")
                return saved_path

            # Install new driver if necessary
            self.logger.info("Installing new ChromeDriver...")
            full_path = WDManager().install()
            driver_path = os.path.dirname(full_path)
            self.save_driver_path(driver_path)
            self.logger.info(f"New ChromeDriver installed at: {driver_path}")
            return driver_path

        except Exception as e:
            self.logger.error(f"Error initializing ChromeDriver: {e}")
            raise

class ApplicationManager:
    """Manages the core application lifecycle and components"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.app = None
        self.main_window = None
        self.file_handler = JsonFileHandler()
        self.chrome_manager = ChromeDriverManager(self.file_handler)

    def initialize_application(self):
        """Initialize core application components"""
        self.app = QApplication(sys.argv)
        nest_asyncio.apply()
        return self.app

    def start_telegram_bot(self):
        """Initialize and start the Telegram bot in a separate thread"""
        bot_thread = threading.Thread(
            target=lambda: asyncio.run(telegram_bot.run_bot())
        )
        bot_thread.daemon = True
        bot_thread.start()

    def cleanup(self):
        """Perform application cleanup operations"""
        try:
            if self.main_window:
                self.main_window.stop_all_monitoring()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def run(self):
        """Main application execution flow"""
        try:
            # Initialize application
            self.initialize_application()

            # Start Telegram bot
            self.start_telegram_bot()

            # Initialize ChromeDriver
            driver_path = self.chrome_manager.initialize_driver_path()

            # Create and show main window
            table_widget = TableWidget()
            self.main_window = MainWindow(
                driver_path=driver_path,
                table_widget=table_widget
            )
            self.main_window.show()

            # Set up cleanup handler
            self.app.aboutToQuit.connect(self.cleanup)

            # Start application event loop
            return self.app.exec()

        except Exception as e:
            self.logger.error(f"Critical error during initialization: {e}")
            self.logger.error(traceback.format_exc())
            raise

def main():
    """Application entry point with error handling"""
    try:
        app_manager = ApplicationManager()
        return app_manager.run()
    except Exception as e:
        logging.error(f"Fatal application error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())