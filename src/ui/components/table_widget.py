from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QHeaderView
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
import logging
import json
from PyQt6.QtGui import QPalette 
# from ui.main_window import MainWindow
class TableWidget(QTableWidget):
    status_updated = pyqtSignal(str, str, str)
    stop_monitoring = pyqtSignal(str)
    stop_task_signal = pyqtSignal(str)

    def __init__(self):  
        super().__init__()
        self.setup_table()
        # self.main_window = MainWindow(driver_path,table_widget)
        self.row_task_map = {}
        self.task_row_map = {}
        self.logger = logging.getLogger(__name__)

    def setup_table(self):
        """Initialize the table structure"""
        self.setColumnCount(12)
        self.setHorizontalHeaderLabels([
            "Product Name",
            "Price",
            "Launch Time",
            "Quantity",
            "Monitoring",
            "Product",
            "Cart",
            "Check Out",
            "Notification",
            "Action",
            "Interval",
            "URL"
        ])
        
        # Set column stretching
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)    
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)    
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)    
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)    
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)    
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(10, QHeaderView.ResizeMode.Fixed)    
        header.setSectionResizeMode(11, QHeaderView.ResizeMode.Fixed)      



        
        # Set fixed widths for status columns
        self.setColumnWidth(1, 80)  # Monitoring Status
        self.setColumnWidth(2, 100)  # Product Status
        self.setColumnWidth(3, 80)  # Notification Status
        self.setColumnWidth(4, 80)   # Action Button
        self.setColumnWidth(5, 80)   
        self.setColumnWidth(6, 80) 
        self.setColumnWidth(7, 80)   
        self.setColumnWidth(8, 80)
        self.setColumnWidth(9, 80)   
        self.setColumnWidth(10,80)
        self.setColumnWidth(11,80)   




        # Apply styling
        self.setStyleSheet("""
            QTableWidget {
                background-color: #2E3440;
                color: #D8DEE9;
                border: 1px solid #4C566A;
                gridline-color: #4C566A;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #5E81AC;
            }
            QHeaderView::section {
                background-color: #3B4252;
                color: #ECEFF4;
                padding: 5px;
                border: 1px solid #4C566A;
                font-weight: bold;
            }
            QTableCornerButton::section {
                background-color: #3B4252;  /* Add this line for corner button */
            }
            QTableView {
                border-top-left-radius: 0px;
                background-color: #3B4252;
            }
        """)
        
    def create_styled_item(self, text, status_type=None):
        """Create a styled table item based on status"""
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Set colors based on status
        if status_type == "monitoring":
            if text == "Active":
                item.setBackground(QColor("#A3BE8C"))  # Green
                item.setForeground(QColor("#000000"))  # Black text
            elif text == "Completed":
                item.setBackground(QColor("#88C0D0"))  # Blue
                item.setForeground(QColor("#000000"))
            elif text == "Stopped":
                item.setBackground(QColor("#BF616A"))  # Red
                item.setForeground(QColor("#FFFFFF"))  # White text
            elif text == "Error":
                item.setBackground(QColor("#B48EAD"))  # Purple
                item.setForeground(QColor("#FFFFFF"))
                
        elif status_type == "product":
            if text == "Available":
                item.setBackground(QColor("#A3BE8C"))
                item.setForeground(QColor("#000000"))
            elif text == "Unavailable":
                item.setBackground(QColor("#BF616A"))
                item.setForeground(QColor("#FFFFFF"))
            elif text == "Unknown":
                item.setBackground(QColor("#BF616A"))
                item.setForeground(QColor("#FFFFFF"))
            elif text == "Searching":
                item.setBackground(QColor("#EBCB8B"))  # Yellow
                item.setForeground(QColor("#000000"))
                
        elif status_type == "notification":
            if text == "Sent":
                item.setBackground(QColor("#A3BE8C"))
                item.setForeground(QColor("#000000"))
            elif text == "Pending":
                item.setBackground(QColor("#EBCB8B"))
                item.setForeground(QColor("#000000"))
            elif text == "Cancelled":
                item.setBackground(QColor("#BF616A"))
                item.setForeground(QColor("#FFFFFF"))
        elif status_type == "url":
            # Set background color to a greenish shade
            item.setBackground(QColor("#A3BE8C"))
            # Set text color to black
            item.setForeground(QColor("#000000"))
            # Optionally, set font weight if needed
            font = item.font()
            font.setBold(True)
            item.setFont(font) 
        
                   
                
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make item read-only
        return item

    def create_stop_button(self, row, task_id):
        """Create a styled stop button"""
        button = QPushButton("Stop")
        button.setStyleSheet("""
            QPushButton {
                background-color: #BF616A;
                color: white;
                border: none;
                padding: 3px;
                border-radius: 3px;
                min-width: 50px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #d08770;
            }
            QPushButton:disabled {
                background-color: #4C566A;
            }
        """)
        button.clicked.connect(lambda: self.handle_stop_button(task_id))
        return button

    def add_or_update_row(self, url, task_id, product_name, monitoring_status, product_status, notification_status,interval):
        """Add a new row at the top or update existing row in the table"""
        try:
            if task_id in self.task_row_map:
                # Update existing row
                row = self.task_row_map[task_id]
            else:
                # Add new row at the top (position 0)
                row = self.rowCount()
                self.insertRow(row)
                
                
                # Update row mappings
                self.row_task_map[row] = task_id
                self.task_row_map[task_id] = row
             
                # Create stop button for new row
                self.setCellWidget(row, 4, self.create_stop_button(row, task_id))

            # Update cells with styling
            url_item = QTableWidgetItem(url)
            url_item.setFlags(url_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            # self.setItem(row, 8, url_item)
            self.setItem(row, 6, self.create_styled_item(url_item, "url"))


            
            name_item = QTableWidgetItem(product_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 0, name_item)
            
            self.setItem(row, 1, self.create_styled_item(monitoring_status, "monitoring"))
            self.setItem(row, 2, self.create_styled_item(product_status, "product"))
            self.setItem(row, 3, self.create_styled_item(notification_status, "notification"))
            # Add interval with styling (using integer directly)
            interval_item = QTableWidgetItem()
            interval_item.setData(Qt.ItemDataRole.DisplayRole, interval)  # Set as integer
            interval_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            interval_item.setFlags(interval_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            # Apply the green styling
            interval_item.setBackground(QColor("#A3BE8C"))
            interval_item.setForeground(QColor("#000000"))
            font = interval_item.font()
            font.setBold(True)
            interval_item.setFont(font)
            
            self.setItem(row, 5, interval_item)
            # Disable stop button if monitoring is completed or stopped
            stop_button = self.cellWidget(row, 4)
            if stop_button and monitoring_status in ["Completed", "Stopped", "Error"]:
                stop_button.setEnabled(False)
            else:
                stop_button.setEnabled(True)

        except Exception as e:
            self.logger.error(f"Error adding/updating row: {e}")

    def _update_cell(self, row, column, value, editable=True):
        """Helper function to update a cell with optional editability"""
        item = QTableWidgetItem(value)
        if not editable:
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.setItem(row, column, item)
    def get_column_values(self, column_index):
            """Retrieve all values from the specified column and return them as a list."""
            values = []
            for row in range(self.rowCount()):
                item = self.item(row, column_index)
                if item:
                    values.append(item.text())
            return values
    def save_active_tasks(self, file_path):
        """Retrieve rows with 'Active' Monitoring Status and save selected fields as JSON to a file."""
        active_rows = []

        for row in range(self.rowCount()):
            status_item = self.item(row, 1)  # "Monitoring Status" column
            if status_item and status_item.text() == "Active":
                # Get interval value and convert to integer
                interval_value = self.item(row, 5).text() if self.item(row, 5) else "5"
                try:
                    interval_int = int(interval_value)  # Convert to integer
                except ValueError:
                    interval_int = 5  # Default value if conversion fails      
                row_data = {
                    "url": self.item(row, 6).text() if self.item(row, 6) else "",
                    "interval":interval_int,
                }
                active_rows.append(row_data)

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(active_rows, file, ensure_ascii=False, indent=4)
                print(f"Data saved successfully to {file_path}")
        except Exception as e:
            print(f"Error saving to file: {e}")


    def update_product_name(self, task_id, value):
        """Update the product name column"""
        if task_id in self.task_row_map:
            row = self.task_row_map[task_id]
            name_item = QTableWidgetItem(value)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 0, name_item)
            self.status_updated.emit(task_id, "product_name", value)

    
    
    def update_monitoring_status(self, task_id, value):
        """Update the monitoring status column"""
        if task_id in self.task_row_map:
            row = self.task_row_map[task_id]
            self.setItem(row, 1, self.create_styled_item(value, "monitoring"))
            self.status_updated.emit(task_id, "monitoring_status", value)
        
                    

    def update_product_status(self, task_id, value):
        """Update the product status column"""
        if task_id in self.task_row_map:
            row = self.task_row_map[task_id]
            self.setItem(row, 2, self.create_styled_item(value, "product"))
            self.status_updated.emit(task_id, "product_status", value)

    def update_notification_status(self, task_id, value):
        """Update the notification status column"""
        if task_id in self.task_row_map:
            row = self.task_row_map[task_id]
            self.setItem(row, 3, self.create_styled_item(value, "notification"))
            self.status_updated.emit(task_id, "notification_status", value)

    def handle_stop_button(self, task_id):
        """Handle stop button click for a single task"""
        try:
            if task_id:
                self.stop_task_signal.emit(task_id)
                # Update UI in TableWidget
                row = self.task_row_map.get(task_id)
                stop_button = self.cellWidget(row, 4)
                if stop_button:
                    stop_button.setEnabled(False)
                # Remove the task from active monitors after stopping
                self.main_window.active_monitors.pop(task_id, None)            
        except Exception as e:
            self.logger.error(f"Error handling stop button: {e}")
            # self.log_display.append(f"Error stopping task {task_id}: {e}")

    

    

    def remove_multiple_rows(self, task_ids):
        """Remove multiple rows from the table at once"""
        try:
            # Sort rows in descending order to avoid index issues when removing
            rows_to_remove = []
            for task_id in task_ids:
                if task_id in self.task_row_map:
                    rows_to_remove.append(self.task_row_map[task_id])
            
            # Sort in descending order to remove from bottom to top
            rows_to_remove.sort(reverse=True)
            
            # Remove the rows
            for row in rows_to_remove:
                self.removeRow(row)
            
            # Update mappings after all removals
            new_row_task_map = {}
            new_task_row_map = {}
            
            # Create new mappings for remaining rows
            for current_row in range(self.rowCount()):
                current_task_id = self.row_task_map.get(current_row)
                if current_task_id and current_task_id not in task_ids:
                    new_row_task_map[current_row] = current_task_id
                    new_task_row_map[current_task_id] = current_row
            
            # Update the mappings
            self.row_task_map = new_row_task_map
            self.task_row_map = new_task_row_map
                
        except Exception as e:
            self.logger.error(f"Error removing multiple rows: {e}")

    def clear_stopped(self):
        """Clear all stopped monitoring tasks"""
        try:
            # First collect all task_ids for rows with "Stopped" status
            stopped_task_ids = []
            for row in range(self.rowCount()):
                status_item = self.item(row, 1)  # Check monitoring status column
                if status_item and status_item.text() == "Stopped":
                    task_id = self.row_task_map.get(row)
                    if task_id:
                        stopped_task_ids.append(task_id)
            
            # Now remove all collected rows at once
            self.remove_multiple_rows(stopped_task_ids)
        except Exception as e:
            self.logger.error(f"Error clearing stopped tasks: {e}")       