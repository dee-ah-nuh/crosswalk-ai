/**
 * Data Model API Service - Provides PI20 data model intelligence and validation
 */

const API_BASE_URL = '/api/datamodel';

export interface DataModelField {
  schema_layer: string;
  table_name: string;
  column_name: string;
  data_type: string;
  description: string;
  is_standard_field: boolean;
  is_case_sensitive: boolean;
}

export interface ValidationResult {
  is_valid: boolean;
  rule_violations: Array<{
    rule: string;
    message: string;
    field: string;
  }>;
  suggestions: string[];
}

export interface FieldSuggestion {
  column_name: string;
  table_name: string;
  schema_layer: string;
  confidence_score: number;
  reason: string;
}

export interface FieldInfo {
  schema_layer: string;
  table_name: string;
  column_name: string;
  data_type: string;
  description: string;
  is_standard_field: boolean;
  is_case_sensitive: boolean;
}

class DataModelApiService {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get PI20 data model fields with optional filtering
   */
  async getFields(filters: {
    schema_layer?: string;
    table_name?: string;
    search?: string;
  } = {}): Promise<DataModelField[]> {
    const params = new URLSearchParams();
    
    if (filters.schema_layer) params.append('schema_layer', filters.schema_layer);
    if (filters.table_name) params.append('table_name', filters.table_name);
    if (filters.search) params.append('search', filters.search);
    
    const queryString = params.toString();
    const endpoint = queryString ? `/fields?${queryString}` : '/fields';
    
    return this.request<DataModelField[]>(endpoint);
  }

  /**
   * Get intelligent field suggestions for a source column
   */
  async suggestMapping(
    sourceColumn: string,
    fileGroup?: string
  ): Promise<FieldSuggestion[]> {
    const params = new URLSearchParams({ source_column: sourceColumn });
    if (fileGroup) params.append('file_group', fileGroup);
    
    return this.request<FieldSuggestion[]>(`/suggest-mapping?${params.toString()}`);
  }

  /**
   * Validate a crosswalk mapping against PI20 data model rules
   */
  async validateMapping(mappingData: any): Promise<ValidationResult> {
    return this.request<ValidationResult>('/validate-mapping', {
      method: 'POST',
      body: JSON.stringify(mappingData),
    });
  }

  /**
   * Get available schema layers (RAW, CLEANSE, CURATED)
   */
  async getSchemaLayers(): Promise<string[]> {
    return this.request<string[]>('/schema-layers');
  }

  /**
   * Get available tables in the data model
   */
  async getTables(schemaLayer?: string): Promise<string[]> {
    const params = schemaLayer ? `?schema_layer=${schemaLayer}` : '';
    return this.request<string[]>(`/tables${params}`);
  }

  /**
   * Get detailed information about a specific field
   */
  async getFieldInfo(columnName: string): Promise<FieldInfo[]> {
    return this.request<FieldInfo[]>(`/field-info/${encodeURIComponent(columnName)}`);
  }

  /**
   * Get MCDM column suggestions for autocomplete
   */
  async getMcdmColumns(search: string = ''): Promise<string[]> {
    const fields = await this.getFields({ search });
    return Array.from(new Set(fields.map(f => f.column_name))).sort();
  }

  /**
   * Check if a field requires case sensitivity handling
   */
  async requiresCaseSensitivity(columnName: string): Promise<boolean> {
    try {
      const fieldInfo = await this.getFieldInfo(columnName);
      return fieldInfo.some(field => field.is_case_sensitive);
    } catch {
      return false;
    }
  }

  /**
   * Get smart formatting suggestions for a column
   */
  async getFormattingSuggestions(
    sourceColumn: string,
    targetColumn: string
  ): Promise<string[]> {
    const suggestions: string[] = [];
    
    try {
      const requiresCase = await this.requiresCaseSensitivity(targetColumn);
      
      if (requiresCase) {
        suggestions.push(`UPPER(${sourceColumn})`);
        suggestions.push(`LOWER(${sourceColumn})`);
      }
      
      // Common transformation patterns
      if (sourceColumn.toLowerCase().includes('date')) {
        suggestions.push(`TO_DATE(${sourceColumn}, 'YYYY-MM-DD')`);
        suggestions.push(`${sourceColumn}::DATE`);
      }
      
      if (sourceColumn.toLowerCase().includes('amount') || 
          sourceColumn.toLowerCase().includes('cost')) {
        suggestions.push(`${sourceColumn}::DECIMAL(10,2)`);
        suggestions.push(`ROUND(${sourceColumn}, 2)`);
      }
      
      if (targetColumn.toLowerCase().includes('sid')) {
        suggestions.push(`${sourceColumn}::BIGINT`);
      }
      
    } catch (error) {
      console.error('Error getting formatting suggestions:', error);
    }
    
    return suggestions;
  }

  /**
   * Validate IN_MODEL rules
   */
  getInModelValidation(inModel: string, mcdmColumn: string): {
    isValid: boolean;
    message?: string;
    suggestions: string[];
  } {
    const suggestions: string[] = [];
    
    if (inModel === 'Y' && !mcdmColumn.trim()) {
      return {
        isValid: false,
        message: 'Fields with IN_MODEL=Y must have an MCDM column name',
        suggestions: ['Select a target column from the PI20 data model']
      };
    }
    
    if (inModel === 'N') {
      suggestions.push('Custom field - will only appear in CLEANSE schema');
    }
    
    if (inModel === 'U') {
      suggestions.push('Under review - field mapping needs validation');
    }
    
    if (inModel === 'N/A') {
      suggestions.push('Field will be skipped in processing');
    }
    
    return {
      isValid: true,
      suggestions
    };
  }
}

// Export singleton instance
export const dataModelApi = new DataModelApiService();