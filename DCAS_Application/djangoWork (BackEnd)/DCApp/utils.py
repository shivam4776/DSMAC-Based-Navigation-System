# that code which will be added to DCA APP
import pyautogui
import cv2
import numpy as np
import time
import os


# Initialize variables
downMoves = 0
row = 1
col = 1

# Global variables to store received options
# def process_received_options(overlapping, imgQuality):
#     # Store or process the options
#     print(f"Option 1 received: {overlapping}")
#     print(f"Option 2 received: {imgQuality}")

#     # Example: Store them in global variables (use cautiously)
#     global received_overlapping, received_imgQuality
#     received_overlapping = overlapping
#     received_imgQuality = imgQuality

#     # Perform additional processing as needed
#     print("Processing options...")


# Helper functions
def detect_red_line(image):
    """
    Detects horizontal or vertical red lines in the given image.
    Returns:
        str: 'horizontal', 'vertical', or None.
    """
    image_hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    
    # Improved red color thresholds
    lower_red1 = np.array([0, 150, 150])   # Pure red lower range (saturated red)
    upper_red1 = np.array([10, 255, 255])  # Pure red upper range
    lower_red2 = np.array([170, 150, 150]) # Pure red lower range (towards 180° hue)
    upper_red2 = np.array([180, 255, 255]) # Pure red upper range

    
    # Combine masks for red detection
    mask1 = cv2.inRange(image_hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(image_hsv, lower_red2, upper_red2)
    mask = mask1 | mask2

    # Erode and dilate to remove noise
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 0.8 * image.shape[1]:  # Horizontal line condition
            return "horizontal"
        if h > 0.8 * image.shape[0]:  # Vertical line condition
            return "vertical"
    return None

def save_image(filename):
    """Saves the current screen to the specified filename."""
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)

def click_button(image_path, confidence=0.8, double_click=False):
    """Clicks a button on the screen based on its image."""
    location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
    if location:
        if double_click:
            pyautogui.doubleClick(location)
        else:
            pyautogui.click(location)
        time.sleep(0.5)

def drag_screen(start_x, start_y, end_x, end_y):
    """Drags the screen from one point to another."""
    pyautogui.moveTo(start_x, start_y)
    pyautogui.dragTo(end_x, end_y, duration=1)
    time.sleep(2)  # Ensure screen has updated after dragging

