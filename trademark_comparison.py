import re
import csv
import json
from typing import List, Dict, Tuple
from difflib import SequenceMatcher
import jellyfish  # For Soundex, Metaphone, and Levenshtein distance
from fuzzywuzzy import fuzz, process


class TrademarkComparator:
    def __init__(self):
        self.existing_trademarks = []
        
    def load_existing_trademarks_from_csv(self, csv_file_path: str):
        """Load existing trademark data from CSV file"""

        except Exception as e:
            print(f"Error loading CSV: {str(e)}")
            self.existing_trademarks = []
    
    def normalize_name(self, name: str) -> str:
        """Normalize name for better comparison"""
        if not name:
            return ""
        
        # Convert to lowercase and remove special characters
        normalized = re.sub(r'[^\w\s]', ' ', name.lower())
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        return normalized
    
    def phonetic_similarity(self, name1: str, name2: str) -> Dict[str, float]:
        """Calculate phonetic similarity using Soundex and Metaphone"""
        if not name1 or not name2
        
        return {
            "soundex": soundex_match,
            "metaphone": metaphone_match,
            "avg_phonetic": avg_phonetic
        }
    
    def fuzzy_similarity(self, name1: str, name2: str) -> Dict[str, float]:
        """Calculate fuzzy string similarity using various Levenshtein-based methods"""
        
        return {
            "levenshtein": levenshtein_similarity,
            "fuzzy_ratio": fuzzy_ratio,
            "partial_ratio": partial_ratio,
            "token_sort": token_sort_ratio,
            "avg_fuzzy": avg_fuzzy
        }
        
    def find_similar_trademarks(self, new_trademark: Dict, similarity_threshold: float = 50.0) -> List[Dict]:
        """Find similar trademarks in the existing database"""
        if not self.existing_trademarks:
            return []
        
        similar_trademarks = []
        
        # Handle both old format (from extraction) and new CSV format
                        
            if max_similarity >= similarity_threshold:
                similar_trademarks.append({
                    "existing_trademark": existing,
                    "name_similarity": name_similarity,
                    "logo_similarity": logo_similarity,
                    "max_similarity_score": max_similarity,
                    "similarity_type": similarity_type,
                    "fallback_used": fallback_used,
                    "comparison_note": "Used Client/Applicant name for trademark comparison (Trademark column empty)" if fallback_used else "Normal comparison"
                })
        
        # Sort by similarity score (highest first)
        similar_trademarks.sort(key=lambda x: x["max_similarity_score"], reverse=True)
        
        return similar_trademarks
    
    def classify_similarity_level(self, score: float) -> str:
        """Classify similarity level based on score"""
        if score >= 85:
            return "HIGH - Likely same brand"
        elif score >= 70:
            return "MEDIUM - Potential conflict"
        elif score >= 50:
            return "LOW - Worth reviewing"
        else:
            return "MINIMAL - No significant similarity"
    
    def generate_comparison_report(self, new_trademark: Dict, similarity_threshold: float = 50.0) -> Dict:
        """Generate a comprehensive comparison report"""
        similar_trademarks = self.find_similar_trademarks(new_trademark, similarity_threshold)
        return similar_trademarks 
