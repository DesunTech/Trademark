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
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.existing_trademarks = list(reader)
            print(f"Loaded {len(self.existing_trademarks)} existing trademarks from CSV")
        except FileNotFoundError:
            print(f"CSV file {csv_file_path} not found. Creating empty trademark database.")
            self.existing_trademarks = []
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
        if not name1 or not name2:
            return {"soundex": 0.0, "metaphone": 0.0, "avg_phonetic": 0.0}
        
        # Normalize names
        norm1 = self.normalize_name(name1)
        norm2 = self.normalize_name(name2)
        
        # Soundex comparison
        soundex1 = jellyfish.soundex(norm1)
        soundex2 = jellyfish.soundex(norm2)
        soundex_match = 1.0 if soundex1 == soundex2 else 0.0
        
        # Metaphone comparison  
        metaphone1 = jellyfish.metaphone(norm1)
        metaphone2 = jellyfish.metaphone(norm2)
        metaphone_match = 1.0 if metaphone1 == metaphone2 else 0.0
        
        # Average phonetic score
        avg_phonetic = (soundex_match + metaphone_match) / 2
        
        return {
            "soundex": soundex_match,
            "metaphone": metaphone_match,
            "avg_phonetic": avg_phonetic
        }
    
    def fuzzy_similarity(self, name1: str, name2: str) -> Dict[str, float]:
        """Calculate fuzzy string similarity using various Levenshtein-based methods"""
        if not name1 or not name2:
            return {"levenshtein": 0.0, "fuzzy_ratio": 0.0, "partial_ratio": 0.0, "token_sort": 0.0, "avg_fuzzy": 0.0}
        
        # Normalize names
        norm1 = self.normalize_name(name1)
        norm2 = self.normalize_name(name2)
        
        # Levenshtein distance (convert to similarity percentage)
        levenshtein_dist = jellyfish.levenshtein_distance(norm1, norm2)
        max_len = max(len(norm1), len(norm2))
        levenshtein_similarity = (1 - (levenshtein_dist / max_len)) * 100 if max_len > 0 else 0
        
        # FuzzyWuzzy ratios
        fuzzy_ratio = fuzz.ratio(norm1, norm2)
        partial_ratio = fuzz.partial_ratio(norm1, norm2)
        token_sort_ratio = fuzz.token_sort_ratio(norm1, norm2)
        
        # Average fuzzy score
        avg_fuzzy = (levenshtein_similarity + fuzzy_ratio + partial_ratio + token_sort_ratio) / 4
        
        return {
            "levenshtein": levenshtein_similarity,
            "fuzzy_ratio": fuzzy_ratio,
            "partial_ratio": partial_ratio,
            "token_sort": token_sort_ratio,
            "avg_fuzzy": avg_fuzzy
        }
    
    def calculate_overall_similarity(self, name1: str, name2: str) -> Dict[str, float]:
        """Calculate overall similarity combining phonetic and fuzzy matching"""
        phonetic_scores = self.phonetic_similarity(name1, name2)
        fuzzy_scores = self.fuzzy_similarity(name1, name2)
        
        # Weighted combination (adjust weights as needed)
        phonetic_weight = 0.3
        fuzzy_weight = 0.7
        
        overall_score = (phonetic_scores["avg_phonetic"] * phonetic_weight * 100) + (fuzzy_scores["avg_fuzzy"] * fuzzy_weight)
        
        return {
            **phonetic_scores,
            **fuzzy_scores,
            "overall_similarity": overall_score
        }
    
    def find_similar_trademarks(self, new_trademark: Dict, similarity_threshold: float = 50.0) -> List[Dict]:
        """Find similar trademarks in the existing database"""
        if not self.existing_trademarks:
            return []
        
        similar_trademarks = []
        
        # Handle both old format (from extraction) and new CSV format
        new_name = new_trademark.get("name", "") or new_trademark.get("Client / Applicant", "")
        new_logo_text = new_trademark.get("text_in_logo", "") or new_trademark.get("Trademark", "")
        
        for existing in self.existing_trademarks:
            existing_name = existing.get("Client / Applicant", "")
            existing_logo_text = existing.get("Trademark", "")
            
            # Fallback: If Trademark column is empty, use Client/Applicant for trademark comparison
            if not existing_logo_text or not existing_logo_text.strip():
                existing_logo_text = existing_name
                fallback_used = True
            else:
                fallback_used = False
            
            # Compare company names/applicants
            name_similarity = self.calculate_overall_similarity(new_name, existing_name)
            
            # Compare trademark/logo text (may use fallback)
            logo_similarity = self.calculate_overall_similarity(new_logo_text, existing_logo_text)
            
            # Determine comparison type more accurately
            if fallback_used:
                # If fallback was used, both comparisons are essentially the same
                max_similarity = max(name_similarity["overall_similarity"], logo_similarity["overall_similarity"])
                similarity_type = "applicant_name"  # Both are comparing against applicant name
            else:
                # Normal case: separate name and trademark comparisons
                max_similarity = max(name_similarity["overall_similarity"], logo_similarity["overall_similarity"])
                similarity_type = "applicant" if name_similarity["overall_similarity"] > logo_similarity["overall_similarity"] else "trademark"
            
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
        
        report = {
            "new_trademark": {
                "name": new_trademark.get("name", "") or new_trademark.get("Client / Applicant", ""),
                "trademark": new_trademark.get("text_in_logo", "") or new_trademark.get("Trademark", ""),
                "application_no": new_trademark.get("registration_number", "") or new_trademark.get("Application No.", ""),
                "class": new_trademark.get("business_category", "") or new_trademark.get("Class", ""),
                "status": new_trademark.get("legal_status", "") or new_trademark.get("Status", "")
            },
            "total_existing_trademarks": len(self.existing_trademarks),
            "similar_trademarks_found": len(similar_trademarks),
            "similarity_threshold": similarity_threshold,
            "matches": []
        }
        
        for match in similar_trademarks:
            match_report = {
                "existing_trademark": match["existing_trademark"],
                "similarity_score": round(match["max_similarity_score"], 2),
                "similarity_level": self.classify_similarity_level(match["max_similarity_score"]),
                "similarity_type": match["similarity_type"],
                "detailed_scores": {
                    "name_comparison": {
                        "phonetic": {
                            "soundex": match["name_similarity"]["soundex"],
                            "metaphone": match["name_similarity"]["metaphone"],
                            "avg_phonetic": round(match["name_similarity"]["avg_phonetic"] * 100, 2)
                        },
                        "fuzzy": {
                            "levenshtein": round(match["name_similarity"]["levenshtein"], 2),
                            "fuzzy_ratio": match["name_similarity"]["fuzzy_ratio"],
                            "partial_ratio": match["name_similarity"]["partial_ratio"],
                            "token_sort": match["name_similarity"]["token_sort"],
                            "avg_fuzzy": round(match["name_similarity"]["avg_fuzzy"], 2)
                        },
                        "overall": round(match["name_similarity"]["overall_similarity"], 2)
                    },
                    "logo_comparison": {
                        "phonetic": {
                            "soundex": match["logo_similarity"]["soundex"],
                            "metaphone": match["logo_similarity"]["metaphone"],
                            "avg_phonetic": round(match["logo_similarity"]["avg_phonetic"] * 100, 2)
                        },
                        "fuzzy": {
                            "levenshtein": round(match["logo_similarity"]["levenshtein"], 2),
                            "fuzzy_ratio": match["logo_similarity"]["fuzzy_ratio"],
                            "partial_ratio": match["logo_similarity"]["partial_ratio"],
                            "token_sort": match["logo_similarity"]["token_sort"],
                            "avg_fuzzy": round(match["logo_similarity"]["avg_fuzzy"], 2)
                        },
                        "overall": round(match["logo_similarity"]["overall_similarity"], 2)
                    }
                }
            }
            report["matches"].append(match_report)
        
        return report 