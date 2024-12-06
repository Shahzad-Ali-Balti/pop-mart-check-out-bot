# MainWindow.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSpinBox, QTextEdit,
    QMessageBox, QDialog,QScrollArea,QPlainTextEdit,QTextBrowser
)
import asyncio
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression
from datetime import datetime
from PyQt6.QtCore import QTimer
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import logging
import json
from PyQt6.QtGui import QTextCursor  # Add this import at the top

'''File/functions Import'''
from src.core.managers.json_file_handler import get_json_path
from src.core.managers.persistence_manager import PersistenceManager
from src.core.product_monitor import ProductMonitorWorker
from src.core.notifications import telegram_bot
from src.ui.components.table_widget import TableWidget



class MainWindow(QMainWindow):
    def __init__(self, driver_path, table_widget):
        super().__init__()
        self.driver_path = driver_path
        # self.table_widget = table_widget
        self.table_widget = TableWidget()
        self.persistence_manager = PersistenceManager()
        self.table_widget.stop_task_signal.connect(self.handle_stop_task)
        self.active_monitors = {}  # Dictionary to store active monitoring workers
        self.logger = logging.getLogger(__name__)
        self.file_path = get_json_path('Actived_tasks.json')
        self.url_validator = None
        self.bot_thread = None
        self.setup_ui()
        self.restore_active_monitors()

    def setup_ui(self):
        self.setWindowTitle("TikTok Shop Monitor")
        self.setMinimumSize(800, 600)
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2E3440;
                color: #D8DEE9;
            }
            QLabel {
                font-size: 14px;
                color: #ECEFF4;
            }
            QLineEdit, QSpinBox, QTextEdit {
                background-color: #3B4252;
                border: 1px solid #4C566A;
                color: #ECEFF4;
                padding: 4px;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #5E81AC;
                color: #ECEFF4;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:disabled {
                background-color: #4C566A;
                color: #D8DEE9;
            }
            QPushButton:hover {
                background-color: #81A1C1;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Input section
        input_section = QVBoxLayout()

        # URL input
        url_layout = QHBoxLayout()
        url_label = QLabel("Product URL:")
        url_label.setMinimumWidth(120)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter TikTok Shop product URL")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        input_section.addLayout(url_layout)

        # Interval input
        interval_layout = QHBoxLayout()
        interval_label = QLabel("Check Interval (seconds):")
        interval_label.setMinimumWidth(120)
        self.interval_input = QSpinBox()
        self.interval_input.setRange(1, 3600)
        self.interval_input.setValue(1)
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_input)
        input_section.addLayout(interval_layout)

        layout.addLayout(input_section)

        # Button section
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Monitoring")
        self.stop_button = QPushButton("Stop All")
        self.clear_stopped_button = QPushButton("Clear Stopped")
        self.telegram_button = QPushButton("Telegram Settings")
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.clear_stopped_button)
        button_layout.addWidget(self.telegram_button)
        layout.addLayout(button_layout)

        # Button Connections
        self.start_button.clicked.connect(self.start_monitoring_task)
        # self.start_button.clicked.connect(self.start_monitoring)
        self.clear_stopped_button.clicked.connect(self.clear_stopped_tasks)
        self.stop_button.clicked.connect(self.stop_all_monitoring)
        self.telegram_button.clicked.connect(self.show_telegram_menu)

        # Add table widget
        layout.addWidget(self.table_widget)

        # Create log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMaximumHeight(150)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #2E3440;
                color: #D8DEE9;
                border: 1px solid #4C566A;
                font-family: monospace;
                font-size: 12px;
                padding: 5px;
            }
            QScrollBar:vertical {
                background-color: #2E3440;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #4C566A;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #5E81AC;
            }
        """)
        self.log_display.setAcceptRichText(True)
        layout.addWidget(self.log_display)
    def show_telegram_menu(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Telegram Bot Menu")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet(self.styleSheet())

        layout = QVBoxLayout(dialog)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2E3440;
            }
            QLabel {
                color: #ECEFF4;
                font-size: 14px;
                padding: 8px;
            }
        """)

        forgot_pwd_btn = QPushButton("View Telegram Details")
        user_list_btn = QPushButton("View Telegram Users List")
        remove_user_btn = QPushButton("Remove Telegram User")
        change_password_btn = QPushButton("Change Password")
        change_bot_btn = QPushButton("Change Telegram Configuration")

        forgot_pwd_btn.clicked.connect(
            lambda: (self.show_forgot_password(), dialog.close()))
        user_list_btn.clicked.connect(
            lambda: (self.show_user_list(), dialog.close()))
        remove_user_btn.clicked.connect(
            lambda: (self.remove_bot_user(), dialog.close()))
        change_password_btn.clicked.connect(
            lambda: (self.change_bot_password(), dialog.close())
        )
        change_bot_btn.clicked.connect(
            lambda: (self.show_telegram_dialog(), dialog.close()))

        layout.addWidget(forgot_pwd_btn)
        layout.addWidget(user_list_btn)
        layout.addWidget(remove_user_btn)
        layout.addSpacing(20)  # Add some margin from the top
        layout.addWidget(change_password_btn)
        layout.addWidget(change_bot_btn)

        dialog.exec()

    def change_bot_password(self):
        """
        Shows a themed dialog for changing password with confirmation and updates the data_id.json file.
        Uses the custom message box system for consistent styling across the application.
        """
        # Create the password input dialog
        password_dialog = QDialog(self)
        password_dialog.setWindowTitle("Change Password")
        password_dialog.setModal(True)
        
        # Apply the Nord theme styling to the password dialog
        password_dialog.setStyleSheet("""
            QDialog {
                background-color: #2E3440;
                border: 1px solid #4C566A;
                border-radius: 6px;
            }
            QLabel {
                color: #ECEFF4;
                font-size: 14px;
                padding: 12px;
            }
            QLineEdit {
                background-color: #3B4252;
                color: #ECEFF4;
                border: 1px solid #4C566A;
                padding: 8px;
                border-radius: 4px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #5E81AC;
            }
            QPushButton {
                background-color: #4C566A;
                color: #ECEFF4;
                border: 1px solid #4C566A;
                padding: 8px 16px;
                margin: 6px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5E81AC;
                border-color: #5E81AC;
            }
        """)
        
        # Create the layout and components
        layout = QVBoxLayout()
        password_label = QLabel("New Password:")
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_input.setMinimumWidth(250)
        
        save_button = QPushButton("Save")
        save_button.setFixedWidth(100)
        
        # Add widgets to layout with proper spacing
        layout.addWidget(password_label)
        layout.addWidget(password_input)
        layout.addSpacing(10)
        layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(10)
        
        password_dialog.setLayout(layout)
        
        def on_save_clicked():
            """
            Handles the save button click by showing confirmation dialog
            and updating the password if confirmed.
            """
            new_password = password_input.text().strip()
            
            # Validate password is not empty
            if not new_password:
                response = self.show_custom_message_box(
                    "Invalid Input",
                    "Password cannot be empty.",
                    ["OK"]
                )
                return
            
            # Show confirmation dialog using custom message box
            response = self.show_custom_message_box(
                "Confirm Password Change",
                "Are you sure you want to change the password?",
                ["Yes", "No"]
            )
            
            # If user confirms, update the password
            if response == "Yes":
                try:
                    # Read the current data
                    with open(get_json_path('telegram_config.json'), 'r') as file:
                        data = json.load(file)
                    
                    # Update the password
                    data['password'] = new_password
                    
                    # Write the updated data back to file
                    with open(get_json_path('telegram_config.json'), 'w') as file:
                        json.dump(data, file, indent=4)
                    
                    # Show success message using custom message box
                    self.show_custom_message_box(
                        "Success",
                        "Password has been successfully updated.",
                        ["OK"]
                    )
                    password_dialog.accept()
                    
                except Exception as e:
                    # Show error message using custom message box
                    self.show_custom_message_box(
                        "Error",
                        f"Failed to update password: {str(e)}",
                        ["OK"]
                    )
        
        # Connect the save button click to our handler
        save_button.clicked.connect(on_save_clicked)
        
        # Show the password dialog
        password_dialog.exec()        
    def remove_bot_user(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Remove Telegram User")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2E3440;
            }
            QLabel {
                color: #ECEFF4;
                font-size: 14px;
                padding: 8px;
            }
            QMessageBox {
                background-color: #0000;
            }
            QPushButton {
                background-color: #4C566A;
                color: #0000;
                border: none;
                padding: 8px 16px;
                margin: 4px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5E81AC;
            }
        """)

        layout = QVBoxLayout(dialog)
        
        chat_id_label = QLabel("Enter Chat ID:")
        chat_id_input = QLineEdit()
        
        button_layout = QHBoxLayout()
        remove_btn = QPushButton("Remove User")
        cancel_btn = QPushButton("Cancel")
        
        remove_btn.clicked.connect(lambda: self.confirm_remove_user(chat_id_input.text(), dialog))
        cancel_btn.clicked.connect(dialog.close)
        
        button_layout.addWidget(remove_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addWidget(chat_id_label)
        layout.addWidget(chat_id_input)
        layout.addLayout(button_layout)
        
        dialog.exec()


    def confirm_remove_user(self, chat_id, parent_dialog):
        if not chat_id:
            show_custom_message_box(self, "Error", "Please enter a Chat ID", ["OK"])
            return

        result = show_custom_message_box(self, "Confirm", f"Remove user with Chat ID: {chat_id}?", ["Yes", "No"])
        
        if result == "Yes":
            try:
                with open(get_json_path('chat_ids.json'), 'r') as file:
                    users = json.load(file)
                    
                users = [user for user in users if str(user['chat_id']) != str(chat_id)]
                
                with open(get_json_path('chat_ids.json'), 'w') as file:
                    json.dump(users, file, indent=4)
                
                show_custom_message_box(self, "Success", "User removed successfully", ["OK"])
                parent_dialog.close()
                
            except Exception as e:
                    show_custom_message_box(self, "Error", f"Failed to remove user: {str(e)}", ["OK"])
    def show_telegram_dialog(self): 
        dialog = QDialog(self) 
        dialog.setWindowTitle("Telegram Bot Configuration") 
        dialog.setMinimumWidth(400) 
        
        layout = QVBoxLayout(dialog) 
        dialog.setStyleSheet(""" 
            QDialog { 
                background-color: #2E3440; 
            } 
            QLabel { 
                color: #ECEFF4; 
                font-size: 14px; 
                padding: 8px; 
            } 
            QLineEdit { 
                background-color: #3B4252; 
                color: #ECEFF4; 
                padding: 5px; 
                border: 1px solid #4C566A; 
                border-radius: 3px; 
            } 
            QPushButton { 
                background-color: #3B4252;
                color: #ECEFF4;
                padding: 5px;
                border: 1px solid #4C566A;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #434C5E;
            }
        """) 

        bot_name_label = QLabel("Bot Name:") 
        bot_name_input = QLineEdit() 
        bot_name_input.setPlaceholderText("Enter Bot Name") 

        token_label = QLabel("Bot Token:") 
        token_input = QLineEdit() 
        token_input.setPlaceholderText("Enter Bot Token") 

        password_label = QLabel("Password:") 
        
        # Create a horizontal layout for password input and visibility toggle
        password_layout = QHBoxLayout()
        
        password_input = QLineEdit() 
        password_input.setPlaceholderText("Enter Password") 
        password_input.setEchoMode(QLineEdit.EchoMode.Password) 
        
        # Create toggle password visibility button
        toggle_password = QPushButton()
        toggle_password.setFixedWidth(30)
        toggle_password.setFixedHeight(30)
        toggle_password.setText("👁️")
        
        def toggle_password_visibility():
            if password_input.echoMode() == QLineEdit.EchoMode.Password:
                password_input.setEchoMode(QLineEdit.EchoMode.Normal)
                toggle_password.setText("🔒")
            else:
                password_input.setEchoMode(QLineEdit.EchoMode.Password)
                toggle_password.setText("👁️")
        
        toggle_password.clicked.connect(toggle_password_visibility)
        
        # Add password input and toggle button to horizontal layout
        password_layout.addWidget(password_input)
        password_layout.addWidget(toggle_password)

        save_button = QPushButton("Save") 

        def save_and_close(): 
            bot_name = bot_name_input.text() 
            token = token_input.text() 
            password = password_input.text() 
            
            if not all([bot_name, token, password]): 
                self.show_custom_message_box("Error", "Please fill all fields", ["OK"]) 
                return 
                    
            result = self.show_custom_message_box( 
                "Confirm",  
                "Are you sure you want to save these bot settings?\nThis will clear all existing users.",  
                ["Yes", "No"] 
            ) 
            
            if result == "Yes": 
                self.save_telegram_config(bot_name, token, password) 
                open(get_json_path('chat_ids.json'), 'w').close() 
                self.show_custom_message_box("Success", "New Telegram bot configurated successfully.\n\n Please add new user and restart app", ["OK"]) 
                dialog.close() 

        save_button.clicked.connect(save_and_close) 
        
        # Add widgets to main layout
        layout.addWidget(bot_name_label) 
        layout.addWidget(bot_name_input) 
        layout.addWidget(token_label) 
        layout.addWidget(token_input) 
        layout.addWidget(password_label) 
        layout.addLayout(password_layout)  # Add the password layout instead of individual widgets
        layout.addWidget(save_button) 

        dialog.exec()
    def show_custom_message_box(self, title, message, buttons):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2E3440;
                border: 1px solid #4C566A;
                border-radius: 6px;
            }
            QLabel {
                color: #ECEFF4;
                font-size: 14px;
                padding: 12px;
            }
            QPushButton {
                background-color: #4C566A;
                color: #ECEFF4;
                border: 1px solid #4C566A;
                padding: 8px 16px;
                margin: 6px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5E81AC;
                border-color: #5E81AC;
            }
        """)

        layout = QVBoxLayout(dialog)
        label = QLabel(message, dialog)
        layout.addWidget(label)

        clicked_button = None

        def handle_button_click(button_text):
            nonlocal clicked_button
            clicked_button = button_text
            dialog.accept()

        for button_text in buttons:
            button = QPushButton(button_text, dialog)
            button.clicked.connect(lambda _, b=button_text: handle_button_click(b))
            layout.addWidget(button)

        dialog.exec()
        return clicked_button

    def show_user_list(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Telegram Users")
        dialog.setMinimumWidth(400)

        dialog.setStyleSheet("""
            QDialog {
                background-color: #2E3440;
            }
            QLabel {
                color: #ECEFF4;
                font-size: 13px;
                padding: 5px;
            }
            QScrollArea {
                border: none;
                background-color: #2E3440;
            }
            QWidget#scrollContent {
                background-color: #2E3440;
            }
            QTextBrowser {
                background-color: #3B4252;
                color: #ECEFF4;
                border: none;
                selection-background-color: #88C0D0;
            }
        """)

        layout = QVBoxLayout(dialog)
        
        scroll = QScrollArea()
        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        scroll_layout = QVBoxLayout(scroll_content)

        try:
            with open(get_json_path('chat_ids.json'), 'r') as file:
                users = json.load(file)
                
            for user in users:
                user_info_text = (
                    f"Name: {user.get('first_name', '')} {user.get('last_name', '')}\n"
                    f"Username: {user.get('username', 'N/A')}\n"
                    f"Chat ID: {user.get('chat_id', 'N/A')}"
                )
                user_info = QTextBrowser()
                user_info.setText(user_info_text)
                user_info.setReadOnly(True)
                scroll_layout.addWidget(user_info)
                
        except FileNotFoundError:
            error_label = QLabel("No users found")
            scroll_layout.addWidget(error_label)
        except json.JSONDecodeError:
            error_label = QLabel("No users found")
            scroll_layout.addWidget(error_label)

        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        scroll.setWidgetResizable(True)

        layout.addWidget(scroll)
        dialog.exec()
    def show_forgot_password(self):
        try:
            with open(get_json_path('telegram_config.json'), 'r') as f:
                config = json.load(f)
                bot_name = config.get('bot_name', '')
                bot_password = config.get('password', '')
                bot_token = config.get('bot_token', '')
        except FileNotFoundError:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Telegram Bot Details")
        dialog.setMinimumWidth(300)
        layout = QVBoxLayout(dialog)

        dialog.setStyleSheet("""
            QDialog {
                background-color: #2E3440;
            }
            QTextEdit {
                color: #ECEFF4;
                font-size: 14px;
                padding: 8px;
                background-color: #3B4252;
                border: none;
            }
        """)

        bot_info = (f"Name: {bot_name}\n\n"
                    f"Password: {bot_password}\n\n"
                    f"Token:\n\{bot_token}")

        text_edit = QTextEdit()
        text_edit.setPlainText(bot_info)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)

        dialog.exec()

    def save_telegram_config(self, name, token, password, filename=get_json_path('telegram_config.json')):
        config = {"bot_name": name, "bot_token": token, "password": password}
        with open(filename, "w") as f:
            json.dump(config, f)
    def show_temporary_log(self, message, duration=5000, message_type=None):
        """Show a styled log message that disappears after specified duration"""
        try:
            # Get icon based on message type
            if message_type == "error":
                icon = "⚠"
            elif message_type == "success":
                icon = "✓"
            else:  # info
                icon = "ℹ"

            # Create message with icon
            full_message = f"{icon} {message}\n"

            # Insert at the beginning of text
            cursor = self.log_display.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.insertText(full_message)

            # Schedule message removal
            QTimer.singleShot(
                duration, lambda: self.remove_single_message(full_message))

        except Exception as e:
            print(f"Error showing temporary log: {e}")

    def remove_single_message(self, message_to_remove):
        """Remove a specific message from the log display"""
        try:
            current_text = self.log_display.toPlainText()
            new_text = current_text.replace(message_to_remove, '')
            self.log_display.setPlainText(new_text)
        except Exception as e:
            print(f"Error removing message: {e}")

    def restore_active_monitors(self):
        """Restore previously active monitoring tasks"""
        try:
            active_tasks = self.persistence_manager.load_active_tasks()
            num_tasks = len(active_tasks)

            # Restore each task
            for task in active_tasks:
                self.start_monitoring_task(task)

            # Log message with number of tasks restored
            if num_tasks > 0:
                self.show_temporary_log(
                    f"Successfully restored {num_tasks} previous monitoring task{'s' if num_tasks > 1 else ''}.", message_type="success"
                )
            else:
                self.show_temporary_log(
                    "No previous monitoring tasks to restore.", message_type="info")

        except Exception as e:
            self.logger.error(f"Error restoring monitors: {e}")
            # self.show_temporary_log(
            #     "Error restoring previous monitoring tasks"
            # )

    def validate_and_start_monitoring(self):
        """Validate inputs and call start_monitoring_task with validated values"""
        try:
            # Get input values
            url = self.url_input.text().strip()
            interval = self.interval_input.value()

            # Validate URL
            if not url:
                self.show_temporary_log(
                    "URL cannot be empty", message_type="error")
                return False

            # Updated regex validation for all URL types
             # Updated regex validation with specific product ID length
            import re
            tiktok_pattern = (
                r'^https?:\/\/'  # Protocol (http:// or https://)
                # Optional subdomains (shop. or www. or vt.)
                r'(?:(?:shop|www|vt)\.)?'
                r'tiktok\.com\/'  # Base domain
                r'(?:'  # Start non-capturing group for paths
                r'view\/product\/\d+|'  # Product path with exactly 19 digits
                r'[A-Za-z0-9]+\/?|'  # Short URL format
                r'ZS[A-Za-z0-9]+\/?'  # vt.tiktok.com format
                r')'  # End path group
                r'(?:\?[^\/\s]*)?'  # Optional query parameters
                r'$'  # End of string
            )

            if not re.match(tiktok_pattern, url):
                self.show_temporary_log(
                    "Invalid TikTok Shop URL format", message_type="error")
                return False

            # Validate interval
            if interval <= 0:
                self.show_temporary_log(
                    "Interval must be greater than 0", message_type="error")
                return False

            # All validations passed, start monitoring with validated values
            task = None  # Initialize task as None
            # Call with task=None to use validated values
            monitor_id = self.start_monitoring_task(task)

            if monitor_id:
                self.show_temporary_log(f"Started monitoring task: {
                                        url}", message_type="success")
                return True
            else:
                self.show_temporary_log(
                    "Failed to start monitoring task", message_type="error")
                return False

        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            self.show_temporary_log(f"Error during validation: {
                                    str(e)}", message_type="error")
            return False

    def setup_url_validator(self):
        """Set up the URL validator with regex pattern"""
        tiktok_pattern = (
            r'^https?:\/\/'  # Protocol
            r'(?:shop\.|www\.|vt\.)?'  # Optional subdomains
            r'tiktok\.com\/'  # Domain
            r'(?:'  # Start non-capturing group
            r'view\/product\/\d+'  # Product view pattern
            r'|'  # OR
            r'[A-Za-z0-9]+'  # Short URL pattern
            r')'  # End non-capturing group
            r'(?:\?[^\/\s]*)?$'  # Optional query parameters
        )

        # Create QRegularExpression validator
        regex = QRegularExpression(tiktok_pattern)
        self.url_validator = QRegularExpressionValidator(regex)
        self.url_input.setValidator(self.url_validator)

    def start_monitoring_task(self, task=None):
        """Start a new monitoring task"""
        try:
            # if task is None:
            #     # New monitoring task
            #     url = self.url_input.text().strip()
            #     interval = self.interval_input.value()
            # else:
            #     # Restored task
            #     url = task.url
            #     interval = task.interval
            # New monitoring task
            url = self.url_input.text().strip()
            interval = self.interval_input.value()
            monitor = ProductMonitorWorker(
                driver_path=self.driver_path,
                table_widget=self.table_widget,
                persistence_manager=self.persistence_manager,
                url=url,
                check_interval=interval
            )

            monitor_id = monitor.task_id
            self.active_monitors[monitor_id] = monitor
            monitor.start()

            # Add new row to the table
            self.table_widget.add_or_update_row(
                url, monitor_id, "Loading", "Active", "Searching", "Pending", interval
            )

            # self.log_display.append(f"Started monitoring: {url}")
            self.stop_button.setEnabled(True)
            return monitor_id

        except Exception as e:
            self.logger.error(f"Error starting monitor: {e}")
            # self.log_display.append(f"Error starting monitoring: {str(e)}")
            return None

    def handle_stop_task(self, task_id):
        """Handle the stop task action when a stop button is clicked"""
        if task_id in self.active_monitors:
            # Perform UI updates and disable the button (if required)
            row = self.table_widget.task_row_map.get(task_id)
            if row is not None:
                self.table_widget.setItem(
                    row, 1, self.table_widget.create_styled_item("Stopped", "monitoring"))
                product_status_item = self.table_widget.item(
                    row, 2)  # Get the product status column
                product_status = product_status_item.text() if product_status_item else None
                if product_status in ["Searching"]:
                    self.table_widget.setItem(
                        row, 2, self.table_widget.create_styled_item("Unknown", "product"))
                self.table_widget.setItem(
                    row, 3, self.table_widget.create_styled_item("Cancelled", "notification"))

                # Disable the stop button for this task
                stop_button = self.table_widget.cellWidget(row, 4)
                if stop_button:
                    stop_button.setEnabled(False)

            task = self.active_monitors[task_id]
            # Call stop method of the corresponding task (assuming ProductMonitorWorker has a stop method)
            task.stop(task_id)
            # Remove the task from active monitors after stopping
            self.active_monitors.pop(task_id, None)
            self.logger.info(f"Task {task_id} stopped.")
        else:
            self.logger.error(f"Task {task_id} not found in active monitors.")

    def start_monitoring(self):
        """Start button handler"""
        monitor_id = self.start_monitoring_task()
        if monitor_id:
            # Allow multiple monitoring tasks
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(True)

    def stop_all_monitoring(self):
        """Stop all monitoring tasks and update the GUI table for all task IDs."""
        try:
            # Initialize a counter for stopped tasks
            stopped_task_count = 0

            # Update the UI for all tasks first
            for task_id in list(self.active_monitors.keys()):
                row = self.table_widget.task_row_map.get(task_id)

                if row is not None:
                    # Update the status columns
                    self.table_widget.setItem(
                        row, 1, self.table_widget.create_styled_item("Stopped", "monitoring"))
                    self.table_widget.setItem(
                        row, 2, self.table_widget.create_styled_item("Unknown", "product"))
                    self.table_widget.setItem(
                        row, 3, self.table_widget.create_styled_item("Cancelled", "notification"))

                    # Disable the stop button for the task
                    stop_button = self.table_widget.cellWidget(row, 4)
                    if stop_button:
                        stop_button.setEnabled(False)

            # Stop all monitoring tasks
            for task_id, monitor in list(self.active_monitors.items()):
                try:
                    # Stop the monitor
                    monitor.stop()
                    monitor.wait()

                    # Remove from active monitors
                    self.active_monitors.pop(task_id, None)
                    stopped_task_count += 1

                    # Log the stop action
                    self.logger.info(f"Task {task_id} stopped successfully.")
                except Exception as monitor_stop_error:
                    self.logger.error(f"Error stopping monitor for task {task_id}: {monitor_stop_error}")

            # Show a log message with the count of stopped tasks
            self.show_temporary_log(
                f"Stopped all {stopped_task_count} monitoring tasks.", message_type="success")

            # Update main control button states
            self.stop_button.setEnabled(False)
            self.start_button.setEnabled(True)

            # Log overall completion
            self.show_temporary_log(
                "All monitoring tasks have been stopped.", message_type="info")

        except Exception as e:
            self.logger.error(f"Error in stop_all_monitoring: {e}")
            self.show_temporary_log(
                "An error occurred while stopping all tasks.", message_type="error")


    def clear_stopped_tasks(self):
        """Clear stopped monitoring tasks from table"""
        self.table_widget.clear_stopped()
        # self.show_temporary_log("Cleared All stopped tasks")

    def closeEvent(self, event):
        """Handle application closure"""
        try:
            # Create a message box for confirmation
            message_box = QMessageBox(self)
            message_box.setWindowTitle('Confirm Exit')
            message_box.setText(
                'Are you sure you want to exit? Active monitoring tasks will be stopped.')

            # Apply styling to the message box
            message_box.setStyleSheet("""
                QMessageBox {
                                      
                    background-color: #000000;
                    color: #ECEFF4;  /* Text color white */
                }                    
                QMessageBox QPushButton {
                    background-color: #5E81AC;
                    color: #ECEFF4;
                    border: none;
                    padding: 8px 12px;
                    border-radius: 4px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #81A1C1;
                }
            """)

            # Add the Yes and No buttons with their respective actions
            message_box.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            # Get the user's response
            reply = message_box.exec()

            if reply == QMessageBox.StandardButton.Yes:
                Monitoring_status = self.table_widget.save_active_tasks(
                    self.file_path)
                print('Monitoring_status are', Monitoring_status)
                # Stop bot if running
                if self.bot_thread and self.bot_thread.is_alive():
                    # Add cleanup function in telegram_bot.py
                    asyncio.run(telegram_bot.cleanup())
                    self.bot_thread.join(timeout=1)
                self.stop_all_monitoring()

                event.accept()
            else:
                event.ignore()

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            event.accept()
@staticmethod
def show_custom_message_box(parent, title, message, buttons):
    dialog = QDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setStyleSheet("""
        QDialog {
            background-color: #2E3440;
            border: 1px solid #4C566A;
            border-radius: 6px;
        }
        QLabel {
            color: #ECEFF4;
            font-size: 14px;
            font-family: "Segoe UI", Arial, sans-serif;
            padding: 12px;
        }
        QPushButton {
            background-color: #4C566A;
            color: #ECEFF4;
            border: 1px solid #4C566A;
            padding: 8px 16px;
            margin: 6px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: bold;
            font-family: "Segoe UI", Arial, sans-serif;
        }
        QPushButton:hover {
            background-color: #5E81AC;
            border-color: #5E81AC;
        }
        QPushButton:pressed {
            background-color: #3B4252;
            border-color: #3B4252;
        }
    """)

    layout = QVBoxLayout(dialog)
    label = QLabel(message, dialog)
    layout.addWidget(label)

    clicked_button = None

    def handle_button_click(button_text):
        nonlocal clicked_button
        clicked_button = button_text
        dialog.accept()

    for button_text in buttons:
        button = QPushButton(button_text, dialog)
        button.clicked.connect(lambda _, b=button_text: handle_button_click(b))
        layout.addWidget(button)

    dialog.exec()
    return clicked_button