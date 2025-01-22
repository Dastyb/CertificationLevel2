from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables


http = HTTP()
tables = Tables()

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
    orders = get_orders()
    process_orders(orders)

def open_robot_order_website():
    """Opens the Robot Order website using robocorp.browser."""
    browser.configure(
        headless=False,  
        slowmo=1000,      
        screenshot="only-on-failure",
    )

    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders():
    """Downloads the orders CSV file, reads it as a table, and returns the result."""
    url = "https://robotsparebinindustries.com/orders.csv"
    file_path = "orders.csv"  
    http.download(url, file_path, overwrite=True)
    orders_table = tables.read_table_from_csv(file_path)

    return orders_table

def process_orders(orders):
    """Iterates through the orders and logs each order."""
    for order in orders:
        print(f"Processing order: {order}")