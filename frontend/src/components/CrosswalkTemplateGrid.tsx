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
  const [editingCell, setEditingCell] = useState<{rowId: string; columnId: string} | null>(null);

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

  // Update cell value
  const updateCell = async (rowId: string, columnId: string, value: any) => {
    const mapping = data.find(m => m.id.toString() === rowId);
    if (!mapping) return;

    try {
      await crosswalkApi.updateMapping(mapping.id, {
        [columnId]: value
      });
      
      // Update local data
      setData(prev => prev.map(item => 
        item.id.toString() === rowId 
          ? { ...item, [columnId]: value }
          : item
      ));
      setEditingCell(null);
    } catch (err: any) {
      console.error('Error updating mapping:', err);
      alert('Failed to update mapping: ' + (err.message || 'Unknown error'));
    }
  };

  // Table columns matching Excel template structure
  const columns = useMemo<ColumnDef<CrosswalkMapping>[]>(() => [
    {
      accessorKey: 'client_id',
      header: 'Client ID',
      size: 100,
      cell: ({ getValue, row, column }) => {
        const value = getValue() as string;
        const isEditing = editingCell?.rowId === row.id && editingCell?.columnId === column.id;
        
        return isEditing ? (
          <input
            className="w-full px-1 py-0.5 text-xs border rounded"
            defaultValue={value || ''}
            onBlur={(e) => updateCell(row.id, column.id, e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                updateCell(row.id, column.id, (e.target as HTMLInputElement).value);
              } else if (e.key === 'Escape') {
                setEditingCell(null);
              }
            }}
            autoFocus
          />
        ) : (
          <div
            className="cursor-pointer hover:bg-gray-100 px-1 py-0.5 min-h-[20px]"
            onClick={() => setEditingCell({rowId: row.id, columnId: column.id})}
          >
            {value || ''}
          </div>
        );
      },
    },
    {
      accessorKey: 'source_column_order',
      header: 'Column Order',
      size: 90,
      cell: ({ getValue, row, column }) => {
        const value = getValue() as number;
        const isEditing = editingCell?.rowId === row.id && editingCell?.columnId === column.id;
        
        return isEditing ? (
          <input
            type="number"
            className="w-full px-1 py-0.5 text-xs border rounded"
            defaultValue={value || ''}
            onBlur={(e) => updateCell(row.id, column.id, parseInt(e.target.value) || null)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                updateCell(row.id, column.id, parseInt((e.target as HTMLInputElement).value) || null);
              } else if (e.key === 'Escape') {
                setEditingCell(null);
              }
            }}
            autoFocus
          />
        ) : (
          <div
            className="cursor-pointer hover:bg-gray-100 px-1 py-0.5 min-h-[20px] text-center"
            onClick={() => setEditingCell({rowId: row.id, columnId: column.id})}
          >
            {value || ''}
          </div>
        );
      },
    },
    {
      accessorKey: 'source_column_name',
      header: 'Source Column Name',
      size: 180,
      cell: ({ getValue, row, column }) => {
        const value = getValue() as string;
        const isEditing = editingCell?.rowId === row.id && editingCell?.columnId === column.id;
        
        return isEditing ? (
          <input
            className="w-full px-1 py-0.5 text-xs border rounded"
            defaultValue={value || ''}
            onBlur={(e) => updateCell(row.id, column.id, e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                updateCell(row.id, column.id, (e.target as HTMLInputElement).value);
              } else if (e.key === 'Escape') {
                setEditingCell(null);
              }
            }}
            autoFocus
          />
        ) : (
          <div
            className="cursor-pointer hover:bg-gray-100 px-1 py-0.5 min-h-[20px] font-medium"
            onClick={() => setEditingCell({rowId: row.id, columnId: column.id})}
          >
            {value || ''}
          </div>
        );
      },
    },
    {
      accessorKey: 'file_group_name',
      header: 'File Group',
      size: 120,
      cell: ({ getValue, row, column }) => {
        const value = getValue() as string;
        const isEditing = editingCell?.rowId === row.id && editingCell?.columnId === column.id;
        
        return isEditing ? (
          <select
            className="w-full px-1 py-0.5 text-xs border rounded"
            defaultValue={value || ''}
            onChange={(e) => updateCell(row.id, column.id, e.target.value)}
            onBlur={() => setEditingCell(null)}
            autoFocus
          >
            <option value="">Select...</option>
            <option value="CLAIM">CLAIM</option>
            <option value="CLAIM_LINE">CLAIM_LINE</option>
            <option value="MEMBER">MEMBER</option>
            <option value="PROVIDER">PROVIDER</option>
            <option value="PLAN">PLAN</option>
          </select>
        ) : (
          <div
            className="cursor-pointer hover:bg-gray-100 px-1 py-0.5 min-h-[20px]"
            onClick={() => setEditingCell({rowId: row.id, columnId: column.id})}
          >
            <span className={`px-2 py-0.5 rounded-full text-xs ${
              value === 'CLAIM' ? 'bg-blue-100 text-blue-800' :
              value === 'CLAIM_LINE' ? 'bg-green-100 text-green-800' :
              value === 'MEMBER' ? 'bg-purple-100 text-purple-800' :
              value === 'PROVIDER' ? 'bg-orange-100 text-orange-800' :
              value === 'PLAN' ? 'bg-pink-100 text-pink-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {value || ''}
            </span>
          </div>
        );
      },
    },
    {
      accessorKey: 'mcdm_column_name',
      header: 'MCDM Column Name',
      size: 180,
      cell: ({ getValue, row, column }) => {
        const value = getValue() as string;
        const isEditing = editingCell?.rowId === row.id && editingCell?.columnId === column.id;
        
        return isEditing ? (
          <input
            className="w-full px-1 py-0.5 text-xs border rounded"
            defaultValue={value || ''}
            onBlur={(e) => updateCell(row.id, column.id, e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                updateCell(row.id, column.id, (e.target as HTMLInputElement).value);
              } else if (e.key === 'Escape') {
                setEditingCell(null);
              }
            }}
            autoFocus
          />
        ) : (
          <div
            className="cursor-pointer hover:bg-gray-100 px-1 py-0.5 min-h-[20px] font-medium text-blue-600"
            onClick={() => setEditingCell({rowId: row.id, columnId: column.id})}
          >
            {value || ''}
          </div>
        );
      },
    },
    {
      accessorKey: 'in_model',
      header: 'In Model',
      size: 80,
      cell: ({ getValue, row, column }) => {
        const value = getValue() as string;
        const isEditing = editingCell?.rowId === row.id && editingCell?.columnId === column.id;
        
        return isEditing ? (
          <select
            className="w-full px-1 py-0.5 text-xs border rounded"
            defaultValue={value || 'Y'}
            onChange={(e) => updateCell(row.id, column.id, e.target.value)}
            onBlur={() => setEditingCell(null)}
            autoFocus
          >
            <option value="Y">Y</option>
            <option value="N">N</option>
            <option value="U">U</option>
            <option value="N/A">N/A</option>
          </select>
        ) : (
          <div
            className="cursor-pointer hover:bg-gray-100 px-1 py-0.5 min-h-[20px] text-center"
            onClick={() => setEditingCell({rowId: row.id, columnId: column.id})}
          >
            <span className={`px-1.5 py-0.5 rounded text-xs font-bold ${
              value === 'Y' ? 'bg-green-100 text-green-800' :
              value === 'N' ? 'bg-red-100 text-red-800' :
              value === 'U' ? 'bg-yellow-100 text-yellow-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {value || 'Y'}
            </span>
          </div>
        );
      },
    },
    {
      accessorKey: 'mcdm_table',
      header: 'MCDM Table',
      size: 120,
      cell: ({ getValue, row, column }) => {
        const value = getValue() as string;
        const isEditing = editingCell?.rowId === row.id && editingCell?.columnId === column.id;
        
        return isEditing ? (
          <input
            className="w-full px-1 py-0.5 text-xs border rounded"
            defaultValue={value || ''}
            onBlur={(e) => updateCell(row.id, column.id, e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                updateCell(row.id, column.id, (e.target as HTMLInputElement).value);
              } else if (e.key === 'Escape') {
                setEditingCell(null);
              }
            }}
            autoFocus
          />
        ) : (
          <div
            className="cursor-pointer hover:bg-gray-100 px-1 py-0.5 min-h-[20px]"
            onClick={() => setEditingCell({rowId: row.id, columnId: column.id})}
          >
            {value || ''}
          </div>
        );
      },
    },
    {
      accessorKey: 'data_profile_info',
      header: 'Data Profile',
      size: 150,
      cell: ({ getValue, row, column }) => {
        const value = getValue() as string;
        const isEditing = editingCell?.rowId === row.id && editingCell?.columnId === column.id;
        
        return isEditing ? (
          <textarea
            className="w-full px-1 py-0.5 text-xs border rounded resize-none"
            rows={2}
            defaultValue={value || ''}
            onBlur={(e) => updateCell(row.id, column.id, e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                updateCell(row.id, column.id, (e.target as HTMLTextAreaElement).value);
              } else if (e.key === 'Escape') {
                setEditingCell(null);
              }
            }}
            autoFocus
          />
        ) : (
          <div
            className="cursor-pointer hover:bg-gray-100 px-1 py-0.5 min-h-[20px] text-xs"
            onClick={() => setEditingCell({rowId: row.id, columnId: column.id})}
            title={value || ''}
          >
            {value ? (value.length > 50 ? `${value.substring(0, 50)}...` : value) : ''}
          </div>
        );
      },
    },
    {
      accessorKey: 'source_column_formatting',
      header: 'Source Formatting',
      size: 150,
      cell: ({ getValue, row, column }) => {
        const value = getValue() as string;
        const isEditing = editingCell?.rowId === row.id && editingCell?.columnId === column.id;
        
        return isEditing ? (
          <textarea
            className="w-full px-1 py-0.5 text-xs border rounded resize-none font-mono"
            rows={2}
            defaultValue={value || ''}
            onBlur={(e) => updateCell(row.id, column.id, e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                updateCell(row.id, column.id, (e.target as HTMLTextAreaElement).value);
              } else if (e.key === 'Escape') {
                setEditingCell(null);
              }
            }}
            autoFocus
          />
        ) : (
          <div
            className="cursor-pointer hover:bg-gray-100 px-1 py-0.5 min-h-[20px] text-xs font-mono"
            onClick={() => setEditingCell({rowId: row.id, columnId: column.id})}
            title={value || ''}
          >
            {value ? (value.length > 30 ? `${value.substring(0, 30)}...` : value) : ''}
          </div>
        );
      },
    },
    {
      accessorKey: 'skipped_flag',
      header: 'Skip',
      size: 60,
      cell: ({ getValue, row, column }) => {
        const value = getValue() as boolean;
        
        return (
          <div className="text-center">
            <input
              type="checkbox"
              checked={value || false}
              onChange={(e) => updateCell(row.id, column.id, e.target.checked)}
              className="rounded"
            />
          </div>
        );
      },
    },
  ], [editingCell]);

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      sorting,
      columnFilters,
    },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-2">Loading crosswalk data...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 m-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <i className="fas fa-exclamation-circle text-red-400"></i>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error loading crosswalk data</h3>
            <div className="mt-2 text-sm text-red-700">{error}</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-white border-b px-4 py-2 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h2 className="text-lg font-semibold">Crosswalk Template</h2>
          <div className="text-sm text-gray-500">
            {data.length} mappings
            {clientId && <span> for {clientId}</span>}
            {fileGroup && <span> ({fileGroup})</span>}
          </div>
        </div>
        <div className="text-xs text-gray-500">
          Click any cell to edit • Enter to save • Esc to cancel
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 sticky top-0 z-10">
            {table.getHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map(header => (
                  <th
                    key={header.id}
                    className="border border-gray-200 px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    style={{ width: header.getSize() }}
                  >
                    {header.isPlaceholder ? null : (
                      <div
                        className={header.column.getCanSort() ? 'cursor-pointer select-none' : ''}
                        onClick={header.column.getToggleSortingHandler()}
                      >
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        {{
                          asc: ' ↑',
                          desc: ' ↓',
                        }[header.column.getIsSorted() as string] ?? null}
                      </div>
                    )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="bg-white">
            {table.getRowModel().rows.map((row, index) => (
              <tr key={row.id} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                {row.getVisibleCells().map(cell => (
                  <td
                    key={cell.id}
                    className="border border-gray-200 text-sm"
                    style={{ width: cell.column.getSize() }}
                  >
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div className="bg-gray-50 border-t px-4 py-2 text-xs text-gray-500">
        Displaying {data.length} crosswalk mappings. Click any cell to edit values inline.
      </div>
    </div>
  );
};

export default CrosswalkTemplateGrid;