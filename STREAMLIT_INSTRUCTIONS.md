# Streamlit Trademark Extraction UI

## Installation & Setup

1. **Install Required Dependencies**
   ```bash
   # Activate your virtual environment
   source venv/bin/activate
   
   # Install new dependencies
   pip install streamlit plotly pandas
   ```

2. **Set Environment Variable** (if not already set)
   ```bash
   export GROQ_API_KEY="your_groq_api_key_here"
   ```

## Running the Application

### Option 1: Direct Streamlit Command
```bash
cd /Users/apple/Trademark
source venv/bin/activate
streamlit run streamlit_app.py
```

### Option 2: Using the Run Script
```bash
cd /Users/apple/Trademark
source venv/bin/activate
python run_streamlit.py
```

## Features

The Streamlit UI provides a comprehensive interface for trademark extraction and comparison:

### 🏷️ Main Features:
- **PDF Upload**: Upload PDF files containing trademark information
- **Automatic Extraction**: Extract structured trademark data using AI
- **Database Comparison**: Compare extracted trademarks with existing CSV database
- **Similarity Analysis**: Find potential conflicts using multiple similarity algorithms
- **Visual Analytics**: Interactive charts and visualizations
- **Export Functionality**: Download results in CSV/JSON formats

### 📋 Sidebar Features:
- **CSV Database Upload**: Upload existing trademark database
- **Similarity Threshold**: Adjust comparison sensitivity (30-95%)
- **Database Statistics**: View current database metrics

### 🎯 Analysis Dashboard:
- **Summary Statistics**: Overview of extraction and comparison results
- **Export Data**: Download extracted data and comparison results
- **Advanced Settings**: Configuration and management options

## Usage Workflow

1. **Upload CSV Database** (Optional but recommended)
   - Click "Upload Existing Trademark Database (CSV)" in sidebar
   - Use CSV with columns: `Client / Applicant`, `Application No.`, `Trademark`, `Logo`, `Class`, `Status`, `Validity`

2. **Extract from PDF**
   - Upload a PDF file containing trademark information
   - View extracted trademark details for each page
   - See structured data including company info, trademark details, and contact information

3. **Review Similarity Analysis**
   - Automatic comparison with existing database
   - Color-coded similarity levels (High/Medium/Low)
   - Detailed scoring breakdown using multiple algorithms

4. **Export Results**
   - Download extracted data as CSV or JSON
   - Export comparison results for further analysis

## File Structure

```
/Users/apple/Trademark/
├── streamlit_app.py           # Main Streamlit application
├── run_streamlit.py           # Helper script to run the app
├── trademark_dal.py           # Data access layer for extraction
├── trademark_comparison.py    # Comparison algorithms
├── csv_manager.py            # CSV database management
├── existing_trademarks.csv   # Default database (created if not exists)
└── requirements.txt          # Dependencies
```

## Troubleshooting

### Common Issues:

1. **Missing Dependencies**
   ```bash
   pip install streamlit plotly pandas
   ```

2. **GROQ API Key Error**
   - Set environment variable: `export GROQ_API_KEY="your_key"`
   - Or create a `.env` file with `GROQ_API_KEY=your_key`

3. **CSV Format Issues**
   - Ensure CSV has required columns
   - Use UTF-8 encoding
   - Check for proper comma separation

4. **PDF Processing Errors**
   - Ensure PDF is not password-protected
   - Check PDF contains text/images (not just scanned images without OCR)
   - Try with smaller PDF files first

## Advanced Configuration

### Similarity Algorithm Weights:
The comparison uses multiple similarity metrics:
- **Phonetic Matching**: Soundex and Metaphone (30% weight)
- **Fuzzy String Matching**: Levenshtein, FuzzyWuzzy (70% weight)

### Similarity Threshold Recommendations:
- **85%+**: High similarity - Likely same brand
- **70-84%**: Medium similarity - Potential conflict
- **50-69%**: Low similarity - Worth reviewing
- **<50%**: Minimal similarity

## Support

For issues or questions:
1. Check the console output for detailed error messages
2. Verify all dependencies are installed
3. Ensure API keys are properly configured
4. Check file formats match expected structure