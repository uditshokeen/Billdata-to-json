import openai
import pytesseract
from PIL import Image
import os
import json
from pdf2image import convert_from_path
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

#Load the environment variables
load_dotenv(dotenv_path="C:\og\AI\Billdata-to-json\.gitignore\.env" )

#access the open api key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


POPPLER_PATH = r'C:/Users/udits/Downloads/Release-24.08.0-0 (3)/poppler-24.08.0/Library/bin'

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

class BillEntry(BaseModel):
    """Model to capture each entry dynamically."""
    field_name: str = Field(..., description="The field name.")
    value: str = Field(..., description="The value of the field.")

class BillData(BaseModel):
    entries: List[BillEntry] = Field(..., description="A list of bill entries with dynamic field names and values.")

def extract_text_from_image(image_path):
    """Extracts text from a given image using Tesseract OCR."""
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        raise RuntimeError(f"Error extracting text from image: {e}")

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file by converting it to images and then using OCR."""
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Explicitly specify the Poppler path
        pages = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
        text = ""
        for page in pages:
            text += pytesseract.image_to_string(page)
        return text
    except Exception as e:
        raise RuntimeError(f"Error extracting text from PDF: {e}")

def process_bill_data_with_gpt(text):
    """Sends extracted text to OpenAI GPT for tabular interpretation."""
    openai.api_key = OPENAI_API_KEY

    prompt = (
        "You are tasked with extracting structured data from an image, scanned document, or PDF of a bill. Your objective is to accurately identify and extract all fields that appear in the document, regardless of format or layout. "
        "Dynamically detect all fields, including but not limited to Date, Description, Credit, Debit, Balance, and any other fields that may appear. Organize the extracted data into a table or list format, and ensure the output is a structured JSON or CSV format that includes all fields, even if some fields are empty or misaligned."
        "Return the extracted data as a list of key-value pairs, where each key represents a field name and the value is the corresponding value for that field.\n\n"
        f"Text:\n{text}\n\n"
        "Extracted fields and values:"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  
            messages=[
                {"role": "system", "content": "You are a helpful assistant that organizes data from documents into structured tables."},
                {"role": "user", "content": prompt},
            ],
        )

        # Check if the response is valid
        if response.get("choices"):
            return response["choices"][0]["message"]["content"]
        else:
            raise RuntimeError("Received empty or invalid response from GPT.")
    except Exception as e:
        raise RuntimeError(f"Error processing data with GPT: {e}")

def tabular_data_to_json(tabular_data):
    """Converts tabular data into JSON format dynamically."""
    try:
        # Clean and split the data into lines
        lines = [line.strip() for line in tabular_data.splitlines() if line.strip()]
        if not lines:
            raise RuntimeError("Tabular data is empty or improperly formatted.")

        # Parse each line as a field name-value pair
        entries = []
        for line in lines:
            # Assuming fields and values are separated by a common delimiter like ':', '=', or whitespace
            if ':' in line:
                field, value = line.split(":", 1)
            elif '=' in line:
                field, value = line.split("=", 1)
            else:
                # Split by first whitespace
                parts = line.split(None, 1)
                if len(parts) > 1:
                    field, value = parts
                else:
                    continue  # Skip malformed lines
            entries.append({
                "field_name": field.strip(),
                "value": value.strip()
            })

        # Use Pydantic to ensure the data is valid
        bill_data = BillData(entries=[BillEntry(**entry) for entry in entries])

        # Convert to JSON using model_dump() and json.dumps() for pretty formatting
        return json.dumps(bill_data.model_dump(), indent=4)
    except Exception as e:
        raise RuntimeError(f"Error converting tabular data to JSON: {e}")

def main():
    try:
        print("Starting the program...")  
        # Input: Path to the bill image or PDF
        file_path = input("Enter the path to the bill (image or PDF): ").strip().strip('"')
        print(f"File path provided: {file_path}")

        # Extract text from the file (image or PDF)
        extracted_text = ""
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            print("Extracting text from image...")
            extracted_text = extract_text_from_image(file_path)
        elif file_path.lower().endswith('.pdf'):
            print("Extracting text from PDF...")
            extracted_text = extract_text_from_pdf(file_path)
        else:
            print("Unsupported file format. Only PNG, JPG, JPEG, and PDF are supported.")
            return

        print("\nExtracted Text:")
        print(extracted_text)

        # Process extracted text with GPT
        if extracted_text.strip():
            print("\nProcessing data with GPT...")
            tabular_data = process_bill_data_with_gpt(extracted_text)
            if not tabular_data.strip():
                raise RuntimeError("GPT returned empty or invalid tabular data.")
            print("\nExtracted Fields and Values:")
            print(tabular_data)

            # Convert tabular data to JSON
            print("\nConverting to JSON format...")
            json_output = tabular_data_to_json(tabular_data)
            print("\nExtracted JSON Data:")
            print(json_output)
        else:
            print("No text extracted. Please check the file quality or format.")
            return

    except FileNotFoundError as fnf_error:
        print(f"File Error: {fnf_error}")
    except RuntimeError as run_error:
        print(f"Runtime Error: {run_error}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    print("Program is starting...") 
    main()
