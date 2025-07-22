#!/usr/bin/env python3
"""
Test script for trademark comparison functionality
This demonstrates how to use the trademark comparison system with CSV data.
"""

import os
import sys
import json
from trademark_dal import TrademarkExtractor
from trademark_comparison import TrademarkComparator
from csv_manager import TrademarkCSVManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_comparison_system():
    """Test the trademark comparison system"""
    
    print("=== TRADEMARK COMPARISON SYSTEM TEST ===\n")
    
    # Initialize components
    groq_api_key = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")
    
    if groq_api_key == "your-groq-api-key-here":
        print("Warning: Please set your GROQ_API_KEY in environment variables")
        print("For now, we'll test the comparison logic without extraction")
        use_extraction = False
    else:
        use_extraction = True
    
    # Initialize components
    csv_manager = TrademarkCSVManager()
    comparator = TrademarkComparator()
    
    if use_extraction:
        extractor = TrademarkExtractor(groq_api_key=groq_api_key)
    
    # Step 1: Check for existing CSV data
    print("1. Checking for existing CSV database...")
    if not os.path.exists(csv_manager.csv_file_path):
        print(f"No CSV file found at {csv_manager.csv_file_path}")
        print("Please upload a CSV file with columns: Client / Applicant, Application No., Trademark, Logo, Class, Status, Validity")
        print("You can use the /csv/upload endpoint or place a CSV file manually.")
        return
    
    # Load the CSV data into comparator
    comparator.load_existing_trademarks_from_csv(csv_manager.csv_file_path)
    
    if not comparator.existing_trademarks:
        print("No trademark data found in CSV. Please ensure CSV has the correct format.")
        return
    
    # Step 2: Test with sample new trademarks
    print("\n2. Testing comparison with sample new trademarks...")
    
    test_trademarks = [
        {
            "Client / Applicant": "Apple Technologies Inc.",
            "Trademark": "Apple",
            "Application No.": "APP2024001",
            "Class": "Technology",
            "Status": "Pending"
        },
        {
            "Client / Applicant": "Microsofy Corporation",
            "Trademark": "Microsofy",
            "Application No.": "APP2024002", 
            "Class": "Software",
            "Status": "Pending"
        },
        {
            "Client / Applicant": "TechCorp Solutions",
            "Trademark": "TechCorp",
            "Application No.": "APP2024003",
            "Class": "Consulting",
            "Status": "Pending"
        }
    ]
    
    # Test each trademark
    for i, test_trademark in enumerate(test_trademarks, 1):
        print(f"\n--- TESTING TRADEMARK {i}: {test_trademark['Client / Applicant']} ---")
        
        # Generate comparison report
        report = comparator.generate_comparison_report(test_trademark, similarity_threshold=50.0)
        
        print(f"New Applicant: {report['new_trademark']['name']}")
        print(f"Trademark: {report['new_trademark']['trademark']}")
        print(f"Application No.: {report['new_trademark']['application_no']}")
        print(f"Similar trademarks found: {report['similar_trademarks_found']}")
        
        if report['matches']:
            print("\nSIMILARITY MATCHES:")
            for match in report['matches']:
                existing = match['existing_trademark']
                print(f"  • Match: {existing['Client / Applicant']} (Trademark: {existing['Trademark']})")
                print(f"    Application No.: {existing['Application No.']}")
                print(f"    Class: {existing['Class']}")
                print(f"    Status: {existing['Status']}")
                print(f"    Similarity Score: {match['similarity_score']}%")
                print(f"    Level: {match['similarity_level']}")
                print(f"    Type: {match['similarity_type']} comparison")
                print(f"    Applicant Phonetic Score: {match['detailed_scores']['name_comparison']['phonetic']['avg_phonetic']}%")
                print(f"    Applicant Fuzzy Score: {match['detailed_scores']['name_comparison']['fuzzy']['avg_fuzzy']}%")
                print()
        else:
            print("  No similar trademarks found above threshold")
    
    # Step 3: Test direct similarity methods
    print("\n3. Testing direct similarity comparison methods...")
    
    test_pairs = [
        ("Apple", "Aple"),
        ("Microsoft", "Microsofy"),
        ("Microsoft", "MicroSoft"),
        ("TechCorp", "TechCorporation"),
        ("Google", "Apple")
    ]
    
    print("\nDIRECT SIMILARITY TESTS:")
    for name1, name2 in test_pairs:
        similarity = comparator.calculate_overall_similarity(name1, name2)
        print(f"\n'{name1}' vs '{name2}':")
        print(f"  Soundex Match: {similarity['soundex']}")
        print(f"  Metaphone Match: {similarity['metaphone']}")
        print(f"  Levenshtein Similarity: {similarity['levenshtein']:.1f}%")
        print(f"  Fuzzy Ratio: {similarity['fuzzy_ratio']}%")
        print(f"  Overall Score: {similarity['overall_similarity']:.1f}%")
        print(f"  Classification: {comparator.classify_similarity_level(similarity['overall_similarity'])}")
    
    # Step 4: Extract and compare from PDF if API key is available
    if use_extraction and os.path.exists("ViewJournal.pdf"):
        print("\n4. Testing PDF extraction with comparison...")
        
        try:
            # Extract from PDF
            with open("ViewJournal.pdf", "rb") as file:
                pdf_bytes = file.read()
            
            extracted_trademarks = extractor.extract_from_pdf_bytes(pdf_bytes)
            
            print(f"Extracted {len(extracted_trademarks)} trademarks from ViewJournal.pdf")
            
            # Compare each extracted trademark
            for i, trademark in enumerate(extracted_trademarks, 1):
                print(f"\n--- PDF TRADEMARK {i} ---")
                report = comparator.generate_comparison_report(trademark, similarity_threshold=50.0)
                
                print(f"Extracted: {report['new_trademark']['name']}")
                print(f"Similar matches: {report['similar_trademarks_found']}")
                
                if report['matches']:
                    best_match = report['matches'][0]  # Highest similarity
                    print(f"Best match: {best_match['existing_trademark']['name']}")
                    print(f"Similarity: {best_match['similarity_score']}%")
                    print(f"Level: {best_match['similarity_level']}")
                
        except Exception as e:
            print(f"Error during PDF extraction: {str(e)}")
    
    # Step 5: Save results
    print("\n5. Saving test results...")
    
    # Export CSV to JSON for review
    csv_manager.export_to_json("test_trademark_database.json")
    
    # Save comparison results
    all_results = []
    for trademark in test_trademarks:
        report = comparator.generate_comparison_report(trademark, similarity_threshold=50.0)
        all_results.append(report)
    
    with open("comparison_test_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print("Test results saved to:")
    print("  - test_trademark_database.json (CSV export)")
    print("  - comparison_test_results.json (comparison results)")
    
    # Display CSV statistics
    print("\n6. CSV Database Statistics:")
    stats = csv_manager.get_csv_stats()
    print(f"  Total Trademarks: {stats['total_trademarks']}")
    print(f"  Unique Applicants: {stats['unique_applicants']}")
    print(f"  Classes: {stats['classes']}")
    print(f"  Statuses: {stats['statuses']}")
    
    print("\n=== COMPARISON SYSTEM TEST COMPLETED ===")


if __name__ == "__main__":
    test_comparison_system() 