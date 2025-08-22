/**
 * API service for intelligent automated mapping suggestions
 */

export interface MappingSuggestion {
  source_column: string;
  target_column: string;
  target_table: string;
  confidence: number;
  reasoning: string;
  data_type: string;
}

export interface SourceColumn {
  column_name: string;
  sample_values?: string[];
  column_order?: number;
}

export interface AutoMappingStats {
  data_model_fields: number;
  corrections_learned: number;
  pattern_types: number;
  status: string;
}

class AutoMappingService {
  private baseURL = '/api/auto-mapping';

  /**
   * Get intelligent mapping suggestions for source columns
   */
  async getSuggestions(sourceColumns: SourceColumn[]): Promise<Record<string, MappingSuggestion[]>> {
    try {
      const response = await fetch(`${this.baseURL}/suggest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          source_columns: sourceColumns
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('📊 Auto-mapping suggestions:', data);
      return data;
    } catch (error) {
      console.error('❌ Error getting mapping suggestions:', error);
      throw error;
    }
  }

  /**
   * Get suggestions for a single column
   */
  async getSingleSuggestion(columnName: string, sampleValues?: string[]): Promise<MappingSuggestion[]> {
    try {
      const response = await fetch(`${this.baseURL}/suggest-single?column_name=${encodeURIComponent(columnName)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(sampleValues || []),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log(`🤖 Suggestions for '${columnName}':`, data);
      return data;
    } catch (error) {
      console.error(`❌ Error getting suggestions for '${columnName}':`, error);
      throw error;
    }
  }

  /**
   * Record a mapping correction to improve future suggestions
   */
  async recordCorrection(
    sourceColumn: string,
    correctTable: string,
    correctColumn: string,
    incorrectSuggestion?: string
  ): Promise<void> {
    try {
      const response = await fetch(`${this.baseURL}/correct`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          source_column: sourceColumn,
          correct_table: correctTable,
          correct_column: correctColumn,
          incorrect_suggestion: incorrectSuggestion
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ Learning from correction:', data.message);
    } catch (error) {
      console.error('❌ Error recording correction:', error);
      throw error;
    }
  }

  /**
   * Get statistics about the auto-mapping system
   */
  async getStats(): Promise<AutoMappingStats> {
    try {
      const response = await fetch(`${this.baseURL}/stats`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('📈 Auto-mapping stats:', data);
      return data;
    } catch (error) {
      console.error('❌ Error getting auto-mapping stats:', error);
      throw error;
    }
  }
}

export const autoMappingService = new AutoMappingService();