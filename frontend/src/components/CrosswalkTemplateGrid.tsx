import React, { useState, useEffect, useMemo } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
  ColumnDef,
  getSortedRowModel,
  SortingState,
  getFilteredRowModel,
  ColumnFiltersState,
} from '@tanstack/react-table';
import { crosswalkApi, CrosswalkMapping } from '../services/crosswalkApi';
import { dataModelApi, ValidationResult, FieldSuggestion } from '../services/dataModelApi';

interface CrosswalkTemplateGridProps {
  clientId?: string;
  fileGroup?: string;
}

const CrosswalkTemplateGrid: React.FC<CrosswalkTemplateGridProps> = ({ 
  clientId, 
  fileGroup 
}) => {
  const [data, setData] = useState<CrosswalkMapping[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [selectedMapping, setSelectedMapping] = useState<CrosswalkMapping | null>(null);
  const [viewMode, setViewMode] = useState<'table' | 'cards'>('cards');
  const [searchTerm, setSearchTerm] = useState('');

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await crosswalkApi.getCrosswalkData({
          client_id: clientId,
          file_group: fileGroup,
          limit: 500
        });
        setData(response.data);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch crosswalk data');
        console.error('Error fetching crosswalk data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [clientId, fileGroup]);

  // Update mapping
  const updateMapping = async (id: number, updates: Partial<CrosswalkMapping>) => {
    try {
      await crosswalkApi.updateMapping(id, updates);
      setData(prev => prev.map(item => 
        item.id === id ? { ...item, ...updates } : item
      ));
    } catch (err: any) {
      console.error('Error updating mapping:', err);
      alert('Failed to update mapping: ' + (err.message || 'Unknown error'));
    }
  };

  // Filter data based on search
  const filteredData = useMemo(() => {
    if (!searchTerm) return data;
    return data.filter(mapping => 
      mapping.source_column_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      mapping.mcdm_column_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      mapping.file_group_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      mapping.data_profile_info?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [data, searchTerm]);

  // Get status info for a mapping
  const getStatusInfo = (mapping: CrosswalkMapping) => {
    const inModel = mapping.in_model?.toUpperCase();
    const hasMcdm = mapping.mcdm_column_name?.trim();
    const isSkipped = mapping.skipped_flag;

    if (isSkipped) {
      return { status: 'skipped', color: 'gray', text: 'Skipped' };
    }
    if (inModel === 'Y' && hasMcdm) {
      return { status: 'mapped', color: 'green', text: 'Mapped' };
    }
    if (inModel === 'Y' && !hasMcdm) {
      return { status: 'incomplete', color: 'red', text: 'Needs MCDM Column' };
    }
    if (inModel === 'N') {
      return { status: 'custom', color: 'blue', text: 'Custom Field' };
    }
    if (inModel === 'U') {
      return { status: 'review', color: 'yellow', text: 'Under Review' };
    }
    return { status: 'pending', color: 'gray', text: 'Pending' };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="text-gray-600">Loading crosswalk data...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <i className="fas fa-exclamation-triangle text-red-500 text-4xl mb-4"></i>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Data</h3>
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex bg-gray-50">
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Enhanced Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Crosswalk Template
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                {filteredData.length} mappings
                {clientId && ` • Client: ${clientId}`}
                {fileGroup && ` • File Group: ${fileGroup}`}
              </p>
            </div>
            
            {/* View Mode Toggle */}
            <div className="flex items-center space-x-3">
              <div className="flex rounded-lg border border-gray-300">
                <button
                  onClick={() => setViewMode('cards')}
                  className={`px-3 py-1.5 text-sm font-medium rounded-l-lg ${
                    viewMode === 'cards'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <i className="fas fa-th-large mr-1.5"></i>
                  Cards
                </button>
                <button
                  onClick={() => setViewMode('table')}
                  className={`px-3 py-1.5 text-sm font-medium rounded-r-lg border-l ${
                    viewMode === 'table'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <i className="fas fa-table mr-1.5"></i>
                  Table
                </button>
              </div>
            </div>
          </div>

          {/* Search and Filters */}
          <div className="flex items-center space-x-4">
            <div className="flex-1 max-w-md">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search columns, mappings, or descriptions..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <i className="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
              </div>
            </div>
            
            <div className="flex items-center space-x-2 text-sm">
              <span className="text-gray-500">Status:</span>
              <div className="flex items-center space-x-3">
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-green-400 rounded-full mr-1.5"></div>
                  <span className="text-gray-600">Mapped ({filteredData.filter(m => getStatusInfo(m).status === 'mapped').length})</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-red-400 rounded-full mr-1.5"></div>
                  <span className="text-gray-600">Incomplete ({filteredData.filter(m => getStatusInfo(m).status === 'incomplete').length})</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-blue-400 rounded-full mr-1.5"></div>
                  <span className="text-gray-600">Custom ({filteredData.filter(m => getStatusInfo(m).status === 'custom').length})</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden">
          {viewMode === 'cards' ? (
            <CardsView 
              data={filteredData} 
              onUpdateMapping={updateMapping}
              onSelectMapping={setSelectedMapping}
              selectedMapping={selectedMapping}
              getStatusInfo={getStatusInfo}
            />
          ) : (
            <TableView 
              data={filteredData} 
              onUpdateMapping={updateMapping}
              onSelectMapping={setSelectedMapping}
              selectedMapping={selectedMapping}
              getStatusInfo={getStatusInfo}
            />
          )}
        </div>
      </div>

      {/* Detail Panel */}
      {selectedMapping && (
        <DetailPanel
          mapping={selectedMapping}
          onUpdateMapping={(updates) => updateMapping(selectedMapping.id, updates)}
          onClose={() => setSelectedMapping(null)}
        />
      )}
    </div>
  );
};

// Cards View Component
const CardsView: React.FC<{
  data: CrosswalkMapping[];
  onUpdateMapping: (id: number, updates: Partial<CrosswalkMapping>) => void;
  onSelectMapping: (mapping: CrosswalkMapping) => void;
  selectedMapping: CrosswalkMapping | null;
  getStatusInfo: (mapping: CrosswalkMapping) => any;
}> = ({ data, onUpdateMapping, onSelectMapping, selectedMapping, getStatusInfo }) => {
  return (
    <div className="h-full overflow-auto p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {data.map((mapping) => {
          const status = getStatusInfo(mapping);
          const isSelected = selectedMapping?.id === mapping.id;
          
          return (
            <div
              key={mapping.id}
              onClick={() => onSelectMapping(mapping)}
              className={`bg-white rounded-lg shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer border-2 ${
                isSelected ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200'
              }`}
            >
              {/* Card Header */}
              <div className="p-4 border-b border-gray-100">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-gray-900 text-sm leading-tight">
                    {mapping.source_column_name || 'Untitled Column'}
                  </h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    status.status === 'mapped' ? 'bg-green-100 text-green-700' :
                    status.status === 'incomplete' ? 'bg-red-100 text-red-700' :
                    status.status === 'custom' ? 'bg-blue-100 text-blue-700' :
                    status.status === 'review' ? 'bg-yellow-100 text-yellow-700' :
                    status.status === 'skipped' ? 'bg-gray-100 text-gray-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {status.text}
                  </span>
                </div>
                
                {mapping.file_group_name && (
                  <span className={`inline-flex px-2 py-1 rounded text-xs font-medium ${
                    mapping.file_group_name === 'CLAIM' ? 'bg-blue-50 text-blue-700' :
                    mapping.file_group_name === 'CLAIM_LINE' ? 'bg-green-50 text-green-700' :
                    mapping.file_group_name === 'MEMBER' ? 'bg-purple-50 text-purple-700' :
                    mapping.file_group_name === 'PROVIDER' ? 'bg-orange-50 text-orange-700' :
                    'bg-gray-50 text-gray-700'
                  }`}>
                    {mapping.file_group_name}
                  </span>
                )}
              </div>

              {/* Card Body */}
              <div className="p-4 space-y-3">
                {mapping.mcdm_column_name && (
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Target Column</label>
                    <p className="text-sm font-medium text-blue-600 mt-1">{mapping.mcdm_column_name}</p>
                  </div>
                )}
                
                {mapping.mcdm_table && (
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Table</label>
                    <p className="text-sm text-gray-900 mt-1">{mapping.mcdm_table}</p>
                  </div>
                )}
                
                {mapping.source_column_formatting && (
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Formatting</label>
                    <p className="text-sm font-mono text-gray-700 mt-1 bg-gray-50 px-2 py-1 rounded">
                      {mapping.source_column_formatting.length > 30 
                        ? `${mapping.source_column_formatting.substring(0, 30)}...`
                        : mapping.source_column_formatting
                      }
                    </p>
                  </div>
                )}

                {mapping.data_profile_info && (
                  <div>
                    <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Profile Info</label>
                    <p className="text-sm text-gray-600 mt-1">
                      {mapping.data_profile_info.length > 60 
                        ? `${mapping.data_profile_info.substring(0, 60)}...`
                        : mapping.data_profile_info
                      }
                    </p>
                  </div>
                )}
              </div>

              {/* Card Footer */}
              <div className="px-4 py-3 bg-gray-50 rounded-b-lg border-t border-gray-100">
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Order: {mapping.source_column_order || 'N/A'}</span>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-0.5 rounded font-medium ${
                      mapping.in_model === 'Y' ? 'bg-green-100 text-green-700' :
                      mapping.in_model === 'N' ? 'bg-red-100 text-red-700' :
                      mapping.in_model === 'U' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {mapping.in_model || 'Y'}
                    </span>
                    {mapping.skipped_flag && (
                      <i className="fas fa-ban text-red-400" title="Skipped"></i>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Table View Component (simplified for now)
const TableView: React.FC<{
  data: CrosswalkMapping[];
  onUpdateMapping: (id: number, updates: Partial<CrosswalkMapping>) => void;
  onSelectMapping: (mapping: CrosswalkMapping) => void;
  selectedMapping: CrosswalkMapping | null;
  getStatusInfo: (mapping: CrosswalkMapping) => any;
}> = ({ data, onUpdateMapping, onSelectMapping, selectedMapping, getStatusInfo }) => {
  return (
    <div className="h-full overflow-auto">
      <div className="min-w-full bg-white">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50 sticky top-0">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Source Column</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">File Group</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">MCDM Column</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Table</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.map((mapping) => {
              const status = getStatusInfo(mapping);
              const isSelected = selectedMapping?.id === mapping.id;
              
              return (
                <tr 
                  key={mapping.id} 
                  className={`hover:bg-gray-50 cursor-pointer ${isSelected ? 'bg-blue-50' : ''}`}
                  onClick={() => onSelectMapping(mapping)}
                >
                  <td className="px-4 py-4 whitespace-nowrap">
                    <div className="font-medium text-gray-900">{mapping.source_column_name || 'Untitled'}</div>
                    <div className="text-sm text-gray-500">Order: {mapping.source_column_order || 'N/A'}</div>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                      mapping.file_group_name === 'CLAIM' ? 'bg-blue-100 text-blue-800' :
                      mapping.file_group_name === 'CLAIM_LINE' ? 'bg-green-100 text-green-800' :
                      mapping.file_group_name === 'MEMBER' ? 'bg-purple-100 text-purple-800' :
                      mapping.file_group_name === 'PROVIDER' ? 'bg-orange-100 text-orange-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {mapping.file_group_name || 'N/A'}
                    </span>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-blue-600">{mapping.mcdm_column_name || 'Not mapped'}</div>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                    {mapping.mcdm_table || 'N/A'}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                      status.status === 'mapped' ? 'bg-green-100 text-green-800' :
                      status.status === 'incomplete' ? 'bg-red-100 text-red-800' :
                      status.status === 'custom' ? 'bg-blue-100 text-blue-800' :
                      status.status === 'review' ? 'bg-yellow-100 text-yellow-800' :
                      status.status === 'skipped' ? 'bg-gray-100 text-gray-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {status.text}
                    </span>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm font-medium">
                    <button className="text-blue-600 hover:text-blue-900">Edit</button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Detail Panel Component
const DetailPanel: React.FC<{
  mapping: CrosswalkMapping;
  onUpdateMapping: (updates: Partial<CrosswalkMapping>) => void;
  onClose: () => void;
}> = ({ mapping, onUpdateMapping, onClose }) => {
  const [formData, setFormData] = useState(mapping);
  const [suggestions, setSuggestions] = useState<FieldSuggestion[]>([]);

  useEffect(() => {
    setFormData(mapping);
  }, [mapping]);

  const handleSave = () => {
    onUpdateMapping(formData);
    onClose();
  };

  const getSuggestions = async () => {
    if (formData.source_column_name) {
      try {
        const result = await dataModelApi.suggestMapping(formData.source_column_name, formData.file_group_name);
        setSuggestions(result);
      } catch (error) {
        console.error('Error getting suggestions:', error);
      }
    }
  };

  return (
    <div className="w-96 bg-white border-l border-gray-200 flex flex-col">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900">Edit Mapping</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <i className="fas fa-times"></i>
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6 space-y-6">
        {/* Source Column */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Source Column Name
          </label>
          <input
            type="text"
            value={formData.source_column_name || ''}
            onChange={(e) => setFormData({ ...formData, source_column_name: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* File Group */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            File Group
          </label>
          <select
            value={formData.file_group_name || ''}
            onChange={(e) => setFormData({ ...formData, file_group_name: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Select file group...</option>
            <option value="CLAIM">CLAIM</option>
            <option value="CLAIM_LINE">CLAIM_LINE</option>
            <option value="MEMBER">MEMBER</option>
            <option value="PROVIDER">PROVIDER</option>
            <option value="PLAN">PLAN</option>
          </select>
        </div>

        {/* MCDM Column with suggestions */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-gray-700">
              MCDM Column Name
            </label>
            <button
              onClick={getSuggestions}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Get Suggestions
            </button>
          </div>
          <input
            type="text"
            value={formData.mcdm_column_name || ''}
            onChange={(e) => setFormData({ ...formData, mcdm_column_name: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          
          {suggestions.length > 0 && (
            <div className="mt-2 border border-gray-200 rounded-md max-h-32 overflow-y-auto">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => setFormData({ 
                    ...formData, 
                    mcdm_column_name: suggestion.column_name,
                    mcdm_table: suggestion.table_name
                  })}
                  className="w-full text-left px-3 py-2 hover:bg-gray-50 text-sm border-b border-gray-100 last:border-b-0"
                >
                  <div className="font-medium">{suggestion.column_name}</div>
                  <div className="text-gray-500 text-xs">{suggestion.table_name} • {suggestion.reason}</div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* IN_MODEL */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            In Model
          </label>
          <select
            value={formData.in_model || 'Y'}
            onChange={(e) => setFormData({ ...formData, in_model: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="Y">Y - Include in model</option>
            <option value="N">N - Custom field</option>
            <option value="U">U - Under review</option>
            <option value="N/A">N/A - Skip</option>
          </select>
        </div>

        {/* Source Formatting */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Source Column Formatting
          </label>
          <textarea
            value={formData.source_column_formatting || ''}
            onChange={(e) => setFormData({ ...formData, source_column_formatting: e.target.value })}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
            placeholder="e.g., UPPER(column_name)"
          />
        </div>

        {/* Data Profile Info */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Data Profile Info
          </label>
          <textarea
            value={formData.data_profile_info || ''}
            onChange={(e) => setFormData({ ...formData, data_profile_info: e.target.value })}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Description of data profile or sample values..."
          />
        </div>

        {/* Skipped Flag */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="skipped"
            checked={formData.skipped_flag || false}
            onChange={(e) => setFormData({ ...formData, skipped_flag: e.target.checked })}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="skipped" className="ml-2 block text-sm text-gray-900">
            Skip this field
          </label>
        </div>
      </div>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-gray-200">
        <div className="flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
          >
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
};

export default CrosswalkTemplateGrid;