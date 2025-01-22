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
    close_annoying_modal()
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

def close_annoying_modal():
    """Closes the annoying modal that appears when the website is loaded."""
    try:
        browser.page().locator("button:has-text('OK')").click()

    except Exception as e:
        print(f"Modal not found or already closed. Error: {e}")

def get_orders():
    """Downloads the orders CSV file, reads it as a table, and returns the result"""
    url = "https://robotsparebinindustries.com/orders.csv"
    file_path = "orders.csv"  
    http.download(url, file_path, overwrite=True)
    orders_table = tables.read_table_from_csv(file_path)

    return orders_table

def process_orders(orders):
    """Iterates through the orders and logs each order"""
    for order in orders:
        print(f"Processing order: {order}")
        fill_the_form(order)

def fill_the_form(order):
    """Fills out the robot order form with the data from a single order"""
    try:
        browser.page().locator('select[name="head"]').select_option(value=order["Head"])
        browser.page().locator(f'label[for="id-body-{order["Body"]}"]').click()
        browser.page().locator('//input[@type="number" and @placeholder="Enter the part number for the legs"]').fill(order["Legs"])
        browser.page().locator('input[name="address"]').fill(order["Address"])
        browser.page().locator('button:text("Preview")').click()
        submit_order(order)

    except Exception as e:
        print(f"Failed to fill the form for order {order['Order ID']}. Error: {e}")

def submit_order(order):
    """Submits the robot order and retries if a server error occurs."""
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            browser.page().locator('button:text("Order")').click()
            if browser.page().locator('div.alert.alert-danger').is_visible():
                print("Server error detected for order")
            else:
                print("Order submitted successfully")
                break
        except Exception as e:
            print(f"Error on attempt {attempt}: {e}")
        if attempt < max_retries:
            browser.page().wait_for_timeout(1000)
        else:
            print(f"Failed to submit order after {max_retries} attempts")