import React, { useState, useEffect } from 'react';
import { useReactTable, getCoreRowModel, createColumnHelper, flexRender, getSortedRowModel, getFilteredRowModel } from '@tanstack/react-table';
import { api } from '../services/api';

interface PI20DataModelField {
  id: number;
  in_crosswalk: string;
  table_name: string;
  column_name: string;
  column_type: string;
  column_order: number;
  column_comment: string;
  table_creation_order: number;
  is_mandatory: boolean;
  mandatory_prov_type: string;
  mcdm_masking_type: string;
  in_edits: boolean;
  key: string;
}

interface PI20DataModelProps {
  onFieldSelect?: (field: PI20DataModelField) => void;
  selectedField?: PI20DataModelField | null;
}

const PI20DataModel: React.FC<PI20DataModelProps> = ({ 
  onFieldSelect,
  selectedField 
}) => {
  const [data, setData] = useState<PI20DataModelField[]>([]);
  const [loading, setLoading] = useState(true);
  const [globalFilter, setGlobalFilter] = useState('');
  const [tableFilter, setTableFilter] = useState('');

  const columnHelper = createColumnHelper<PI20DataModelField>();

  useEffect(() => {
    fetchPI20Data();
  }, []);

  const fetchPI20Data = async () => {
    try {
      setLoading(true);
      const response = await api.get('/datamodel');
      setData(response);
    } catch (error) {
      console.error('Error fetching PI20 data model:', error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    columnHelper.accessor('table_name', {
      header: 'Table',
      cell: info => (
        <span className="font-medium text-white">
          {info.getValue()}
        </span>
      ),
    }),
    columnHelper.accessor('column_name', {
      header: 'Column',
      cell: info => (
        <span className="text-orange-600 font-mono">
          {info.getValue()}
        </span>
      ),
    }),
    columnHelper.accessor('column_type', {
      header: 'Data Type',
      cell: info => (
        <span className="text-xs bg-gray-700 text-gray-300 px-2 py-1 rounded">
          {info.getValue()}
        </span>
      ),
    }),
    columnHelper.accessor('column_comment', {
      header: 'Description',
      cell: info => (
        <span className="text-sm text-gray-300">
          {info.getValue() || 'No description'}
        </span>
      ),
    }),
    columnHelper.accessor('is_mandatory', {
      header: 'Mandatory',
      cell: info => (
        <span className={`px-2 py-1 rounded-full text-xs ${
          info.getValue() 
            ? 'bg-red-100 text-red-800' 
            : 'bg-gray-100 text-gray-600'
        }`}>
          {info.getValue() ? 'Yes' : 'No'}
        </span>
      ),
    }),
    columnHelper.accessor('in_crosswalk', {
      header: 'In Crosswalk',
      cell: info => (
        <span className={`px-2 py-1 rounded-full text-xs ${
          info.getValue() === 'Y' 
            ? 'bg-green-100 text-green-800' 
            : 'bg-yellow-100 text-yellow-800'
        }`}>
          {info.getValue()}
        </span>
      ),
    }),
  ];

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      globalFilter,
    },
    onGlobalFilterChange: setGlobalFilter,
  });

  const filteredData = data.filter(field => {
    const matchesTable = !tableFilter || field.table_name.toLowerCase().includes(tableFilter.toLowerCase());
    return matchesTable;
  });

  // Get unique tables for filters
  const tables = [...new Set(data.map(field => field.table_name))];

  const handleRowClick = (field: PI20DataModelField) => {
    if (onFieldSelect) {
      onFieldSelect(field);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600"></div>
          <span className="text-white">Loading PI20 Data Model...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-800 flex flex-col">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-700">
        <h2 className="text-lg font-semibold text-white">PI20 Data Model</h2>
        <p className="text-sm text-gray-300 mt-1">
          Browse the standardized healthcare data model fields
        </p>
      </div>

      {/* Filters */}
      <div className="px-6 py-4 border-b border-gray-700 bg-gray-800">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Search
            </label>
            <div>
              <input
                type="text"
                value={globalFilter ?? ''}
                onChange={e => setGlobalFilter(e.target.value)}
                placeholder="Search columns, descriptions..."
                className="w-full px-3 pr-4 py-2 border border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 bg-gray-700 text-white placeholder-gray-400"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Table
            </label>
            <select
              value={tableFilter}
              onChange={e => setTableFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 bg-gray-700 text-white"
            >
              <option value="">All Tables</option>
              {tables.map(table => (
                <option key={table} value={table}>{table}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="px-6 py-3 bg-gray-700 border-b border-gray-600">
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-300">
            Showing {filteredData.length} of {data.length} fields
          </span>
          <span className="text-orange-600 font-medium">
            {tables.length} tables
          </span>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-700">
          <thead className="bg-gray-700 sticky top-0">
            {table.getHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map(header => (
                  <th
                    key={header.id}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-600"
                    onClick={header.column.getToggleSortingHandler()}
                  >
                    <div className="flex items-center space-x-1">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {header.column.getIsSorted() && (
                        <span className="text-gray-400">
                          {{
                            asc: '↑',
                            desc: '↓',
                          }[header.column.getIsSorted() as string]}
                        </span>
                      )}
                      {/* Show filter icon if filtering on this column */}
                      {(
                        (header.column.id === 'table_name' && tableFilter) ||
                        (header.column.id === 'column_name' && globalFilter)
                      ) && (
                        <span className="ml-1 text-orange-500" title="Filtering">
                          &#x25B6;
                        </span>
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="bg-gray-800 divide-y divide-gray-700">
            {table.getRowModel().rows.map(row => {
              const isSelected = selectedField?.id === row.original.id;
              return (
                <tr
                  key={row.id}
                  onClick={() => handleRowClick(row.original)}
                  className={`cursor-pointer hover:bg-gray-700 transition-colors ${
                    isSelected ? 'bg-gray-700 border-l-4 border-orange-500' : ''
                  }`}
                >
                  {row.getVisibleCells().map(cell => (
                    <td key={cell.id} className="px-6 py-4 whitespace-nowrap">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Empty State */}
      {filteredData.length === 0 && (
        <div className="flex-1 flex flex-col justify-center items-center">
          <div className="text-gray-400 text-lg mb-2">
            <i className="fas fa-database text-4xl mb-4"></i>
          </div>
          <div className="text-gray-400 text-lg mb-2">No fields found</div>
          <div className="text-gray-500 text-sm">
            Try adjusting your search or filter criteria
          </div>
        </div>
      )}
  </div>
  );
};

export default PI20DataModel;