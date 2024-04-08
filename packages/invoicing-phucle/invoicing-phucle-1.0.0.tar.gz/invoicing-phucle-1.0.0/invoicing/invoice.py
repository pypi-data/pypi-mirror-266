import os
import pandas as pd
import glob
from fpdf import FPDF
from pathlib import Path


def generate(invoices_path, pdfs_path, image_path, product_id, product_name, amount_purchased, price_per_unit, total_price):
    """
    This function converts Excel files to PDF invoices
    :param invoices_path:
    :param pdfs_path:
    :param image_path:
    :param product_id:
    :param product_name:
    :param amount_purchased:
    :param price_per_unit:
    :param total_price:
    :return:
    """
    # Get all Excel files in the 'invoices' directory
    filepaths = glob.glob(f'{invoices_path}/*xlsx')

    # Loop through each file
    for filepath in filepaths:

        # Create a new PDF with A4 size
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.add_page()

        # Get the filename without extension and split it to get invoice number and date
        filename = Path(filepath).stem
        invoice_nr = str(filename).split("-")[0]
        date = str(filename).split("-")[1]

        # Set font and add invoice number to the PDF
        pdf.set_font(family="Times", style="B", size=16)
        pdf.cell(w=50, h=8, txt=f"Invoice nr. {invoice_nr}", align="L", ln=1)

        # Add date to the PDF
        pdf.cell(w=0, h=12, txt=f"Date: {date}", align="L", ln=1)

        # Read the Excel file into a pandas DataFrame
        df = pd.read_excel(filepath, sheet_name="Sheet 1")
        df_columns = df.columns.tolist()

        # Loop through each column in the DataFrame
        for index, column in enumerate(df_columns):
            # Split the column name by underscore and capitalize each word
            column_split = [word.title() for word in column.split("_")]
            column_name = " ".join(column_split)

            # Set font and add column name to the PDF
            pdf.set_font(family="Times", style="B", size=12)
            if index == 1:
                pdf.cell(w=60, h=8, txt=column_name, border=1)
            elif index == 2:
                pdf.cell(w=40, h=8, txt=column_name, border=1)
            else:
                pdf.cell(w=30, h=8, txt=column_name, border=1)
        pdf.ln()

        # Initialize total variable
        total = 0

        # Loop through each row in the DataFrame
        for index, row in df.iterrows():
            # Set font and add row data to the PDF
            pdf.set_font(family="Times", size=10)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(w=30, h=8, txt=str(row[product_id]), border=1)
            pdf.cell(w=60, h=8, txt=str(row[product_name]), border=1)
            pdf.cell(w=40, h=8, txt=str(row[amount_purchased]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[price_per_unit]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[total_price]), border=1, ln=1)

            # Add the total price to the total variable
            total += row[total_price]

        # Add empty cells and the total to the PDF
        pdf.cell(w=30, h=8, txt=" ", border=1)
        pdf.cell(w=60, h=8, txt=" ", border=1)
        pdf.cell(w=40, h=8, txt=" ", border=1)
        pdf.cell(w=30, h=8, txt=" ", border=1)
        pdf.cell(w=30, h=8, txt=str(total), border=1)

        # Add total due amount to the PDF
        pdf.ln(15)
        pdf.set_font(family="Times", style="B", size=12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(w=50, h=10, txt=f"The total due amount is {total} Euros.", ln=1)

        # Add company name to the PDF
        pdf.cell(w=50, h=10, txt="Phuc Proton")

        # Add company logo to the PDF
        pdf.image(image_path, x=60, y=100, w=100, h=80)

        # Save the PDF to the 'invoices_pdf' directory
        if not os.path.exists(pdfs_path):
            os.makedirs(pdfs_path)
        pdf.output(f"{pdfs_path}/{filename}.pdf")