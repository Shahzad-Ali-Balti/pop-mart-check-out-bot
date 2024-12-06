from selenium.webdriver.common.by import By
import logging
import time
from PyQt6.QtCore import QThread
from urllib.parse import unquote
import json
from datetime import datetime
# from src.core.managers.persistence_manager import MonitoringTask
from src.core.managers.web_monitor import WebMonitor
from src.core.notifications.send_notifications import send_notifications
import uuid
from concurrent.futures import ThreadPoolExecutor
import asyncio

class ProductMonitorWorker(QThread):
    running_tasks = set()

    def __init__(self, driver_path, table_widget, persistence_manager, url, check_interval=30):
        super().__init__()
        self.driver_path = driver_path
        self.table_widget = table_widget
        self.persistence_manager = persistence_manager
        self.url = url
        self.check_interval = check_interval
        self.keep_running = True
        self.task_id = str(uuid.uuid4())
        self.web_monitor = None

        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

        self.table_widget.update_product_name(self.task_id, "Loading")
        self.table_widget.update_monitoring_status(self.task_id, "Active")
        self.table_widget.update_product_status(self.task_id, "Searching")
        self.table_widget.update_notification_status(self.task_id, "Pending")

        ProductMonitorWorker.running_tasks.add(self.task_id)

    def run(self):
        try:
            # Step 1: Initialize Browser and Open URL
            self.logger.info("Initializing browser and opening URL")
            self.web_monitor = WebMonitor(self.driver_path)
            self.web_monitor.open_url(self.url)

            # Step 2: Fetch Product Information
            product_info = self.web_monitor.fetch_product_info()
            self.logger.info(f"Product Info: {product_info}")
            self.table_widget.update_product_name(self.task_id, product_info.get('name', 'Unknown'))
            self.table_widget.update_product_status(self.task_id, "Product Found")

            # Step 3: Update Cart Input Value
            # if self.web_monitor.update_cart_input_value("1"):
            #     self.logger.info("Cart input value successfully updated")
            # else:
            #     self.logger.warning("Failed to update cart input value")

            # Step 4: Click Add to Cart Button
            if self.web_monitor.click_add_to_cart_button():
                self.logger.info("Successfully clicked Add to Cart button")
                # self.table_widget.update_monitoring_status(self.task_id, "Added to Cart")
            else:
                self.logger.warning("Failed to click Add to Cart button")
                self.table_widget.update_monitoring_status(self.task_id, "Failed to Add to Cart")

        except Exception as e:
            self.logger.error(f"Error in monitoring task: {e}")
            self.table_widget.update_monitoring_status(self.task_id, "Error")
        finally:
            # Clean up resources
            # self.web_monitor.cleanup()
            self.logger.info("Browser cleanup completed")
            self.table_widget.update_monitoring_status(self.task_id, "Completed")
            ProductMonitorWorker.running_tasks.remove(self.task_id)



    # def run(self):
    #     """Main monitoring loop that alternates between checking for available and unavailable status"""
    #     try:
    #         self.logger.info('Starting Main Loop: Browser Initialization')
    #         # Initialize browser and load URL
    #         if not self.initialize_browser_and_load_url():
    #             raise Exception("Failed to initialize browser")
    #         self.logger.info('Browser Initialized Successfully')

    #         while self.keep_running:
    #             # Step 1: Check for availability
    #             self.logger.info('Checking Available Status')
    #             available_result = self.get_available_status()
                
    #             if not available_result:
    #                 continue

    #             self.table_widget.update_product_name(self.task_id, available_result['product_title'])
                
    #             if available_result['availability']:
    #                 self.logger.info('Product Available - Sending Notification')
    #                 self.table_widget.update_product_status(self.task_id, "Available")
    #                 self.table_widget.update_monitoring_status(self.task_id, "Active")
                    
    #                 # Send notifications using ThreadPoolExecutor
    #                 with ThreadPoolExecutor() as executor:
    #                     futures = [
    #                         executor.submit(
    #                             asyncio.run,
    #                             send_notifications(
    #                                 available_result['product_title'],
    #                                 available_result['product_url'],
    #                                 available_result['formatted_products']
    #                             )
    #                         )
    #                     ]
    #                     for future in futures:
    #                         try:
    #                             results = future.result()
    #                             all_sent = True
                                
    #                             for result in results:
    #                                 if result["success"]:
    #                                     self.logger.info(f"Notification sent to chat ID {result['chat_id']}, Message ID: {result['message_id']}")
    #                                 else:
    #                                     self.logger.error(f"Failed to send to chat ID {result['chat_id']}: {result['error']}")
    #                                     all_sent = False
                                
    #                             self.table_widget.update_notification_status(
    #                                 self.task_id, 
    #                                 "Sent" if all_sent else "Failed"
    #                             )
    #                         except Exception as e:
    #                             self.logger.error(f"Error sending notifications: {e}")
    #                             self.table_widget.update_notification_status(self.task_id, "Error")

                    
    #                 # After sending notification, start checking for unavailability
    #                 while self.keep_running:
    #                     self.logger.info('Checking Unavailable Status')
    #                     unavailable_result = self.get_unavailable_status()
                        
    #                     if not unavailable_result:
    #                         continue
                            
    #                     if unavailable_result['Un_availabile']:
    #                         self.logger.info('Product Became Unavailable - Restarting Availability Check')
    #                         self.logger.info('<-------------->Gotcha<---------------->')
    #                         self.table_widget.update_product_status(self.task_id, "Unavailable")
    #                         break  # Break inner loop to restart availability check
                            
    #                     if self.keep_running:
    #                         time.sleep(self.check_interval)
    #                         self.reload_page()
    #                         self.logger.info('Continuing Unavailability Check')
    #                         self.logger.info('<------------------------------>')

                
    #             else:
    #                 self.table_widget.update_product_status(self.task_id, "Unavailable")
    #                 self.logger.info('1st Iteration Product Unavailable - Continuing Availability Check')
    #                 self.logger.info('<-------------123----------------->')
                    
    #                 if self.keep_running:
    #                     time.sleep(self.check_interval)
    #                     self.reload_page()
    #                     self.logger.info('- Continuing Availability Check')

    #     except Exception as e:
    #         self.logger.error(f"Error in monitoring loop: {e}")
    #         self.table_widget.update_monitoring_status(self.task_id, "Error")
    #         self.table_widget.update_product_status(self.task_id, "Error")
    #         self.table_widget.update_notification_status(self.task_id, "Failed")
    #         self.stop()
    #         self.logger.error(f'Task Stopped-ERROR{e}')

    #     finally:
    #         if self.web_monitor:
    #             self.close_browser()


#     def stop(self, task_id=None):
#         """Handle manual stopping of individual task"""
#         if task_id is None:
#             task_id = self.task_id
#         self.logger.info('Task is being stopped')
#         # Remove from running tasks set
#         self.keep_running = False
#         ProductMonitorWorker.running_tasks.discard(task_id)
#         self.close_browser()

# @classmethod
# def stop_all(cls):
#     """Stop all running tasks"""
#     for task_id in list(cls.running_tasks):
#         task = cls.running_tasks[task_id]
#         task.stop()