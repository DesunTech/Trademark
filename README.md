# Trademark Data Extraction System

A comprehensive system for extracting trademark data from PDF files and images using AI-powered text recognition and structured data extraction.

## Features

- **PDF Processing**: Extract trademark data from multi-page PDF documents
- **Image Processing**: Support for JPG, PNG, BMP, TIFF image formats
- **AI-Powered**: Uses Groq's LLaMA models for intelligent text extraction and structuring
- **Structured Output**: Returns trademark data in consistent JSON format
- **RESTful **: FastAPI-based web service with automatic documentation
- **Batch Processing**: Process multiple pages/trademarks in a single PDF

## JSON Output Format

The system extracts trademark data in the following JSON structure:

```json
{
  "name": "Company/Applicant Name",
  "address": "Full Address",
  "city": "City Name",
  "firm_type": "Business Type (e.g., Private Limited, LLC)",
  "date": "Registration/Application Date",
  "text_in_logo": "Text appearing in trademark/logo",
  "registration_number": "Official registration number",
  "business_category": "Business category/classification",
  "contact_person": "Contact person name",
  "phone": "Phone number",
  "email": "Email address",
  "website": "Website URL",
  "legal_status": "Registration status",
  "description": "Description of goods/services",
  "state": "State/Province",
  "country": "Country",
  "page_number": "Page number (for PDF processing)"
}
```

## CSV Database Format

The system now works with CSV files containing existing trademark data. The required CSV columns are:

| Column | Description |
|--------|-------------|
| `Client / Applicant` | Name of the trademark applicant/owner |
| `Application No.` | Official application or registration number |
| `Trademark` | The trademark name/text |
| `Logo` | Description of logo/visual elements |
| `Class` | Trademark classification (e.g., 09, 42) |
| `Status` | Registration status (Registered, Pending, etc.) |
| `Validity` | Expiration or validity date |

See `trademark_csv_template.csv` for an example format.

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   
   Create a `.env` file in the project root:
   ```bash
   GROQ_API_KEY=your_groq_api_key_here
   ```
   
   Or set the environment variable directly:
   ```bash
   export GROQ_API_KEY="your_groq_api_key_here"
   ```

## Usage

### Option 1: Upload CSV Database and Compare

1. **Prepare your CSV database**:
   - Use the format: `Client / Applicant`, `Application No.`, `Trademark`, `Logo`, `Class`, `Status`, `Validity`
   - See `trademark_csv_template.csv` for reference

2. **Start the server**:
   ```bash
   python main.py
   ```

