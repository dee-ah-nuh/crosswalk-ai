import { ApiError } from '../types';

const API_BASE_URL = '/api';

class ApiService {
  private async handleResponse(response: Response) {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        detail: `HTTP ${response.status}: ${response.statusText}`
      }));
      throw new Error(errorData.detail || 'An error occurred');
    }

    // Handle empty responses (like 204 No Content)
    if (response.status === 204 || response.headers.get('content-length') === '0') {
      return {};
    }

    return response.json();
  }

  async get(endpoint: string, params?: Record<string, string>) {
    let url: string;
    const fullPath = `${API_BASE_URL}${endpoint}`;
    
    if (params) {
      const urlObj = new URL(fullPath, window.location.origin);
      Object.entries(params).forEach(([key, value]) => {
        urlObj.searchParams.append(key, value);
      });
      url = urlObj.toString();
    } else {
      url = fullPath;
    }

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    return this.handleResponse(response);
  }

  async post(endpoint: string, data?: any) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: data ? JSON.stringify(data) : undefined,
    });

    return this.handleResponse(response);
  }

  async postFormData(endpoint: string, formData: FormData) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      body: formData, // Don't set Content-Type header for FormData
    });

    return this.handleResponse(response);
  }

  async put(endpoint: string, data?: any) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: data ? JSON.stringify(data) : undefined,
    });

    return this.handleResponse(response);
  }

  async delete(endpoint: string) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    return this.handleResponse(response);
  }

  // Profiles
  async createProfile(name: string, clientId: string) {
    const formData = new FormData();
    formData.append('name', name);
    formData.append('client_id', clientId);
    
    return this.postFormData('/profiles', formData);
  }

  async getProfiles() {
    return this.get('/profiles');
  }

  async getProfile(profileId: number) {
    return this.get(`/profiles/${profileId}`);
  }

  async uploadFile(profileId: number, file: File) {
    const formData = new FormData();
    formData.append('file', file);
    
    return this.postFormData(`/profiles/${profileId}/source/ingest-file`, formData);
  }

  async importSchema(profileId: number, columns: string[]) {
    return this.post(`/profiles/${profileId}/source/ingest-schema`, { columns });
  }

  async getSourceColumns(profileId: number) {
    return this.get(`/profiles/${profileId}/source-columns`);
  }

  async updateRawTableName(profileId: number, tableName: string) {
    return this.put(`/profiles/${profileId}/raw-table-name`, { 
      raw_table_name: tableName 
    });
  }

  // Data Model
  async getDataModelFields() {
    return this.get('/data-model-fields');
  }

  // Crosswalk
  async getCrosswalkMappings(profileId: number) {
    return this.get(`/profiles/${profileId}/crosswalk`);
  }

  async updateCrosswalkMappings(profileId: number, mappings: any[]) {
    return this.put(`/profiles/${profileId}/crosswalk`, mappings);
  }

  async getValidationSummary(profileId: number) {
    return this.get(`/profiles/${profileId}/validation-summary`);
  }

  // Regex
  async createRegexRule(sourceColumnId: number, ruleData: any) {
    return this.post(`/source-columns/${sourceColumnId}/regex`, ruleData);
  }

  async deleteRegexRule(ruleId: number) {
    return this.delete(`/regex-rules/${ruleId}`);
  }

  async testRegex(sourceColumnId: number, pattern: string, value: string, flags?: string) {
    const params: Record<string, string> = {
      pattern,
      value,
    };
    
    if (flags) {
      params.flags = flags;
    }

    return this.get(`/source-columns/${sourceColumnId}/regex/test`, params);
  }

  // DSL
  async validateDSL(expression: string) {
    return this.post('/dsl/validate', { expression });
  }

  async translateDSL(expression: string, columnMapping?: Record<string, string>) {
    return this.post('/dsl/translate', { expression, column_mapping: columnMapping });
  }

  // Warehouse
  async fetchWarehouseSample(profileId: number) {
    return this.post(`/profiles/${profileId}/sample/fetch`);
  }

  // Export
  async exportCSV(profileId: number): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/profiles/${profileId}/export/csv`);
    if (!response.ok) {
      throw new Error('Export failed');
    }
    return response.blob();
  }

  async exportExcel(profileId: number): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/profiles/${profileId}/export/xlsx`);
    if (!response.ok) {
      throw new Error('Export failed');
    }
    return response.blob();
  }

  async exportJSON(profileId: number): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/profiles/${profileId}/export/json`);
    if (!response.ok) {
      throw new Error('Export failed');
    }
    return response.blob();
  }

  async exportSQL(profileId: number): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/profiles/${profileId}/export/sql`);
    if (!response.ok) {
      throw new Error('Export failed');
    }
    return response.blob();
  }

  // Health check
  async healthCheck() {
    return this.get('/health');
  }
}

export const api = new ApiService();
