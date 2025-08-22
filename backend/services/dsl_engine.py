"""
DSL (Domain Specific Language) engine for transform expressions.
"""

import re
from typing import Any, Dict, List
from dataclasses import dataclass

@dataclass
class DSLFunction:
    name: str
    args: List[Any]

class DSLEngine:
    """Simple DSL engine for transform expressions"""
    
    FUNCTION_PATTERNS = {
        'upper': r'upper\(([^)]+)\)',
        'lower': r'lower\(([^)]+)\)',
        'trim': r'trim\(([^)]+)\)',
        'substr': r'substr\(([^,]+),\s*(\d+),\s*(\d+)\)',
        'coalesce': r'coalesce\(([^)]+)\)',
        'regex_extract': r'regex_extract\(([^,]+),\s*[\'"]([^\'\"]+)[\'"],\s*(\d+)\)',
        'regex_replace': r'regex_replace\(([^,]+),\s*[\'"]([^\'\"]+)[\'"],\s*[\'"]([^\'\"]*)[\'\"]\)',
        'col': r'col\([\'"]([^\'\"]+)[\'"]\)',
        'if': r'if\(([^,]+),\s*([^,]+),\s*([^)]+)\)',
        'matches': r'matches\(([^,]+),\s*[\'"]([^\'\"]+)[\'\"]\)',
        'is_null': r'is_null\(([^)]+)\)'
    }
    
    @classmethod
    def validate_expression(cls, expression: str) -> Dict[str, Any]:
        """
        Validate a DSL expression and return validation result.
        """
        try:
            # Basic syntax validation
            if not expression.strip():
                return {"valid": True, "message": "Empty expression"}
            
            # Check for balanced parentheses
            if not cls._check_balanced_parentheses(expression):
                return {"valid": False, "message": "Unbalanced parentheses"}
            
            # Check for valid function calls
            functions_found = cls._extract_functions(expression)
            invalid_functions = []
            
            for func_call in functions_found:
                if not cls._validate_function_call(func_call):
                    invalid_functions.append(func_call)
            
            if invalid_functions:
                return {
                    "valid": False, 
                    "message": f"Invalid function calls: {', '.join(invalid_functions)}"
                }
            
            return {"valid": True, "message": "Valid expression"}
            
        except Exception as e:
            return {"valid": False, "message": f"Validation error: {str(e)}"}
    
    @classmethod
    def translate_to_sql(cls, expression: str, column_mapping: Dict[str, str] = None) -> str:
        """
        Translate DSL expression to SQL.
        
        Args:
            expression: DSL expression to translate
            column_mapping: Optional mapping of source columns to SQL column references
        """
        if not expression.strip():
            return "NULL"
        
        sql_expr = expression
        
        # Replace DSL functions with SQL equivalents
        replacements = {
            r'upper\(([^)]+)\)': r'UPPER(\1)',
            r'lower\(([^)]+)\)': r'LOWER(\1)',
            r'trim\(([^)]+)\)': r'TRIM(\1)',
            r'substr\(([^,]+),\s*(\d+),\s*(\d+)\)': r'SUBSTR(\1, \2, \3)',
            r'coalesce\(([^)]+)\)': r'COALESCE(\1)',
            r'regex_extract\(([^,]+),\s*[\'"]([^\'\"]+)[\'"],\s*(\d+)\)': r'REGEXP_SUBSTR(\1, \'\2\')',
            r'regex_replace\(([^,]+),\s*[\'"]([^\'\"]+)[\'"],\s*[\'"]([^\'\"]*)[\'\"]\)': r'REGEXP_REPLACE(\1, \'\2\', \'\3\')',
            r'if\(([^,]+),\s*([^,]+),\s*([^)]+)\)': r'CASE WHEN \1 THEN \2 ELSE \3 END',
            r'matches\(([^,]+),\s*[\'"]([^\'\"]+)[\'\"]\)': r'REGEXP_LIKE(\1, \'\2\')',
            r'is_null\(([^)]+)\)': r'(\1 IS NULL)',
        }
        
        for pattern, replacement in replacements.items():
            sql_expr = re.sub(pattern, replacement, sql_expr, flags=re.IGNORECASE)
        
        # Replace column references
        if column_mapping:
            for source_col, sql_ref in column_mapping.items():
                col_pattern = rf'col\([\'\"]{re.escape(source_col)}[\'\"]\)'
                sql_expr = re.sub(col_pattern, sql_ref, sql_expr, flags=re.IGNORECASE)
        else:
            # Default column reference replacement
            sql_expr = re.sub(r'col\([\'"]([^\'\"]+)[\'"]\)', r'\1', sql_expr, flags=re.IGNORECASE)
        
        return sql_expr
    
    @classmethod
    def _check_balanced_parentheses(cls, expression: str) -> bool:
        """Check if parentheses are balanced in the expression"""
        count = 0
        for char in expression:
            if char == '(':
                count += 1
            elif char == ')':
                count -= 1
                if count < 0:
                    return False
        return count == 0
    
    @classmethod
    def _extract_functions(cls, expression: str) -> List[str]:
        """Extract function calls from expression"""
        functions = []
        for func_name, pattern in cls.FUNCTION_PATTERNS.items():
            matches = re.findall(f'{func_name}\\([^)]*\\)', expression, re.IGNORECASE)
            functions.extend(matches)
        return functions
    
    @classmethod
    def _validate_function_call(cls, func_call: str) -> bool:
        """Validate a specific function call"""
        for func_name, pattern in cls.FUNCTION_PATTERNS.items():
            if func_call.lower().startswith(func_name.lower()):
                return bool(re.match(pattern, func_call, re.IGNORECASE))
        return False
