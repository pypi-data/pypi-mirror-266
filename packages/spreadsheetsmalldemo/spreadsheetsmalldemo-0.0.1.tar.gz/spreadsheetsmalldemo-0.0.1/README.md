# HTMLConversor

HTMLConversor is a Python class that automates the process of converting sales data from an intranet website to a PDF file. It utilizes the Robot Framework's RPA library for web automation.

## Features

- Log in to the intranet website.
- Download sales data stored in an Excel file.
- Fill in a sales form with data from the Excel file.
- Collect sales results and export them as a PDF file.
- Log out from the intranet website.

## Installation

1. Make sure you have Python installed on your system.
2. Install the required dependencies using pip


## Usage

```python
from HTMLConversor import HTMLConversor

# Initialize HTMLConversor
converter = HTMLConversor()

# Convert sales data to PDF
converter.to_pdf()

