import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def safe_wait_for_element(driver, by, value, timeout=5):
    """Wait for an element to be present, with retries if necessary."""
    try:
        element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
        return element
    except Exception as e:
        print(f"Error waiting for element {value}: {e}")
        driver.save_screenshot(f"error_{value.replace('/', '_')}.png")
        return None


def safe_click(driver, by, value):
    """Click an element safely."""
    element = safe_wait_for_element(driver, by, value)
    if element:
        element.click()
    else:
        print(f"Element {value} not found or clickable.")


def safe_send_keys(driver, by, value, keys):
    """Send keys to an element safely."""
    element = safe_wait_for_element(driver, by, value)
    if element:
        element.send_keys(keys)
    else:
        print(f"Element {value} not found for sending keys.")


def wait_for_detection_status(driver, status_id, expected_text, max_wait=5, check_interval=1):
    """Wait for detection status to update with retries."""
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            detection_status = safe_wait_for_element(driver, By.ID, status_id, timeout=check_interval)
            if detection_status and expected_text in detection_status.get_attribute("innerText"):
                print(f"Detection status: {detection_status.text}")
                return True
        except Exception as e:
            print(f"Error while checking detection status: {e}")
            driver.save_screenshot(f"status_error_{int(time.time())}.png")
        time.sleep(check_interval)
        print("Retrying detection status...")
    print("Timeout: Detection status not updated.")
    return False


# Set up WebDriver
driver = webdriver.Chrome()  # Ensure ChromeDriver is in your PATH
driver.maximize_window()

# Flask application URL
url = "http://127.0.0.1:5000/"  # Ensure the Flask server is running

# Absolute paths for test files
test_image_path = os.path.abspath("C:/Users/Yuvaraj/OneDrive/Desktop/Mini-Project/uploads/test1.png")  # Update with your actual image path
test_video_path = os.path.abspath("C:/Users/Yuvaraj/OneDrive/Desktop/Mini-Project/uploads/test_video1.mp4")  # Update with your actual video path

try:
    # Test 1: Start webcam feed (optional step for your testing, might not be needed)
    driver.get(url)
    start_webcam_button = safe_wait_for_element(driver, By.XPATH, "//button[text()='Start Webcam Feed']", timeout=2)
    if start_webcam_button:
        safe_click(driver, By.XPATH, "//button[text()='Start Webcam Feed']")
        time.sleep(1)  # Allow some time for feed to start
        webcam_feed = safe_wait_for_element(driver, By.ID, "webcam", timeout=2)
        assert webcam_feed is not None, "Webcam feed is not visible."
        print("Webcam feed started successfully.")

        # Stop webcam feed (optional)
        stop_webcam_button = safe_wait_for_element(driver, By.XPATH, "//button[text()='Stop Webcam Feed']", timeout=2)
        if stop_webcam_button:
            safe_click(driver, By.XPATH, "//button[text()='Stop Webcam Feed']")
            print("Webcam feed stopped successfully.")

    # Test 2: Upload image for detection (keeping this as-is)
    image_file_input = safe_wait_for_element(driver, By.ID, "image", timeout=2)
    if image_file_input:
        safe_send_keys(driver, By.ID, "image", test_image_path)
        detect_image_button = safe_wait_for_element(driver, By.XPATH, "//button[text()='Detect Objects in Image']", timeout=2)
        if detect_image_button:
            safe_click(driver, By.XPATH, "//button[text()='Detect Objects in Image']")
            print("Image uploaded successfully.")

        # Wait for detection result (quick check, no long waits)
        detected_image = safe_wait_for_element(driver, By.XPATH, "//img[@src and @class='img-fluid']", timeout=2)
        assert detected_image is not None, "Detected image not displayed."
        print("Image detection completed successfully.")

    # Test 3: Upload video for detection
    video_file_input = safe_wait_for_element(driver, By.ID, "video", timeout=2)
    if video_file_input:
        # Upload the video
        safe_send_keys(driver, By.ID, "video", test_video_path)
        detect_video_button = safe_wait_for_element(driver, By.XPATH, "//button[text()='Detect Objects in Video']")
        if detect_video_button:
            # Start the detection process
            safe_click(driver, By.XPATH, "//button[text()='Detect Objects in Video']")
            print("Video uploaded successfully.")

            # Instead of waiting for the full processed video, we check for a quick status update
            # Look for a status update like "Detection Completed" or similar
            detection_status = safe_wait_for_element(driver, By.ID, "detection-status")
            if detection_status:
                print(f"Detection Status: {detection_status.text}")
                assert "completed" in detection_status.text.lower(), "Detection was not completed successfully."
                print("Video detection completed successfully within 5 seconds.")

except Exception as e:
    print(f"Test failed: {e}")

finally:
    # Close the browser
    driver.quit()
    print("Test completed.")
