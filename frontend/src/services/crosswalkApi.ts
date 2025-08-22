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
}

export const crosswalkApi = new CrosswalkApiService();