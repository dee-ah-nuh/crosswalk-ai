import React, { useState } from 'react';
import { crosswalkApi } from '../services/crosswalkApi';

interface SnowflakeExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  clientId?: string;
  fileGroup?: string;
}

const SnowflakeExportModal: React.FC<SnowflakeExportModalProps> = ({
  isOpen,
  onClose,
  clientId,
  fileGroup
}) => {
  const [exportType, setExportType] = useState<string>('CREATE_TABLE');
  const [tableName, setTableName] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [generatedSQL, setGeneratedSQL] = useState<string>('');
  const [error, setError] = useState<string>('');

  const handleGenerate = async () => {
    if (!clientId || !tableName.trim()) {
      setError('Client ID and table name are required');
      return;
    }

    setLoading(true);
    setError('');
    setGeneratedSQL('');

    try {
      const result = await crosswalkApi.generateSnowflakeSQL({
        client_id: clientId,
        file_group: fileGroup,
        export_type: exportType,
        table_name: tableName.trim(),
        created_by: 'WEB_USER'
      });

      setGeneratedSQL(result.sql_content);
    } catch (err: any) {
      setError(err.message || 'Failed to generate SQL');
    } finally {
      setLoading(false);
    }
  };

  const handleCopySQL = () => {
    navigator.clipboard.writeText(generatedSQL);
    alert('SQL copied to clipboard!');
  };

  const handleDownload = () => {
    const blob = new Blob([generatedSQL], { type: 'text/sql' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${tableName}_${exportType.toLowerCase()}.sql`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg shadow-xl w-full max-w-4xl mx-4 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-700 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-white">
            <i className="fas fa-database text-orange-600 mr-2"></i>
            Generate Snowflake SQL
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-200"
          >
            <i className="fas fa-times text-xl"></i>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden flex flex-col p-6">
          {/* Configuration */}
          <div className="space-y-4 mb-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-white mb-2">
                  Export Type
                </label>
                <select
                  value={exportType}
                  onChange={(e) => setExportType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-600 rounded-md focus:ring-2 focus:ring-orange-500 focus:border-orange-500 bg-gray-700 text-white"
                >
                  <option value="CREATE_TABLE">CREATE TABLE</option>
                  <option value="INSERT_MAPPING">🎯 Crosswalk Configuration INSERTs (ETL Foundation)</option>
                  <option value="FULL_ETL">Full ETL with Joins</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-white mb-2">
                  Table Name
                </label>
                <input
                  type="text"
                  value={tableName}
                  onChange={(e) => setTableName(e.target.value)}
                  placeholder="e.g., UPHP_CLAIMS_STAGING"
                  className="w-full px-3 py-2 border border-gray-600 rounded-md focus:ring-2 focus:ring-orange-500 focus:border-orange-500 bg-gray-700 text-white"
                />
              </div>
            </div>

            <div className="bg-gray-700 p-4 rounded-lg border border-gray-600">
              <h3 className="font-medium text-orange-400 mb-2">Configuration Summary</h3>
              <div className="text-sm text-gray-300 space-y-1">
                <p><strong>Client:</strong> {clientId}</p>
                <p><strong>File Group:</strong> {fileGroup || 'All'}</p>
                <p><strong>Export Type:</strong> {exportType === 'INSERT_MAPPING' ? 'Crosswalk Configuration INSERTs' : exportType}</p>
                <p><strong>Target Table:</strong> {tableName || (exportType === 'INSERT_MAPPING' ? 'crosswalk.configuration (recommended)' : 'Not specified')}</p>
              </div>
              
              {exportType === 'INSERT_MAPPING' && (
                <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded">
                  <p className="text-sm text-yellow-800">
                    <i className="fas fa-info-circle mr-2"></i>
                    <strong>Critical:</strong> These INSERTs populate your crosswalk.configuration table - 
                    the foundation for all your ETL processes. This is the "Output DML for Crosswalk" functionality.
                  </p>
                </div>
              )}
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex">
                  <i className="fas fa-exclamation-triangle text-red-400 mr-2 mt-1"></i>
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            )}

            <div className="flex items-center space-x-3">
              <button
                onClick={handleGenerate}
                disabled={loading || !tableName.trim()}
                className="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Generating...
                  </>
                ) : (
                  <>
                    <i className="fas fa-code mr-2"></i>
                    Generate SQL
                  </>
                )}
              </button>
              
              {generatedSQL && (
                <>
                  <button
                    onClick={handleCopySQL}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center"
                  >
                    <i className="fas fa-copy mr-2"></i>
                    Copy
                  </button>
                  <button
                    onClick={handleDownload}
                    className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 flex items-center"
                  >
                    <i className="fas fa-download mr-2"></i>
                    Download
                  </button>
                </>
              )}
            </div>
          </div>

          {/* SQL Output */}
          {generatedSQL && (
            <div className="flex-1 min-h-0">
              <label className="block text-sm font-medium text-white mb-2">
                Generated SQL
              </label>
              <div className="h-full border border-gray-600 rounded-md overflow-hidden">
                <textarea
                  value={generatedSQL}
                  readOnly
                  className="w-full h-full p-3 font-mono text-sm resize-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 bg-gray-700 text-white"
                  style={{ minHeight: '300px' }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-700 bg-gray-700">
          <div className="flex justify-end space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-300 bg-gray-700 border border-gray-600 rounded-md hover:bg-gray-600"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SnowflakeExportModal;