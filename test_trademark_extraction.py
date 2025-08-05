#!/usr/bin/env python3
"""
Test script for trademark data extraction from ViewJournal.pdf
This script demonstrates how to use the trademark extraction system.
"""

import os
import sys
import json
from trademark_dal import TrademarkExtractor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Main function to test trademark extraction"""
    
    # Initialize the trademark extractor
    # Replace with your actual Groq API key
    groq_api_key = os.getenv("GROQ_API_KEY", "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")
    
    if groq_api_key == "your-groq-api-key-here":
        print(" Warning: Please set your GROQ_API_KEY in environment variables or .env file")
        print("Example: export GROQ_API_KEY='your_actual_api_key'")
        return
    
    try:
        extractor = TrademarkExtractor(groq_api_key=groq_api_key)
        print("Trademark extractor initialized successfully")
        
        # Check if ViewJournal.pdf exists
        pdf_file = "ViewJournal.pdf"
        if not os.path.exists(pdf_file):
            print(f"Error: {pdf_file} not found in current directory")
            return
        
        print(f"Processing {pdf_file}...")
        
        # Read the PDF file
        with open(pdf_file, "rb") as f:
            pdf_bytes = f.read()
        
        # Extract trademark data from all pages
        trademarks_data = extractor.extract_from_pdf_bytes(pdf_bytes)
        
        print(f"Successfully extracted data from {len(trademarks_data)} pages")
        
        # Save results to JSON file
        output_file = "extracted_trademarks.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(trademarks_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to {output_file}")
        
        # Display summary of extracted data
        print("EXTRACTION SUMMARY:")
        print("=" * 50)
        
        for i, trademark in enumerate(trademarks_data, 1):
            print(f"\n  TRADEMARK {i} (Page {trademark.get('page_number', 'N/A')}):")
            print(f"   Name: {trademark.get('name', 'N/A')}")
            print(f"   Address: {trademark.get('address', 'N/A')}")
            print(f"   City: {trademark.get('city', 'N/A')}")
            print(f"   Firm Type: {trademark.get('firm_type', 'N/A')}")
            print(f"   Date: {trademark.get('date', 'N/A')}")
            print(f"   Text in Logo: {trademark.get('text_in_logo', 'N/A')}")
            print(f"   Logo Description: {trademark.get('logo_description', 'N/A')}")
            print(f"   Registration Number: {trademark.get('registration_number', 'N/A')}")
            print(f"   Business Category: {trademark.get('business_category', 'N/A')}")
        
        print("\n Trademark extraction completed successfully!")
        print(f"Full details saved in {output_file}")
        
    except Exception as e:
        print(f"Error during extraction: {str(e)}")
        return

def test_with_sample_text():
    """Test with sample trademark text"""
    
    sample_text = """
    TRADEMARK REGISTRATION
    
    Application No: TM123456789
    Registration Date: 2024-01-15
    
    Applicant Information:
    Company Name: ABC Technologies Pvt Ltd
    Address: 123 Innovation Street, Tech Park
    City: Bangalore
    State: Karnataka
    Country: India
    Firm Type: Private Limited Company
    
    Trademark Details:
    Text in Logo: TECH INNOVATE
    Business Category: Computer Software and IT Services
    Description: Software development and technology consulting services
    
    Contact Information:
    Contact Person: John Smith
    Phone: +91-80-12345678
    Email: legal@abctech.com
    Website: www.abctech.com
    Legal Status: Registered
    """
    
    groq_api_key = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")
    
    if groq_api_key == "your-groq-api-key-here":
        print("⚠️  Warning: Please set your GROQ_API_KEY to test with sample text")
        return
    
    try:
        extractor = TrademarkExtractor(groq_api_key=groq_api_key)
        
        print("🧪 Testing with sample trademark text...")
        trademark_data = extractor.extract_trademark_data_from_text(sample_text)
        
        print("\n📋 EXTRACTED DATA:")
        print(json.dumps(trademark_data, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ Error during sample text extraction: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Trademark Data Extraction Test")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--sample":
        test_with_sample_text()
    else:
        main()
    
    print("\n" + "=" * 50)
    print("📝 Note: Make sure you have set your GROQ_API_KEY in environment variables")
    print("📖 Usage: python test_trademark_extraction.py [--sample]") 