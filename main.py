
#######these two lines are needed to setup PATH to zbar library##########
#import os
#os.environ['DYLD_LIBRARY_PATH'] = '/opt/homebrew/Cellar/zbar/0.23.93/lib'


#Code starts here:
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

            #Extract text from the header of the file
            header = page.extract_text().split('\n')[0]

            # Extract text from each column starting from second line
            text_column1 = column1.extract_text().split('\n')[1:]
            text_column2 = column2.extract_text().split('\n')[1:]
            pdf_text = text_column1 + text_column2

            #Create a dictionary
            result_dict = {}
            result_dict[f'{header}'] = {}
            for num in range(len(pdf_text)-1):
                key_value_pair = pdf_text[num].split(":")
                dict = {key_value_pair[0]: key_value_pair[1].strip()}
                result_dict[f'{header}'].update(dict)

    return(result_dict)


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


def compare_to_sample(test_pdf_path, sample_pdf_path):
    comparison_result = {}

    with pdfplumber.open(test_pdf_path) as test_pdf_data:
        with pdfplumber.open(sample_pdf_path) as sample_pdf_data:
            # Compare total number of pages
            if len(test_pdf_data.pages) != len(sample_pdf_data.pages):
                comparison_result['total_pages_match'] = False
            else:
                comparison_result['total_pages_match'] = True

     # Compare each page text
    if len(test_pdf_data.pages) <= len(sample_pdf_data.pages):
        for page_num in range(len(test_pdf_data.pages)):
            page_comparison_results = {}
            test_data_text = read_text_from_pdf(test_pdf_path)
            sample_data_text = read_text_from_pdf(sample_pdf_path)

            # Compare headers
            page_headers_test = list(test_data_text.keys())
            page_headers_sample = list(sample_data_text.keys())
            if page_headers_test != page_headers_sample:
                page_comparison_results['page_headers_match'] = False

            else:
                page_comparison_results['page_headers_match'] = True

            # Compare body
            page_body_test = list(test_data_text[page_headers_test[page_num]].keys())
            page_body_sample = list(sample_data_text[page_headers_sample[page_num]].keys())
            if page_body_test != page_body_sample:
                page_comparison_results['page_body_match'] = False
            else:
                page_comparison_results['page_body_match'] = True

            comparison_result[f'Page N {page_num + 1}'] = page_comparison_results

        # Compare each page images
        images_sample = extract_images_from_pdf(sample_pdf_path)
        images_test = extract_images_from_pdf(test_pdf_path)
        if images_test != images_sample:
            comparison_result['images'] = False
        else:
            comparison_result['images'] = True

    return comparison_result



text_from_pdf = read_text_from_pdf('test_task.pdf')
text_in_json = json.dumps(text_from_pdf, indent=4)
print(text_in_json)

images_from_pdf = extract_images_from_pdf('test_task.pdf')

# Read barcodes if they are valid
# barcodes = decode_barcodes_from_images(images_from_pdf)

comparison_final = compare_to_sample('test_task.pdf', "test_task.pdf")
comparison_in_json = json.dumps(comparison_final, indent=4)
print(comparison_in_json)








