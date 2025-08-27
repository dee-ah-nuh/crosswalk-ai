/**
 * API service for crosswalk template operations
 */

export interface CrosswalkMapping {
  id: number;
  client_id: string;
  source_column_order: number | null;
  source_column_name: string;
  file_group_name: string;
  mcdm_column_name: string | null;
  in_model: string;
  mcdm_table: string | null;
  custom_field_type: string | null;
  data_profile_info: string | null;
  profile_column_2: string | null;
  profile_column_3: string | null;
  profile_column_4: string | null;
  profile_column_5: string | null;
  profile_column_6: string | null;
  source_column_formatting: string | null;
  skipped_flag: boolean;
  additional_field_1: string | null;
  additional_field_2: string | null;
  additional_field_3: string | null;
  additional_field_4: string | null;
  additional_field_5: string | null;
  additional_field_6: string | null;
  additional_field_7: string | null;
  additional_field_8: string | null;
  created_at: string;
  updated_at: string;
  
  // Feature 1 & 2: Multi-table and provider fields
  target_tables?: string | null;
  provider_file_group?: string | null;
  is_multi_table?: boolean;
  
  // Feature 3: Version control
  crosswalk_version?: string | null;
  parent_mapping_id?: number | null;
  reuse_from_client?: string | null;
  version_notes?: string | null;
  
  // Feature 4: Data type inference
  inferred_data_type?: string | null;
  custom_data_type?: string | null;
  data_type_source?: string | null;
  data_type?: string | null;
  description?: string | null;
  mcdm_table_name?: string | null;
  
  // Feature 5: Multi-file joins
  source_file_name?: string | null;
  join_key_column?: string | null;
  join_table?: string | null;
  join_type?: string | null;
  
  // Feature 7: MCS review
  mcs_review_required?: boolean;
  mcs_review_notes?: string | null;
  mcs_review_status?: string | null;
  mcs_reviewer?: string | null;
  mcs_review_date?: string | null;
  
  // Additional tracking
  complexity_score?: number | null;
  business_priority?: string | null;
  completion_status?: string | null;
}

export interface CrosswalkResponse {
  data: CrosswalkMapping[];
  total: number;
  offset: number;
  limit: number;
}

export interface CrosswalkSummary {
  total_mappings: number;
  total_clients: number;
  total_file_groups: number;
  skipped_fields: number;
  in_model_distribution: Array<{in_model: string; count: number}>;
  file_group_distribution: Array<{file_group: string; count: number}>;
}

export interface Client {
  client_id: string;
  mapping_count: number;
}

export interface FileGroup {
  file_group: string;
  mapping_count: number;
}

const API_BASE_URL = '/api';

class CrosswalkApiService {
  async getCrosswalkMappings(params?: {
    client_id?: string;
    file_group?: string;
    limit?: number;
    offset?: number;
  }): Promise<CrosswalkMapping[]> {
    const urlParams = new URLSearchParams();
    
    if (params?.client_id) urlParams.append('client_id', params.client_id);
    if (params?.file_group) urlParams.append('file_group', params.file_group);
    if (params?.limit) urlParams.append('limit', params.limit.toString());
    if (params?.offset) urlParams.append('offset', params.offset.toString());
    
    const response = await fetch(`${API_BASE_URL}/crosswalk?${urlParams}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.data || data; // Handle both response formats
  }

  async getCrosswalkData(params?: {
    client_id?: string;
    file_group?: string;
    limit?: number;
    offset?: number;
  }): Promise<CrosswalkResponse> {
    const urlParams = new URLSearchParams();
    
    if (params?.client_id) urlParams.append('client_id', params.client_id);
    if (params?.file_group) urlParams.append('file_group', params.file_group);
    if (params?.limit) urlParams.append('limit', params.limit.toString());
    if (params?.offset) urlParams.append('offset', params.offset.toString());
    
    const response = await fetch(`${API_BASE_URL}/crosswalk?${urlParams}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  async updateMapping(id: number, data: Partial<CrosswalkMapping>): Promise<{success: boolean; message: string}> {
    const response = await fetch(`${API_BASE_URL}/crosswalk/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  async getClients(): Promise<Client[]> {
    const response = await fetch(`${API_BASE_URL}/crosswalk/clients`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  async getFileGroups(client_id?: string): Promise<FileGroup[]> {
    const urlParams = new URLSearchParams();
    if (client_id) urlParams.append('client_id', client_id);
    
    const response = await fetch(`${API_BASE_URL}/crosswalk/file-groups?${urlParams}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  async getSummary(): Promise<CrosswalkSummary> {
    const response = await fetch(`${API_BASE_URL}/crosswalk/summary`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  async searchMappings(searchData: {term: string; fields: string[]}): Promise<{data: CrosswalkMapping[]; total: number}> {
    const response = await fetch(`${API_BASE_URL}/crosswalk/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchData),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
  }

  // Feature 6: Snowflake SQL Generation
  async generateSnowflakeSQL(exportData: {
    client_id: string;
    file_group?: string;
    export_type: string;
    table_name: string;
    created_by?: string;
  }): Promise<{sql_content: string; table_name: string; export_type: string; mapping_count: number}> {
    const response = await fetch(`/api/snowflake/generate-sql`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(exportData),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
  }

  async getSnowflakeExports(client_id?: string): Promise<any[]> {
    const urlParams = new URLSearchParams();
    if (client_id) urlParams.append('client_id', client_id);
    
    const response = await fetch(`/api/snowflake/exports?${urlParams}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
  }

  async duplicateMapping(id: number, newTable: string): Promise<{success: boolean; message: string; new_id: number}> {
    const response = await fetch(`${API_BASE_URL}/crosswalk/${id}/duplicate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ mcdm_table: newTable }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
  }
}

export const crosswalkApi = new CrosswalkApiService();