def main(overlapping,imgQuality, file_path):
    global downMoves, row, col

    received_imgQuality = imgQuality
    received_overlapping = bool(overlapping)

    print("Starting Google Earth Pro scraping...")

    # Initial setup
    os.startfile(file_path)
    time.sleep(20)
    # click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\shivamArea.png", double_click=True)
    # time.sleep(15)
    click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\hide_sidebar.png")
    time.sleep(1)
    click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\save_image.png")
    time.sleep(3)
    click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\map_options.png")
    time.sleep(1)

    # Uncheck boxes
    for checkbox in [r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\title_description.png", r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\legend.png", r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\scale.png", r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\compass.png"]:
        click_button(checkbox)

    # Set resolution to max
    click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\resolution.png")
    time.sleep(5)

    if received_imgQuality == "720 HD" and received_overlapping== True:
        click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\720 HD.png")
    
        while True:
            # Save the current image
            filename = f"img{row},{col}.png"
            click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\save_to_disk.png")
            pyautogui.write(filename)
            pyautogui.press("enter")
            time.sleep(5)
    
            # Add a small delay before capturing the screen
            time.sleep(1)
            screenshot = np.array(pyautogui.screenshot())
            line_type = detect_red_line(screenshot)
    
            if line_type == "vertical":
                print("Vertical line detected")
                downMoves += 1
                click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\hide_sidebar2.png")
                time.sleep(3) 
                click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\shivamArea2.png", double_click=True)
                time.sleep(15) 
                click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\hide_sidebar.png")
                time.sleep(1)
                for _ in range(downMoves):
                    drag_screen(960, 540, 960, 0)  # Vertical Overlapping
                row += 1
                col = 1
                continue
    
            if line_type == "horizontal":
                print("Horizontal line detected: First/Last row of images.")
                break
    
            
            drag_screen(960, 540, 0, 540)  # Horizontal Overlapping
            col += 1
    
        print("Scraping completed.")

    elif received_imgQuality == '8K UHD' and received_overlapping== True:
        click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\8K UHD.png")
        while True:
            # Save the current image
            filename = f"img{row},{col}.png"
            click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\save_to_disk.png")
            pyautogui.write(filename)
            pyautogui.press("enter")
            time.sleep(5)
    
            # Add a small delay before capturing the screen
            time.sleep(1)
            screenshot = np.array(pyautogui.screenshot())
            line_type = detect_red_line(screenshot)
    
            if line_type == "vertical":
                print("Vertical line detected")
                downMoves += 1
                click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\hide_sidebar2.png")
                time.sleep(3) 
                click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\shivamArea2.png", double_click=True)
                time.sleep(15) 
                click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\hide_sidebar.png")
                time.sleep(1)
                for _ in range(downMoves):
                    drag_screen(960, 540, 960, 0)  # Vertical Overlapping
                row += 1
                col = 1
                continue
    
            if line_type == "horizontal":
                print("Horizontal line detected: First/Last row of images.")
                break
    
            time.sleep(2)
            drag_screen(960, 540, 0, 540)  # Horizontal Overlapping
            col += 1
    
        print("Scraping completed.")

    elif received_imgQuality == '720 HD' and received_overlapping == False:
        click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCAppGooglepyAutoImages\720 HD.png")
        while True:
            # Save the current image
            filename = f"img{row},{col}.png"
            click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\save_to_disk.png")
            pyautogui.write(filename)
            pyautogui.press("enter")
            time.sleep(5)
    
            # Add a small delay before capturing the screen
            time.sleep(1)
            screenshot = np.array(pyautogui.screenshot())
            line_type = detect_red_line(screenshot)
    
            if line_type == "vertical":
                print("Vertical line detected")
                downMoves += 1
                click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\hide_sidebar2.png")
                time.sleep(3) 
                click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\shivamArea2.png", double_click=True)
                time.sleep(15) 
                click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\hide_sidebar.png")
                time.sleep(1)
                for _ in range(downMoves):
                    drag_screen(960, 1080, 960, 0)  # Vertical Overlapping
                row += 1
                col = 1
                continue
    
            if line_type == "horizontal":
                print("Horizontal line detected: First/Last row of images.")
                break
    
           
            drag_screen(1920, 540, 0, 540)  # Horizontal overlapping
            col += 1
    
        print("Scraping completed.")

    elif received_imgQuality == '8K UHD' and received_overlapping == False:
        click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\8K UHD.png")
        while True:
            # Save the current image
            filename = f"img{row},{col}.png"
            click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\save_to_disk.png")
            pyautogui.write(filename)
            pyautogui.press("enter")
            time.sleep(5)
    
            # Add a small delay before capturing the screen
            time.sleep(1)
            screenshot = np.array(pyautogui.screenshot())
            line_type = detect_red_line(screenshot)
    
            if line_type == "vertical":
                print("Vertical line detected")
                downMoves += 1
                click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\hide_sidebar2.png")
                time.sleep(3) 
                click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\shivamArea2.png", double_click=True)
                time.sleep(15) 
                click_button(r"C:\Users\parul\AllProjects\pyQt5\djangoWork\DCApp\GooglepyAutoImages\hide_sidebar.png")
                time.sleep(1)
                for _ in range(downMoves):
                    drag_screen(960, 1080, 960, 0)  # Vertical Overlapping
                row += 1
                col = 1
                continue
    
            if line_type == "horizontal":
                print("Horizontal line detected: First/Last row of images.")
                break
            time.sleep(2)
            drag_screen(1920, 540, 0, 540)  # Horizontal Overlapping
            col += 1
    
        print("Scraping completed.")


if __name__ == "__main__":
    main()
