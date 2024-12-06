from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import logging
import os

class WebMonitor:
    def __init__(self, driver_path):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        self.driver_path = driver_path
        self.driver = None
        self.url = None
        self.initialize_driver()

    def initialize_driver(self):
        """Initialize a new WebDriver instance"""
        try:
            # Import subprocess at the top of your file or here
            import subprocess
            
            chromedriver_path = os.path.join(self.driver_path, 'chromedriver.exe')
            chrome_service = Service(chromedriver_path)
            
            # Add this line to hide the console window
            chrome_service.creation_flags = subprocess.CREATE_NO_WINDOW
            
            options = webdriver.ChromeOptions()
            options.add_argument("--disable-extensions")
            # options.add_argument("--headless")
            options.add_argument("--enable-unsafe-swiftshader")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            # Additional options for better stability
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-infobars")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            # Disable the password save prompt by setting the preferences
            options.add_argument("--disable-save-password-bubble")
            options.add_experimental_option("prefs", {
                "profile.password_manager_enabled": False
            })
            
            self.driver = webdriver.Chrome(service=chrome_service, options=options)
            self.driver.set_window_size(1920, 1080)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("WebDriver initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize driver: {e}")
            return False
    def click_accept_terms(self):
        """Click the 'Accept Terms and Conditions' button if present."""
        try:
            # Define the XPath for the accept button
            accept_button_xpath = "//*[@id='__next']/div/div/div[3]/div/div[2]"
            
            # Wait for the button to be present and clickable
            accept_button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, accept_button_xpath))
            )
            
            # Click the button
            accept_button.click()
            self.logger.info("Clicked 'Accept Terms and Conditions' button.")
            
            # Wait for the page to load after clicking
            self.wait_for_page_load()
        except Exception as e:
            self.logger.warning(f"'Accept Terms and Conditions' button not found or clickable: {e}")
    def check_sign_in_status(self):
        try:
            # Define XPaths for the required elements
            my_order_xpath = '//*[@class="index_title___gOaU" and text()="My Orders"]'
            new_arrival_xpath = '//*[@class="index_titleText__Hxz8v" and text()="New Arrivals"]'
            featured_xpath = '//*[@class="index_title__JSAKN" and text()="FEATURED"]'
            recommended_xpath = '//*[@class="index_title__JSAKN" and text()="RECOMMENDED FOR YOU"]'

            # Wait and check for "My Orders"
            my_order_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, my_order_xpath))
            )
            if my_order_element:
                print("Sign-in successful: Found 'My Orders'.")
                return True

        except Exception:
            pass

        # If "My Orders" is not found, check for other elements
        try:
            # Wait and check for New Arrivals, Featured, and Recommended For You elements
            new_arrival_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, new_arrival_xpath))
            )
            if new_arrival_element:
                print("Sign-in successful: Found 'New Arrivals'.")
                return True

            featured_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, featured_xpath))
            )
            if featured_element:
                print("Sign-in successful: Found 'Featured'.")
                return True

            recommended_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, recommended_xpath))
            )
            if recommended_element:
                print("Sign-in successful: Found 'Recommended For You'.")
                return True

        except Exception:
            pass

        # If none of the success indicators are found
        print("Sign-in failed: Indicators not found.")
        return False
    def login_and_return(self, url, email, password):
        try:
            # Click the "Sign/Register" button
            sign_button_xpath = "//*[@id='__next']/div/div/div[1]/div[1]/div[2]/div[2]/a[1]/span/div"  # Replace with your xpath
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, sign_button_xpath))
            ).click()

            # Enter email in the login form
            email_input_xpath = "//*[@id='email']"  # Replace with your xpath
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, email_input_xpath))
            ).send_keys(email)

            # Click the "Continue" button
            continue_button_xpath = "//*[@id='__next']/div/div/div[2]/div/div/form/div[3]/div/div/div/div/button"  # Replace with your xpath
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, continue_button_xpath))
            ).click()

            # Enter password
            password_input_xpath = "//*[@id='password']"  # Replace with your xpath
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, password_input_xpath))
            ).send_keys(password)

            # Submit the login form
            password_submit_button_xpath = "//*[@id='__next']/div/div/div[2]/div/div/form/div[3]/div/div/div/div/button"  # Replace with your xpath
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, password_submit_button_xpath))
            ).click()

            # Wait for the page to render after login
            print("Waiting for 10 seconds to allow page to load...")
            self.driver.implicitly_wait(10)

            # Check sign-in status
            if self.check_sign_in_status():
                print("Sign-in successful. Navigating to the product page...")
            else:
                print("Sign-in failed. Please check credentials or page behavior.")
                return  # Exit the function if sign-in fails

            # Navigate to the product page
            # Navigate directly to the product page using the URL
            print(f"Navigating to the product page: {url}")
            self.driver.get(url)

            # Confirm navigation back to the product page
            WebDriverWait(self.driver, 10).until(
                EC.url_contains(url)
            )
            print("Login and navigation to the product page successful!")

            # Confirm navigation back to the product page
            WebDriverWait(self.driver, 10).until(
                EC.url_contains(url)
            )
            print("Login and navigation successful!")

        except Exception as e:
            print(f"An error occurred during login: {e}")


    def open_url(self, url):
        """Opens the specified URL in the browser."""
        try:
            self.url = url
            self.email='solanaape01@gmail.com'
            self.password = 'Qwerty@12345!'
            self.logger.info(f"Opening URL: {url}")
            self.driver.get(url)
            self.click_accept_terms()
            self.wait_for_page_load()
            self.login_and_return(url,self.email, self.password)
        except Exception as e:
            self.logger.error(f"Error opening URL: {e}")
            raise

    def wait_for_page_load(self, timeout=10):
        """Waits for the page to load completely."""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.info("Page fully loaded")
        except Exception as e:
            self.logger.error(f"Page load timeout: {e}")
            raise

    def find_element_safe(self, by, value, timeout=10):
        """Safely finds an element by its locator."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            self.logger.error(f"Element not found for {value}: {e}")
            return None
        


    def locate_quantity_div(self):
        try:
            # Parent container for quantity div
            parent_container_xpath = "//*[@id='__next']/div/div/div[2]/div[1]/div[2]/div[2]/div"

            # Locate all children divs
            child_divs = self.driver.find_elements(By.XPATH, parent_container_xpath + "/div")

            for index, div in enumerate(child_divs, start=1):
                if "index_quantityContainer__OhYal" in div.get_attribute("class"):
                    # Check if input field is enabled or disabled
                    input_element = div.find_element(By.TAG_NAME, "input")
                    if input_element.is_enabled():
                        self.logger.info(f"Quantity div found at child {index}: Input is enabled.")
                    else:
                        self.logger.info(f"Quantity div found at child {index}: Input is disabled.")
                    return div

            self.logger.warning("Quantity div not found.")
            return None
        except Exception as e:
            self.logger.error(f"Error locating quantity div: {e}")
            return None

    def fetch_dynamic_input_value(self):
        """Fetch the current value of the dynamically loaded input field."""
        input_xpath = "//input[contains(@class, 'ant-input') and @type='number']"
        try:
            self.logger.info("Waiting for the dynamic input field to load...")
            input_element = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, input_xpath))
            )
            if input_element.is_displayed() and input_element.is_enabled():
                input_value = input_element.get_attribute("value")
                self.logger.info(f"Dynamic input field value: {input_value}")
                return input_value
            else:
                self.logger.warning("Input field is not interactable.")
                return None
        except Exception as e:
            self.logger.error(f"Error while fetching dynamic input value: {e}")
            return None

    def verify_add_to_cart(self):
        """Verify the 'Add to cart successfully' alert."""
        try:
            # Define the XPath for the success alert
            alert_xpath = "/html/body/div[2]/div/div/div/div/div/div/div[1]"

            # Wait for the alert to be present
            success_alert = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, alert_xpath))
            )

            # Check if the text matches the expected alert
            if success_alert and success_alert.text.strip() == "Add to cart successfully":
                self.logger.info("Add to cart successfully.")
            else:
                self.logger.warning(
                    f"Alert found, but text does not match 'Add to cart successfully'. Found: {success_alert.text.strip()}"
                )

            # Wait for an additional 3 seconds for any UI updates
            self.driver.implicitly_wait(3)

        except Exception as e:
            self.logger.error(f"Error verifying 'Add to cart' alert: {e}")
    def update_cart_input_value(self, value="1"):
        """Update the cart input value."""
        try:
            cart_input_xpath = "//*[@id='__next']/div/div/div[2]/div[1]/div[2]/div[2]/div/div[3]/div[2]/input"
            cart_input_element = self.find_element_safe(By.XPATH, cart_input_xpath)
            if cart_input_element:
                cart_input_element.clear()
                cart_input_element.send_keys(value)
                self.logger.info(f"Cart input value updated to {value}")
                return True
            else:
                self.logger.warning("Cart input element not found")
                return False
        except Exception as e:
            self.logger.error(f"Error updating cart input value: {e}")
            return False

    def click_add_to_cart_button(self):
        """Click the 'Add to Cart' button."""
        try:
            add_to_cart_xpath = "//*[@id='__next']/div/div/div[2]/div[1]/div[2]/div[2]/div/div[5]/div[1]"
            add_to_cart_button = self.find_element_safe(By.XPATH, add_to_cart_xpath)
            if add_to_cart_button:
                add_to_cart_button.click()
                self.logger.info("Add to Cart button clicked")
                self.click_cart_icon()
                self.logger.info("Cart Icon Clicked")
                return True
            else:
                self.logger.warning("Add to Cart button not found")
                return False
        except Exception as e:
            self.logger.error(f"Error clicking Add to Cart button: {e}")
            return False
    def click_cart_icon(self):
        try:
            # Define the XPath for the cart icon
            cart_icon_xpath = '//*[@class="index_cartItem__xumFD"]'

            # Wait for the cart icon to be clickable and click it
            cart_icon_element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, cart_icon_xpath))
            )
            cart_icon_element.click()
            print("Clicked on the cart icon successfully.")

        except Exception as e:
            print(f"An error occurred while trying to click the cart icon: {e}")

    def fetch_product_info(self):
        """Fetches product information from the page."""
        try:
            product_info = {}

            # Product Name
            name_element = self.find_element_safe(By.XPATH, "//*[@id='__next']/div/div/div[2]/div[1]/div[2]/div[2]/div/div[1]/div[1]/div[1]/h1")
            product_info['name'] = name_element.text if name_element else "Not Found"

            # Product Price
            price_element = self.find_element_safe(By.XPATH, "//*[@id='__next']/div/div/div[2]/div[1]/div[2]/div[2]/div/div[1]/div[2]/div")
            product_info['price'] = price_element.text if price_element else "Not Found"
            
            # Size Div
            size_div_element = self.find_element_safe(By.XPATH, "//*[@id='__next']/div/div/div[2]/div[1]/div[2]/div[2]/div/div[2]/div[2]")
            product_info['size_options'] = size_div_element.text if size_div_element else "Not Found"
            self.locate_quantity_div()
            # Add to Cart Input
            cart_input_element = self.fetch_dynamic_input_value()
            product_info['cart_input_value'] = cart_input_element if cart_input_element else "cart_input Not Found"

            # Add to Cart Button
            cart_button_element = self.find_element_safe(By.XPATH, "//*[@id='__next']/div/div/div[2]/div[1]/div[2]/div[2]/div/div[5]/div[1]")
            product_info['cart_button'] = cart_button_element.text if cart_button_element else "Not Found"

            # Buy Now Button
            buy_button_element = self.find_element_safe(By.XPATH, "//*[@id='__next']/div/div/div[2]/div[1]/div[2]/div[2]/div/div[5]/div[2]")
            product_info['buy_button'] = buy_button_element.text if buy_button_element else "Not Found"

            

            # Log Product Information
            self.logger.info("Fetched Product Info:")
            for key, value in product_info.items():
                self.logger.info(f"{key.replace('_', ' ').capitalize()}: {value}")

            return product_info

        except Exception as e:
            self.logger.error(f"Error fetching product information: {e}")
            raise

    def cleanup(self):
        """Closes the browser and cleans up resources."""
        try:
            if self.driver:
                self.driver.quit()
                self.logger.info("Browser closed successfully")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            raise
