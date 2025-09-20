import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    """Set up the Selenium WebDriver."""
    driver = webdriver.Chrome()
    driver.maximize_window()
    return driver

def safe_wait_for_element(driver, by, value, timeout=10):
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
        try:
            element.click()
        except Exception as e:
            print(f"Error clicking element {value}: {e}")

def safe_send_keys(driver, by, value, keys):
    """Send keys to an element safely."""
    element = safe_wait_for_element(driver, by, value)
    if element:
        try:
            element.send_keys(keys)
        except Exception as e:
            print(f"Error sending keys to element {value}: {e}")

# Web Cam Detection
def test_webcam_feed(driver):
    """Test starting and stopping the webcam feed."""
    print("Testing Webcam Feed...")
    safe_click(driver, By.XPATH, "//button[text()='Start Webcam Feed']")
    time.sleep(2)
    webcam_feed = safe_wait_for_element(driver, By.ID, "webcam")
    assert webcam_feed is not None, "Webcam feed is not visible."
    print("Webcam feed started successfully.")

    safe_click(driver, By.XPATH, "//button[text()='Stop Webcam Feed']")
    print("Webcam feed stopped successfully.")

# Image Detection
def test_image_detection(driver, test_image_path):
    """Test uploading and detecting objects in an image."""
    print("Testing Image Detection...")
    safe_send_keys(driver, By.ID, "image", test_image_path)
    safe_click(driver, By.XPATH, "//button[text()='Detect Objects in Image']")
    detected_image = safe_wait_for_element(driver, By.XPATH, "//img[@src and @class='img-fluid']")
    assert detected_image is not None, "Detected image not displayed."
    print("Image detection completed successfully.")

# Video Detection
def test_video_detection(driver, test_video_path):
    """Test uploading and detecting objects in a video."""
    print("Testing Video Detection...")

    safe_send_keys(driver, By.ID, "video", test_video_path)
    safe_click(driver, By.XPATH, "//button[text()='Detect Objects in Video']")
    print("Video uploaded successfully. Waiting for status update...")

    max_wait_time = 30
    detection_status = safe_wait_for_element(driver, By.ID, "detection-status", timeout=max_wait_time)

    if detection_status:
        assert "processing" in detection_status.text.lower() or "completed" in detection_status.text.lower(), \
            f"Unexpected detection status: {detection_status.text}"
        print(f"Detection status: {detection_status.text}")
    else:
        print("")

    print("Video detection test completed.")

def main():
    """Main test runner function."""
    url = "http://127.0.0.1:5000/"

    test_image_path = os.path.abspath("C:/Users/Yuvaraj/OneDrive/Desktop/Mini-Project/uploads/test1.png")
    test_video_path = os.path.abspath("C:/Users/Yuvaraj/OneDrive/Desktop/Mini-Project/uploads/1.mp4")

    driver = setup_driver()

    try:
        driver.get(url)

        test_webcam_feed(driver)

        test_image_detection(driver, test_image_path)

        test_video_detection(driver, test_video_path)

        print("All tests completed successfully!")

    except AssertionError as ae:
        print(f"Assertion error: {ae}")
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        driver.quit()
        print("Test completed.")

if __name__ == "__main__":
    main()
