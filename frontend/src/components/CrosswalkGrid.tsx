import React, { useState, useEffect } from 'react';
import { useReactTable, getCoreRowModel, createColumnHelper, flexRender } from '@tanstack/react-table';
import { api } from '../services/api';

interface CrosswalkGridProps {
  profileId: number;
  mappings: any[];
  loading: boolean;
  onMappingsUpdate: (mappings: any[]) => void;
  onRowSelect: (mapping: any) => void;
  selectedRow: any;
}

const CrosswalkGrid: React.FC<CrosswalkGridProps> = ({
  profileId,
  mappings,
  loading,
  onMappingsUpdate,
  onRowSelect,
  selectedRow
}) => {
  const [data, setData] = useState<any[]>([]);
  const [dataModelFields, setDataModelFields] = useState<any>({});
  const [filter, setFilter] = useState('');

  const columnHelper = createColumnHelper<any>();

  useEffect(() => {
    setData(mappings);
  }, [mappings]);

  useEffect(() => {
    fetchDataModelFields();
  }, []);

  const fetchDataModelFields = async () => {
    try {
      const fields = await api.get('/data-model-fields');
      setDataModelFields(fields);
    } catch (error) {
      console.error('Error fetching data model fields:', error);
    }
  };

  const updateMappingField = (rowIndex: number, field: string, value: any) => {
    const newData = [...data];
    newData[rowIndex] = { ...newData[rowIndex], [field]: value };
    
    // Clear custom field name if not custom
    if (field === 'is_custom_field' && !value) {
      newData[rowIndex].custom_field_name = '';
    }
    
    // Clear model fields if custom
    if (field === 'is_custom_field' && value) {
      newData[rowIndex].model_table = '';
      newData[rowIndex].model_column = '';
    }
    
    // Update model columns when table changes
    if (field === 'model_table') {
      newData[rowIndex].model_column = '';
    }
    
    setData(newData);
  };

  const handleSave = async () => {
    try {
      await onMappingsUpdate(data);
    } catch (error) {
      console.error('Error saving mappings:', error);
    }
  };

  const columns = [
    columnHelper.accessor('source_column', {
      header: 'Source Column',
      cell: ({ getValue, row }) => (
        <div className="flex items-center space-x-2">
          <span className="font-medium text-gray-900">{getValue()}</span>
          {row.original.inferred_type && (
            <span className={`px-1.5 py-0.5 text-xs rounded ${
              row.original.inferred_type === 'string' ? 'bg-blue-100 text-blue-800' :
              row.original.inferred_type === 'number' ? 'bg-green-100 text-green-800' :
              row.original.inferred_type === 'date' ? 'bg-purple-100 text-purple-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {row.original.inferred_type}
            </span>
          )}
        </div>
      ),
    }),
    
    columnHelper.accessor('model_table', {
      header: 'Model Table',
      cell: ({ getValue, row, table }) => (
        <select
          value={getValue() || ''}
          onChange={(e) => updateMappingField(row.index, 'model_table', e.target.value)}
          disabled={row.original.is_custom_field}
          className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-100"
        >
          <option value="">Select table...</option>
          {Object.keys(dataModelFields).map(table => (
            <option key={table} value={table}>{table}</option>
          ))}
        </select>
      ),
    }),
    
    columnHelper.accessor('model_column', {
      header: 'Model Column',
      cell: ({ getValue, row }) => (
        <select
          value={getValue() || ''}
          onChange={(e) => updateMappingField(row.index, 'model_column', e.target.value)}
          disabled={row.original.is_custom_field || !row.original.model_table}
          className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-100"
        >
          <option value="">Select column...</option>
          {row.original.model_table && dataModelFields[row.original.model_table]?.map((field: any) => (
            <option key={field.column} value={field.column}>
              {field.column}
              {field.required && <span className="text-red-500">*</span>}
            </option>
          ))}
        </select>
      ),
    }),
    
    columnHelper.accessor('is_custom_field', {
      header: 'Custom?',
      cell: ({ getValue, row }) => (
        <input
          type="checkbox"
          checked={getValue() || false}
          onChange={(e) => updateMappingField(row.index, 'is_custom_field', e.target.checked)}
          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
      ),
    }),
    
    columnHelper.accessor('custom_field_name', {
      header: 'Custom Field Name',
      cell: ({ getValue, row }) => (
        <input
          type="text"
          value={getValue() || ''}
          onChange={(e) => updateMappingField(row.index, 'custom_field_name', e.target.value)}
          disabled={!row.original.is_custom_field}
          placeholder="Custom field name"
          className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-100"
        />
      ),
    }),
    
    columnHelper.accessor('transform_expression', {
      header: 'Transform (DSL)',
      cell: ({ getValue, row }) => (
        <input
          type="text"
          value={getValue() || ''}
          onChange={(e) => updateMappingField(row.index, 'transform_expression', e.target.value)}
          placeholder="e.g., upper(col('SOURCE_COLUMN'))"
          className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      ),
    }),
    
    columnHelper.accessor('regex_rules', {
      header: 'Regex Rules',
      cell: ({ getValue, row }) => {
        const rules = getValue() || [];
        return (
          <div className="flex flex-wrap gap-1">
            {rules.map((rule: any, index: number) => (
              <span
                key={index}
                className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-yellow-100 text-yellow-800"
              >
                {rule.rule_name || 'Rule'}
              </span>
            ))}
            {rules.length === 0 && (
              <span className="text-xs text-gray-400">No rules</span>
            )}
          </div>
        );
      },
    }),
    
    columnHelper.accessor('is_mapped', {
      header: 'Mapped?',
      cell: ({ getValue, row }) => {
        const isMapped = row.original.model_column || row.original.custom_field_name;
        return (
          <div className="flex items-center">
            {isMapped ? (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                <i className="fas fa-check mr-1"></i>
                Mapped
              </span>
            ) : (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-800">
                <i className="fas fa-minus mr-1"></i>
                Unmapped
              </span>
            )}
          </div>
        );
      },
    }),
  ];

  const table = useReactTable({
    data: data.filter(row => 
      !filter || row.source_column.toLowerCase().includes(filter.toLowerCase())
    ),
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <i className="fas fa-spinner fa-spin text-gray-400 text-2xl mb-2"></i>
          <p className="text-gray-600">Loading crosswalk data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col">
      {/* Toolbar */}
      <div className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <i className="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
              <input
                type="text"
                placeholder="Filter columns..."
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="pl-9 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div className="text-sm text-gray-600">
              {data.length} columns
            </div>
          </div>
          
          <button
            onClick={handleSave}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <i className="fas fa-save mr-2"></i>
            Save Mappings
          </button>
        </div>
      </div>

      {/* Grid */}
      <div className="flex-1 overflow-auto">
        {data.length === 0 ? (
          <div className="flex-1 flex items-center justify-center bg-gray-50">
            <div className="text-center">
              <i className="fas fa-table text-gray-400 text-3xl mb-3"></i>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Data Available</h3>
              <p className="text-gray-600 max-w-sm">
                Upload a file or paste a schema to start mapping your columns.
              </p>
            </div>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              {table.getHeaderGroups().map(headerGroup => (
                <tr key={headerGroup.id}>
                  {headerGroup.headers.map(header => (
                    <th
                      key={header.id}
                      className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {header.isPlaceholder
                        ? null
                        : flexRender(header.column.columnDef.header, header.getContext())
                      }
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {table.getRowModel().rows.map(row => (
                <tr
                  key={row.id}
                  onClick={() => onRowSelect(row.original)}
                  className={`hover:bg-gray-50 cursor-pointer ${
                    selectedRow?.source_column_id === row.original.source_column_id
                      ? 'bg-blue-50 border-l-4 border-blue-500'
                      : ''
                  }`}
                >
                  {row.getVisibleCells().map(cell => (
                    <td key={cell.id} className="px-4 py-3 whitespace-nowrap text-sm">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default CrosswalkGrid;
