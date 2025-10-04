"""
Automated Data Model Mapping System
====================================

This module provides intelligent mapping suggestions from source columns to data model fields
using a hybrid approach with self-learning capabilities.

Approach:
1. Fuzzy string matching for column names
2. Data pattern analysis for sample values  
3. Learning from user corrections to improve over time
4. Confidence scoring for mapping suggestions
"""
import duckdb
import re
import json
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from fuzzywuzzy import fuzz, process
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class MappingSuggestion:
    """Represents a mapping suggestion with confidence score"""
    source_column: str
    target_column: str
    target_table: str
    confidence: float
    reasoning: str
    data_type: str

@dataclass
class DataModelField:
    """Represents a field in the data model"""
    table: str
    column: str
    description: str
    data_type: str

class AutoMapper:
    """
    Intelligent mapping system that learns from corrections

    Here is where I asked Sarah previously if we had data defintions on the columns 
    themselves. If we do, we can use that to improve the semantic matching.

    We only have a couple. :(
    """
    
    def __init__(self, db_url: str = None):
        self.db_url = db_url or os.getenv('DATABASE_URL')
        self.data_model_fields = []
        self.correction_history = []
        self.pattern_library = {
            'claim_number': [r'^\d{5,20}$', r'^\w{5,15}-\w{3,10}$'],
            'member_id': [r'^\d{8,12}$', r'^[A-Z]{2}\d{6,10}$'],
            'date': [r'^\d{4}-\d{2}-\d{2}$', r'^\d{1,2}/\d{1,2}/\d{4}$'],
            'phone': [r'^\d{10}$', r'^\(\d{3}\)\s?\d{3}-\d{4}$'],
            'amount': [r'^\d+\.\d{2}$', r'^\$?\d+,?\d*\.?\d*$'],
            'zip_code': [r'^\d{5}(-\d{4})?$'],
            'npi': [r'^\d{10}$'],
            'tax_id': [r'^\d{2}-\d{7}$', r'^\d{9}$'],
        }
        self.load_data_model()
        self.load_correction_history()
    
    def load_data_model(self):
        """Load all fields from the data model"""
        try:
                conn = duckdb.connect(self.db_url or 'database/crosswalk.duckdb')
                query = """SELECT IN_CROSSWALK,
                        TABLE_NAME,
                        COLUMN_NAME,
                        COLUMN_TYPE,
                        COLUMN_ORDER,
                        COLUMN_COMMENT,
                        TABLE_CREATION_ORDER,
                        IS_MANDATORY,
                        MANDATORY_PROV_TYPE,
                        MCDM_MASKING_TYPE,
                        IN_EDITS,
                        KEY
                        FROM pi20_data_model
                        ORDER BY TABLE_NAME, COLUMN_ORDER;
                """
                df = pd.read_sql_query(query, conn)
                conn.close()
                self.data_model_fields = [
                DataModelField(
                    table=row['TABLE_NAME'],
                    column=row['COLUMN_NAME'], 
                    description=row['COLUMN_COMMENT'] or '',
                    data_type=row['COLUMN_TYPE']
                )
                for _, row in df.iterrows()
            ]
                print(f"Loaded {len(self.data_model_fields)} data model fields")
        except Exception as e:
            print(f"Error loading data model: {e}")
            self.data_model_fields = []
    
    def load_correction_history(self):
        """Load previous mapping corrections to learn from"""
        try:
                conn = duckdb.connect(self.db_url or 'database/crosswalk.duckdb')
                query = """
                    SELECT source_column,
                           correct_target_table,
                           correct_target_column,
                           incorrect_suggestion
                    FROM mapping_corrections
                """
                df = pd.read_sql_query(query, conn)
                conn.close()
                self.correction_history = df.to_dict('records')
                print(f"Loaded {len(self.correction_history)} correction history records")
        except Exception as e:
            print(f"Error loading correction history: {e}")
            self.correction_history = []
    
    def analyze_data_patterns(self, sample_values: List[str]) -> Dict[str, float]:
        """Analyze sample data to identify patterns"""
        if not sample_values:
            return {}
        
        pattern_scores = {}
        clean_values = [str(v).strip() for v in sample_values if v is not None]
        
        for pattern_type, patterns in self.pattern_library.items():
            matches = 0
            for value in clean_values[:10]:  # Check first 10 values
                for pattern in patterns:
                    if re.match(pattern, str(value)):
                        matches += 1
                        break
            
            if clean_values:
                pattern_scores[pattern_type] = matches / min(len(clean_values), 10)
        
        return pattern_scores
    
    def calculate_string_similarity(self, source_col: str, target_col: str) -> float:
        """Calculate string similarity between column names"""
        # Normalize column names
        source_norm = re.sub(r'[_\s-]+', '', source_col.lower())
        target_norm = re.sub(r'[_\s-]+', '', target_col.lower())
        
        # Use multiple similarity metrics
        ratio = fuzz.ratio(source_norm, target_norm) / 100.0
        partial = fuzz.partial_ratio(source_norm, target_norm) / 100.0
        token_sort = fuzz.token_sort_ratio(source_col.lower(), target_col.lower()) / 100.0
        
        # Weighted average
        return (0.4 * ratio + 0.3 * partial + 0.3 * token_sort)
    
    def get_semantic_similarity(self, source_desc: str, target_desc: str) -> float:
        """Calculate semantic similarity using TF-IDF"""
        if not source_desc or not target_desc:
            return 0.0
        
        try:
            docs = [source_desc.lower(), target_desc.lower()]
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(docs)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return similarity[0][0]
        except:
            return 0.0
    
    def apply_learning_boost(self, source_col: str, target_field: DataModelField) -> float:
        """Apply learning boost based on correction history"""
        boost = 0.0
        
        for correction in self.correction_history:
            # If this exact mapping was corrected as correct before
            if (correction['source_column'].lower() == source_col.lower() and 
                correction['correct_target_table'] == target_field.table and
                correction['correct_target_column'] == target_field.column):
                boost += 0.3
            
            # If similar source column was mapped to this target before
            if (fuzz.ratio(correction['source_column'].lower(), source_col.lower()) > 80 and
                correction['correct_target_table'] == target_field.table and
                correction['correct_target_column'] == target_field.column):
                boost += 0.1
        
        return min(boost, 0.5)  # Cap boost at 0.5
    
    def generate_mapping_suggestions(self, source_column: str, sample_values: List[str] = None) -> List[MappingSuggestion]:
        """Generate ranked mapping suggestions for a source column"""
        suggestions = []
        
        # Analyze data patterns if sample values provided
        pattern_scores = self.analyze_data_patterns(sample_values or [])
        
        for target_field in self.data_model_fields:
            # Calculate different similarity scores
            name_similarity = self.calculate_string_similarity(source_column, target_field.column)
            semantic_similarity = self.get_semantic_similarity(source_column, target_field.description)
            learning_boost = self.apply_learning_boost(source_column, target_field)
            
            # Pattern matching boost
            pattern_boost = 0.0
            field_name_lower = target_field.column.lower()
            for pattern_type, score in pattern_scores.items():
                if pattern_type in field_name_lower or any(keyword in field_name_lower for keyword in pattern_type.split('_')):
                    pattern_boost += score * 0.2
            
            # Calculate final confidence score
            confidence = (
                0.4 * name_similarity +      # Column name similarity
                0.2 * semantic_similarity +  # Description similarity  
                0.2 * pattern_boost +        # Data pattern match
                0.2 * learning_boost         # Learning from corrections
            )
            
            # Generate reasoning
            reasoning_parts = []
            if name_similarity > 0.6:
                reasoning_parts.append(f"Column name match ({name_similarity:.0%})")
            if pattern_boost > 0.1:
                best_pattern = max(pattern_scores.items(), key=lambda x: x[1])[0] if pattern_scores else None
                if best_pattern:
                    reasoning_parts.append(f"Data pattern suggests {best_pattern}")
            if learning_boost > 0.1:
                reasoning_parts.append("Previously learned mapping")
            if semantic_similarity > 0.3:
                reasoning_parts.append("Description similarity")
            
            reasoning = " • ".join(reasoning_parts) if reasoning_parts else "Basic similarity match"
            
            if confidence > 0.1:  # Only include suggestions with reasonable confidence
                suggestions.append(MappingSuggestion(
                    source_column=source_column,
                    target_column=target_field.column,
                    target_table=target_field.table,
                    confidence=confidence,
                    reasoning=reasoning,
                    data_type=target_field.data_type
                ))
        
        # Sort by confidence and return top 5
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        return suggestions[:5]
    
    def record_correction(self, source_column: str, correct_table: str, correct_column: str, incorrect_suggestion: str = None):
        """Record a user correction to improve future suggestions"""
        try:
                conn = duckdb.connect(self.db_url or 'backend/database/crosswalk.duckdb')
                query = """
                    INSERT INTO mapping_corrections 
                    (source_column, correct_target_table, correct_target_column, incorrect_suggestion)
                    VALUES (?, ?, ?, ?)
                """
                conn.execute(query, [source_column, correct_table, correct_column, incorrect_suggestion or ''])
                conn.commit()
                conn.close()
                # Reload correction history
                self.load_correction_history()
                print(f"Recorded correction: {source_column} -> {correct_table}.{correct_column}")
        except Exception as e:
            print(f"Error recording correction: {e}")
    
    def bulk_suggest_mappings(self, source_columns: List[Dict]) -> Dict[str, List[MappingSuggestion]]:
        """Generate suggestions for multiple source columns"""
        results = {}
        
        for col_info in source_columns:
            source_col = col_info.get('column_name', '')
            sample_values = col_info.get('sample_values', [])
            
            if source_col:
                suggestions = self.generate_mapping_suggestions(source_col, sample_values)
                results[source_col] = suggestions
        
        return results

