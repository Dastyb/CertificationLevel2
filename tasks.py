from robocorp.tasks import task
from robocorp import browser

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_robot_order_website()

def open_robot_order_website():
    """
    Opens the Robot Order website using robocorp.browser.
    """
    # Configure browser settings
    browser.configure(
        headless=False,  # Show the browser window (change to True for headless mode)
        slowmo=100,      # Add delay to observe interactions (in milliseconds)
        screenshot="only-on-failure",  # Take a screenshot if an error occurs
    )

    # Navigate to the Robot Order website
    url = "https://robotsparebinindustries.com/#/robot-order"
    browser.goto(url)
    print(f"Website opened: {url}")