3. **Upload your CSV database**:
   - Use the `/csv/upload` endpoint
   - Or access  docs at [http://localhost:8000/docs](http://localhost:8000/docs)

4. **Extract and compare trademarks**:
   - Use `/extract/trademark/pdf_with_comparison` for PDF extraction with similarity analysis
   - Use `/compare/trademark` to compare individual trademarks

### Option 2: Using the Test Script

Test the comparison system (requires existing CSV):

```bash
python test_comparison.py
```

Extract trademarks without comparison:

```bash
python test_trademark_extraction.py
```

### Option 3: Using the FastAPI Web Service

**Key Endpoints**:

   - `POST /csv/upload` - Upload CSV database
   - `POST /extract/trademark/pdf_with_comparison` - Extract PDF + compare
   - `POST /compare/trademark` - Compare single trademark
   - `POST /extract/trademark/pdf` - Extract PDF only
   - `POST /extract/trademark/image` - Upload image file
   - `GET /csv/stats` - Database statistics
   - `GET /trademark/health` - Health check

### Option 3: Direct Python Usage

```python
from trademark_dal import TrademarkExtractor
import os

# Initialize extractor
api_key = os.getenv("GROQ_API_KEY")
extractor = TrademarkExtractor(groq_api_key=api_key)

# Process PDF file
with open("ViewJournal.pdf", "rb") as f:
    pdf_bytes = f.read()

trademarks = extractor.extract_from_pdf_bytes(pdf_bytes)

# Print results
for i, trademark in enumerate(trademarks, 1):
    print(f"Trademark {i}: {trademark['name']}")
    print(f"Address: {trademark['address']}")
    print(f"City: {trademark['city']}")
    print("---")
```

##  Examples

### Upload PDF via cURL

```bash
curl -X POST "http://localhost:8000//v1/extract/trademark/pdf" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@ViewJournal.pdf"
```

### Submit Text via cURL

```bash
curl -X POST "http://localhost:8000//v1/extract/trademark/text" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "TRADEMARK REGISTRATION\nCompany: ABC Corp\nAddress: 123 Main St\nCity: New York"
     }'
```

### Upload Image via cURL

```bash
curl -X POST "http://localhost:8000//v1/extract/trademark/image" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@trademark_document.jpg"
```

## Project Structure

```
├── trademark_dal.py          # Data access layer with AI extraction logic
├── trademark_controller.py   # FastAPI controller with  endpoints
├── main.py                  # FastAPI application entry point
├── test_trademark_extraction.py  # Test script for direct usage
├── requirements.txt         # Python dependencies
├── README.md               # This documentation
├── ViewJournal.pdf         # Sample PDF file to process
└── .env                    # Environment variables (create this)
```

## System Architecture

The system is built following the same patterns as the existing invoice extraction system:

1. **TrademarkExtractor (DAL)**: Core business logic for AI-powered extraction
2. **trademark_controller**: RESTful  endpoints using FastAPI
3. **main.py**: Application entry point and configuration
4. **test_trademark_extraction.py**: Command-line interface for testing

## Key Components

### TrademarkExtractor Class

- **Text Extraction**: Uses vision-capable LLaMA model to extract text from images
- **Data Structuring**: Uses LLaMA 3.3 70B to convert text into structured JSON
- **PDF Processing**: Handles multi-page PDFs by processing each page separately
- **Error Handling**: Robust error handling with informative messages

###  Endpoints

- **Flexible Input**: Support for PDF, images, text, and base64-encoded data
- **Consistent Output**: All endpoints return data in the same JSON structure
- **Validation**: Input validation and error handling
- **Documentation**: Auto-generated OpenAPI/Swagger documentation

## Configuration

### Environment Variables

- `GROQ_API_KEY`: Required for AI model access

### Model Configuration

The system uses two Groq models:
- **meta-llama/llama-4-scout-17b-16e-instruct**: For text extraction from images
- **llama-3.3-70b-versatile**: For structured data extraction

## Error Handling

The system includes comprehensive error handling for:
- Missing or invalid  keys
- Unsupported file formats
- PDF processing errors
- AI model errors
- JSON parsing errors

## Dependencies

Key dependencies include:
- **FastAPI**: Web framework for  endpoints
- **langchain-groq**: Integration with Groq AI models
- **PyMuPDF**: PDF processing and image extraction
- **python-dotenv**: Environment variable management

## Getting Your Groq  Key

1. Visit [console.groq.com](https://console.groq.com)
2. Sign up or log in to your account
3. Navigate to the  Keys section
4. Create a new  key
5. Copy the key and add it to your `.env` file

## Troubleshooting

### Common Issues

1. **"GROQ_API_KEY not found"**
   - Ensure you have set the GROQ_API_KEY environment variable
   - Check that your .env file is in the correct location

2. **"Module not found" errors**
   - Install all requirements: `pip install -r requirements.txt`
   - Ensure you're using Python 3.8 or higher

3. **PDF processing errors**
   - Ensure the PDF file exists and is readable
   - Check that the PDF is not password-protected

4. ** rate limits**
   - Groq has rate limits on  usage
   - Consider adding delays between requests for large batches

## License

This project is provided as-is for demonstration purposes. Please ensure you comply with Groq's terms of service when using their .

## Support

For issues related to:
- **Groq **: Visit [Groq Documentation](https://console.groq.com/docs)
- **FastAPI**: Visit [FastAPI Documentation](https://fastapi.tiangolo.com/)
- **PDF Processing**: Check PyMuPDF documentation 