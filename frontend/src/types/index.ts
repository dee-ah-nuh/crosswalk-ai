export interface Profile {
  id: number;
  name: string;
  client_id: string | null;
  created_at: string | null;
  has_physical_file: boolean;
  raw_table_name: string | null;
}

export interface DataModelField {
  id: number;
  column: string;
  description: string | null;
  data_type: string | null;
  required: boolean;
  unique_key: boolean;
}

export interface DataModelTable {
  [tableName: string]: DataModelField[];
}

export interface SourceColumn {
  id: number;
  source_column: string;
  sample_values: string[];
  inferred_type: string;
}

export interface RegexRule {
  id: number;
  rule_name: string | null;
  pattern: string;
  flags: string | null;
  description: string | null;
}

export interface CrosswalkMapping {
  source_column_id: number;
  source_column: string;
  sample_values: string[];
  inferred_type: string;
  model_table: string;
  model_column: string;
  is_custom_field: boolean;
  custom_field_name: string | null;
  transform_expression: string | null;
  notes: string | null;
  is_mapped: boolean;
  regex_rules: RegexRule[];
}

export interface ValidationSummary {
  total_columns: number;
  mapped_columns: number;
  unmapped_columns: number;
  mapping_percentage: number;
  regex_pass_count: number;
  regex_fail_count: number;
}

export interface RegexTestResult {
  matches: boolean;
  groups: string[];
  full_match: string;
  error?: string;
}

export interface DSLValidationResult {
  valid: boolean;
  message: string;
}

export interface DSLTranslationResult {
  success: boolean;
  sql_expression?: string;
  error?: string;
}

export interface WarehouseSampleResult {
  success: boolean;
  row_count: number;
  data: Record<string, any>[];
}

export interface ExportFormat {
  id: 'csv' | 'xlsx' | 'json' | 'sql';
  name: string;
  description: string;
  icon: string;
  color: string;
}

export interface ApiError {
  detail: string;
}

export interface FileUploadResult {
  message: string;
  columns_count: number;
  columns: string[];
}

export interface SchemaImportResult {
  message: string;
  columns_count: number;
  columns: string[];
}

export interface JSONExportConfig {
  client_id: string;
  profile: string;
  mappings: {
    source_column: string;
    target: {
      table: string;
      column: string;
    };
    custom: boolean;
    custom_field_name?: string;
    transform: string;
    regex_rules: {
      name: string;
      pattern: string;
      flags?: string;
      description?: string;
    }[];
  }[];
}

// Form types
export interface CreateProfileForm {
  name: string;
  client_id: string;
}

export interface RegexRuleForm {
  rule_name: string;
  pattern: string;
  flags: string;
  description: string;
}

// Hook return types
export interface UseProfilesReturn {
  profiles: Profile[];
  loading: boolean;
  error: string | null;
  createProfile: (name: string, clientId: string) => Promise<void>;
  refreshProfiles: () => Promise<void>;
}

export interface UseCrosswalkReturn {
  mappings: CrosswalkMapping[];
  loading: boolean;
  error: string | null;
  validationSummary: ValidationSummary | null;
  updateMappings: (mappings: CrosswalkMapping[]) => Promise<void>;
  refreshMappings: () => Promise<void>;
}

// API response types
export interface ApiResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}
