import os
os.environ['DYLD_LIBRARY_PATH'] = '/opt/homebrew/Cellar/zbar/0.23.93/lib'

import json
import pdfplumber
from pdf2image import convert_from_path
from PIL import Image
from io import BytesIO
from pyzbar.pyzbar import decode





def read_text_from_pdf(pdf_path):
    # Open the PDF file
    with pdfplumber.open(pdf_path) as pdf:

        # Iterate through each page to extract text
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            # Define the areas for each column
            column1 = page.crop((0, 0, 140, 282.96))  # (x0, y0, x1, y1)
            column2 = page.crop((141, 0, 282.96, 282.96))  # (x0, y0, x1, y1)

            #Extracr text from the header of the file
            header = page.extract_text().split('\n')[0]
            # Extract text from each column starting from second line
            text_column1 = column1.extract_text().split('\n')[1:]
            text_column2 = column2.extract_text().split('\n')[1:]
            pdf_text = text_column1 + text_column2

            #Create a dictionary
            result_dict = {}
            for num in range(len(pdf_text)-1):
                key_value_pair = pdf_text[num].split(":")
                dict = {key_value_pair[0]: key_value_pair[1].strip()}
                result_dict.update(dict)

            # Convert dictionary to JSON
            result_json = json.dumps(result_dict, indent=4)

    return(result_json)



def extract_images_from_pdf(pdf_path):
    images = []
    # Convert PDF pages to images
    pdf_images = convert_from_path(pdf_path)
    for image in pdf_images:
        # Convert image to bytes
        image_bytes = image.tobytes()
        images.append(image_bytes)
    return images


def decode_barcodes_from_images(images):
    decoded_barcodes = []
    for image_bytes in images:
        image = Image.open(BytesIO(image_bytes))
        decoded_objects = decode(image)
        if decoded_objects:
            for obj in decoded_objects:
                barcode_data = obj.data.decode('utf-8')
                decoded_barcodes.append(barcode_data)
    return decoded_barcodes


text_from_pdf = read_text_from_pdf('test_task.pdf')
print(text_from_pdf)
images_from_pdf = extract_images_from_pdf('test_task.pdf')
decode_barcodes_from_images(images_from_pdf)












