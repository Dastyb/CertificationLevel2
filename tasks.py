from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF


http = HTTP()
tables = Tables()
pdf = PDF()

@task
def order_robots_from_RobotSpareBin():
    """
    - Orders robots from RobotSpareBin Industries Inc.
    - Saves the order HTML receipt as a PDF file.
    - Saves the screenshot of the ordered robot.
    - Embeds the screenshot of the robot to the PDF receipt.
    - Creates ZIP archive of the receipts and the images.
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
        receipt_path = store_receipt_as_pdf(order["Order number"])
        screenshot_path = screenshot_robot(order["Order number"])
        if screenshot_path and receipt_path:
            embed_screenshot_to_receipt(screenshot_path, receipt_path)
    except Exception as e:
        print(f"Failed to fill the form for order {order['Order number']}. Error: {e}")

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

def store_receipt_as_pdf(order_number):
    """Saves the order receipt as a PDF file in the output/receipts directory"""
    try:
        page = browser.page()
        receipt_html = page.locator("#receipt").inner_html()

        pdf = PDF()
        pdf_file = f"output/receipts/receipt_{order_number}.pdf"
        pdf.html_to_pdf(receipt_html, pdf_file)

        return pdf_file
    except Exception as e:
        print(f"Failed to save receipt as PDF for order {order_number}. Error: {e}")
        return None

def screenshot_robot(order_number):
    """Takes a screenshot of the robot preview and saves it in the output/screenshots directory"""
    try:
        page = browser.page()
        screenshot_file = f"output/screenshots/robot_preview_{order_number}.png"
        robot_preview_locator = page.locator("#robot-preview-image")
        robot_preview_locator.screenshot(path=screenshot_file)

        return screenshot_file
    except Exception as e:
        print(f"Failed to save receipt as PDF for order {order_number}. Error: {e}")
        return None

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embeds the robot screenshot at the end of the receipt PDF"""
    try:
        pdf = PDF()
        pdf.add_files_to_pdf([screenshot], pdf_file, append=True)
        print(f"Screenshot embedded in PDF: {pdf_file}")
        return pdf_file
    except Exception as e:
        print(f"Failed to embed screenshot in PDF {pdf_file}. Error: {e}")
        return None