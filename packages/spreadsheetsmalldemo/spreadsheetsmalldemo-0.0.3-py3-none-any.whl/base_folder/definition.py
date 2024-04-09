from RPA.HTTP import HTTP
from RPA.Excel.Files import Files
from RPA.PDF import PDF
from .locators import Locators
from .browser import Browser

class HTMLConversor(Browser):
    def __init__(self):
        super(HTMLConversor, self).__init__()
    

    def to_pdf(self):
        """Insert the sales data for the week and export it as a PDF"""

        self.open_the_intranet_website()
        self.log_in()
        self.download_excel_file()
        self.fill_form_with_excel_data()
        self.collect_results()
        self.export_as_pdf()
        self.log_out()

    def open_the_intranet_website(self):
        """Navigates to the given URL"""
        self.browser.goto(Locators.main_url)

    def log_in(self):
        """Fills in the login form and clicks the 'Log in' button"""
        page = self.browser.page()
        page.fill(Locators.username, "maria")
        page.fill(Locators.password, "thoushallnotpass")
        page.click(Locators.login_button)

    def fill_and_submit_sales_form(self, sales_rep):
        """Fills in the sales data and click the 'Submit' button"""
        page = self.browser.page()

        page.fill(Locators.first_name, sales_rep["First Name"])
        page.fill(Locators.last_name, sales_rep["Last Name"])
        page.select_option(Locators.sales_target, str(sales_rep["Sales Target"]))
        page.fill(Locators.sales_result, str(sales_rep["Sales"]))
        page.click(Locators.submit_button)

    def download_excel_file(self):
        """Downloads excel file from the given URL"""
        http = HTTP()
        http.download(url=Locators.excel_url, overwrite=True)

    def fill_form_with_excel_data(self):
        """Read data from excel and fill in the sales form"""
        excel = Files()
        excel.open_workbook(Locators.excel_file_name)
        worksheet = excel.read_worksheet_as_table("data", header=True)
        excel.close_workbook()

        for row in worksheet:
            self.fill_and_submit_sales_form(row)

    def collect_results(self):
        """Take a screenshot of the page"""
        page = self.browser.page()
        page.screenshot(path=Locators.output_sales_summary)

    def export_as_pdf(self):
        """Export the data to a pdf file"""
        page = self.browser.page()
        sales_results_html = page.locator(Locators.sales_results).inner_html()

        pdf = PDF()
        pdf.html_to_pdf(sales_results_html, Locators.output_sales_pdf)

    def log_out(self):
        """Presses the 'Log out' button"""
        page = self.browser.page()
        page.click(Locators.logout_button)