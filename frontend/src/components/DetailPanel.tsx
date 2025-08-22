import React, { useState } from 'react';
import { Profile } from '../types';
import RegexTester from './RegexTester';
import { api } from '../services/api';

interface DetailPanelProps {
  profile: Profile;
  selectedColumn: any;
  validationSummary: any;
  onRefresh: () => void;
}

const DetailPanel: React.FC<DetailPanelProps> = ({
  profile,
  selectedColumn,
  validationSummary,
  onRefresh
}) => {
  const [activeTab, setActiveTab] = useState<'regex' | 'sample' | 'validation' | 'export'>('regex');
  const [sampleData, setSampleData] = useState<any[]>([]);
  const [loadingSample, setLoadingSample] = useState(false);
  const [sampleError, setSampleError] = useState<string | null>(null);

  const fetchWarehouseSample = async () => {
    setLoadingSample(true);
    setSampleError(null);
    
    try {
      const response = await api.post(`/profiles/${profile.id}/sample/fetch`);
      setSampleData(response.data || []);
    } catch (error: any) {
      setSampleError(error.response?.data?.detail || 'Failed to fetch sample data');
    } finally {
      setLoadingSample(false);
    }
  };

  const downloadExport = async (format: 'csv' | 'xlsx' | 'json' | 'sql') => {
    try {
      const response = await fetch(`http://localhost:8000/api/profiles/${profile.id}/export/${format}`, {
        method: 'GET',
      });
      
      if (!response.ok) {
        throw new Error('Export failed');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `crosswalk_${profile.id}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Export error:', error);
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Details</h3>
        
        {/* Tab Navigation */}
        <div className="mt-4 flex space-x-1 border-b border-gray-200">
          {[
            { id: 'regex', label: 'Regex Tester', icon: 'fa-code' },
            { id: 'sample', label: 'Sample Data', icon: 'fa-database' },
            { id: 'validation', label: 'Validation', icon: 'fa-check-circle' },
            { id: 'export', label: 'Export', icon: 'fa-download' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-3 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <i className={`fas ${tab.icon} mr-1`}></i>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'regex' && (
          <div className="p-4">
            {selectedColumn ? (
              <RegexTester
                sourceColumn={selectedColumn}
                onRuleChange={onRefresh}
              />
            ) : (
              <div className="text-center py-8">
                <i className="fas fa-mouse-pointer text-gray-400 text-2xl mb-2"></i>
                <p className="text-gray-600">Select a row to test regex patterns</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'sample' && (
          <div className="p-4">
            <div className="space-y-4">
              {/* Sample Values from File */}
              {selectedColumn?.sample_values && selectedColumn.sample_values.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-2">
                    Sample Values (from file)
                  </h4>
                  <div className="bg-gray-50 rounded-md p-3 max-h-32 overflow-y-auto">
                    {selectedColumn.sample_values.map((value: string, index: number) => (
                      <div key={index} className="text-sm text-gray-700 py-1 border-b border-gray-200 last:border-b-0">
                        {value}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Warehouse Sample */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-medium text-gray-900">
                    Warehouse Sample
                  </h4>
                  <button
                    onClick={fetchWarehouseSample}
                    disabled={loadingSample}
                    className="inline-flex items-center px-3 py-1 border border-gray-300 text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
                  >
                    {loadingSample ? (
                      <>
                        <i className="fas fa-spinner fa-spin mr-1"></i>
                        Loading...
                      </>
                    ) : (
                      <>
                        <i className="fas fa-download mr-1"></i>
                        Fetch Sample
                      </>
                    )}
                  </button>
                </div>

                {sampleError && (
                  <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-3">
                    <div className="flex">
                      <i className="fas fa-exclamation-triangle text-red-400 mt-0.5 mr-2"></i>
                      <div>
                        <h5 className="text-sm font-medium text-red-800">Error</h5>
                        <p className="text-sm text-red-700 mt-1">{sampleError}</p>
                      </div>
                    </div>
                  </div>
                )}

                {sampleData.length > 0 && (
                  <div className="bg-gray-50 rounded-md p-3 max-h-64 overflow-auto">
                    <div className="text-xs text-gray-600 mb-2">
                      {sampleData.length} rows fetched
                    </div>
                    <div className="space-y-2">
                      {sampleData.slice(0, 10).map((row, index) => (
                        <div key={index} className="bg-white rounded p-2 text-sm">
                          <pre className="text-xs text-gray-700 whitespace-pre-wrap">
                            {JSON.stringify(row, null, 2)}
                          </pre>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {sampleData.length === 0 && !sampleError && !loadingSample && (
                  <div className="text-center py-6 text-gray-500">
                    <i className="fas fa-database text-2xl mb-2"></i>
                    <p className="text-sm">No sample data available</p>
                    <p className="text-xs">Click "Fetch Sample" to retrieve data from warehouse</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'validation' && (
          <div className="p-4">
            {validationSummary ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-blue-50 rounded-lg p-3">
                    <div className="text-2xl font-bold text-blue-600">
                      {validationSummary.mapped_columns}
                    </div>
                    <div className="text-sm text-blue-800">Mapped Columns</div>
                  </div>
                  
                  <div className="bg-orange-50 rounded-lg p-3">
                    <div className="text-2xl font-bold text-orange-600">
                      {validationSummary.unmapped_columns}
                    </div>
                    <div className="text-sm text-orange-800">Unmapped Columns</div>
                  </div>
                  
                  <div className="bg-green-50 rounded-lg p-3">
                    <div className="text-2xl font-bold text-green-600">
                      {validationSummary.regex_pass_count}
                    </div>
                    <div className="text-sm text-green-800">Regex Passes</div>
                  </div>
                  
                  <div className="bg-red-50 rounded-lg p-3">
                    <div className="text-2xl font-bold text-red-600">
                      {validationSummary.regex_fail_count}
                    </div>
                    <div className="text-sm text-red-800">Regex Failures</div>
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">
                    Mapping Progress
                  </h4>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div 
                      className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                      style={{ width: `${validationSummary.mapping_percentage}%` }}
                    ></div>
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    {validationSummary.mapping_percentage}% complete
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <i className="fas fa-chart-bar text-gray-400 text-2xl mb-2"></i>
                <p className="text-gray-600">No validation data available</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'export' && (
          <div className="p-4">
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-3">Export Formats</h4>
                <div className="space-y-2">
                  <button
                    onClick={() => downloadExport('csv')}
                    className="w-full flex items-center justify-between p-3 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <div className="flex items-center">
                      <i className="fas fa-file-csv text-green-600 mr-3"></i>
                      <div className="text-left">
                        <div className="text-sm font-medium text-gray-900">CSV Export</div>
                        <div className="text-xs text-gray-600">Crosswalk mapping table</div>
                      </div>
                    </div>
                    <i className="fas fa-download text-gray-400"></i>
                  </button>

                  <button
                    onClick={() => downloadExport('xlsx')}
                    className="w-full flex items-center justify-between p-3 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <div className="flex items-center">
                      <i className="fas fa-file-excel text-green-600 mr-3"></i>
                      <div className="text-left">
                        <div className="text-sm font-medium text-gray-900">Excel Export</div>
                        <div className="text-xs text-gray-600">Spreadsheet format</div>
                      </div>
                    </div>
                    <i className="fas fa-download text-gray-400"></i>
                  </button>

                  <button
                    onClick={() => downloadExport('json')}
                    className="w-full flex items-center justify-between p-3 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <div className="flex items-center">
                      <i className="fas fa-file-code text-blue-600 mr-3"></i>
                      <div className="text-left">
                        <div className="text-sm font-medium text-gray-900">JSON Config</div>
                        <div className="text-xs text-gray-600">Pipeline configuration</div>
                      </div>
                    </div>
                    <i className="fas fa-download text-gray-400"></i>
                  </button>

                  <button
                    onClick={() => downloadExport('sql')}
                    className="w-full flex items-center justify-between p-3 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <div className="flex items-center">
                      <i className="fas fa-database text-purple-600 mr-3"></i>
                      <div className="text-left">
                        <div className="text-sm font-medium text-gray-900">SQL Script</div>
                        <div className="text-xs text-gray-600">DDL/DML statements</div>
                      </div>
                    </div>
                    <i className="fas fa-download text-gray-400"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DetailPanel;
