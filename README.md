# Billdata-to-json
This Python project extracts structured data from scanned bills or invoices (in image or PDF format) and outputs the data in JSON format. It uses Tesseract OCR for text extraction, Poppler for PDF-to-image conversion, and OpenAI's GPT for intelligent field detection and data organization.

Features:
•	Supports Multiple Formats: Handles image files (PNG, JPG, JPEG) and PDF files by using Tesseract OCR and Poppler.
•	Automated Data Extraction: Automatically detects fields like Date, Description, Amount, Debit, Credit, and more, extracting them into a structured format.
•	OpenAI GPT Integration: Uses GPT to interpret and organize the extracted text into a tabular or list format for easy data extraction.
•	Pydantic Validation: Ensures that the output is validated and follows a strict data schema for consistency.
•	Dynamic Field Handling: Extracted fields are stored as dynamic key-value pairs, allowing flexibility in the types of bills that can be processed.
•	JSON Output: Converts the tabular or list data into well-structured JSON for easy further use or storage.
•	Environment Variable Support: Uses .env files to securely manage sensitive data like the OpenAI API key.

How It Works:
1.	Text Extraction: The program uses Tesseract OCR to extract text from images and PDF files. For PDFs, it first converts pages into images using Poppler.
2.	Field Extraction: Extracted text is sent to OpenAI GPT, which intelligently identifies and organizes key-value pairs in a structured manner.
3.	JSON Conversion: The data is then validated using Pydantic models and converted to JSON format, which is then displayed.
   
Tech Stack:
•	Python: The primary programming language.
•	Tesseract OCR: Used for extracting text from images.
•	Poppler: For PDF-to-image conversion.
•	OpenAI GPT-4: For intelligent text processing and field extraction.
•	Pydantic: Ensures data integrity and validation.
•	dotenv: Secure management of environment variables.


