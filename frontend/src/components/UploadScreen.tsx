import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { autoMappingService, MappingSuggestion } from '../services/autoMappingApi';

interface UploadScreenProps {}

interface ColumnInfo {
  name: string;
  sample_values: string[];
  suggestions?: MappingSuggestion[];
}

const UploadScreen: React.FC<UploadScreenProps> = () => {
  const navigate = useNavigate();
  const [clientId, setClientId] = useState('TEST');
  const [fileGroup, setFileGroup] = useState('CLAIM');
  const [version, setVersion] = useState('V00');
  const [stream, setStream] = useState('S00');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [columns, setColumns] = useState<ColumnInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<Record<string, MappingSuggestion[]>>({});

  // Sample demo data for testing
  const handleDemoData = async () => {
    setLoading(true);
    const demoColumns: ColumnInfo[] = [
      { name: 'MEMBER_FIRST_NAME', sample_values: ['John', 'Jane', 'Mike', 'Sarah'] },
      { name: 'MEMBER_LAST_NAME', sample_values: ['Smith', 'Johnson', 'Williams', 'Brown'] },
      { name: 'CLAIM_NUMBER', sample_values: ['12345-67890', '98765-43210', '11111-22222'] },
      { name: 'SERVICE_DATE', sample_values: ['2024-01-15', '2024-02-20', '2024-03-10'] },
      { name: 'CLAIM_AMOUNT', sample_values: ['1250.00', '890.50', '2100.75'] },
      { name: 'PROVIDER_NPI', sample_values: ['1234567890', '0987654321', '1122334455'] },
    ];

    setColumns(demoColumns);

    try {
      // Get AI suggestions for demo columns
      const sourceCols = demoColumns.map(col => ({
        column_name: col.name,
        sample_values: col.sample_values
      }));

      const aiSuggestions = await autoMappingService.getSuggestions(sourceCols);
      setSuggestions(aiSuggestions);
    } catch (error) {
      console.error('Error getting AI suggestions:', error);
    }

    setLoading(false);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      // In a real implementation, you would parse the CSV/Excel file here
      // For demo purposes, we'll use sample data
      handleDemoData();
    }
  };

  const handleProceedToCrosswalk = () => {
    // Navigate to crosswalk screen with the uploaded data
    navigate('/crosswalk', {
      state: {
        clientId,
        fileGroup,
        version,
        stream,
        columns,
        suggestions
      }
    });
  };

  return (
    <div className="h-screen bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="bg-gray-900 border-b border-gray-700 shadow-sm">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">Upload Source Data</h1>
              <p className="text-sm text-gray-300 mt-1">
                Upload client files or define schema to start crosswalk mapping
              </p>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={() => navigate('/crosswalk')}
                className="px-4 py-2 text-sm font-medium text-gray-300 bg-gray-700 rounded-lg hover:bg-gray-600"
              >
                Skip to Crosswalk
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-4xl mx-auto">
          
          {/* Project Configuration */}
          <div className="bg-gray-800 rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-white mb-4">Project Configuration</h2>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Client ID</label>
                <input
                  type="text"
                  value={clientId}
                  onChange={(e) => setClientId(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-orange-500"
                  placeholder="e.g., TEST"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">File Group</label>
                <select
                  value={fileGroup}
                  onChange={(e) => setFileGroup(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-orange-500"
                >
                  <option value="CLAIM">CLAIM</option>
                  <option value="CLAIM_LINE">CLAIM_LINE</option>
                  <option value="MEMBER">MEMBER</option>
                  <option value="PROVIDER">PROVIDER</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Version</label>
                <select
                  value={version}
                  onChange={(e) => setVersion(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-orange-500"
                >
                  <option value="V00">V00</option>
                  <option value="V01">V01</option>
                  <option value="V02">V02</option>
                  <option value="V03">V03</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Stream</label>
                <select
                  value={stream}
                  onChange={(e) => setStream(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-orange-500"
                >
                  <option value="S00">S00</option>
                  <option value="S02">S02</option>
                  <option value="S03">S03</option>
                  <option value="S04">S04</option>
                </select>
              </div>
            </div>
          </div>

          {/* File Upload Section */}
          <div className="bg-gray-800 rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-white mb-4">Data Source</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="border-2 border-dashed border-gray-600 rounded-lg p-6 text-center hover:border-orange-500 transition-colors">
                <i className="fas fa-cloud-upload-alt text-4xl text-gray-400 mb-4"></i>
                <h3 className="text-lg font-medium text-white mb-2">Upload CSV/Excel File</h3>
                <p className="text-sm text-gray-400 mb-4">
                  Upload your client's source data file
                </p>
                <input
                  type="file"
                  id="file-upload"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <label
                  htmlFor="file-upload"
                  className="cursor-pointer px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 inline-block"
                >
                  Choose File
                </label>
                {uploadedFile && (
                  <p className="mt-2 text-sm text-green-400">
                    ✓ {uploadedFile.name} uploaded
                  </p>
                )}
              </div>

              <div className="border-2 border-dashed border-gray-600 rounded-lg p-6 text-center hover:border-blue-500 transition-colors">
                <i className="fas fa-magic text-4xl text-gray-400 mb-4"></i>
                <h3 className="text-lg font-medium text-white mb-2">Use Demo Data</h3>
                <p className="text-sm text-gray-400 mb-4">
                  Try with sample healthcare data
                </p>
                <button
                  onClick={handleDemoData}
                  disabled={loading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? (
                    <>
                      <i className="fas fa-spinner fa-spin mr-2"></i>
                      Loading...
                    </>
                  ) : (
                    'Load Demo Data'
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Preview and AI Suggestions */}
          {columns.length > 0 && (
            <div className="bg-gray-800 rounded-lg p-6 mb-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-white">
                  Data Preview & AI Suggestions
                </h2>
                <span className="text-sm text-gray-400">{columns.length} columns detected</span>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-white">
                  <thead className="bg-gray-700">
                    <tr>
                      <th className="px-4 py-3 text-left">Source Column</th>
                      <th className="px-4 py-3 text-left">Sample Values</th>
                      <th className="px-4 py-3 text-left">AI Suggestion</th>
                      <th className="px-4 py-3 text-left">Confidence</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-600">
                    {columns.map((column, index) => {
                      const topSuggestion = suggestions[column.name]?.[0];
                      return (
                        <tr key={index} className="hover:bg-gray-700">
                          <td className="px-4 py-3 font-medium">{column.name}</td>
                          <td className="px-4 py-3 text-gray-300">
                            {column.sample_values.slice(0, 3).join(', ')}
                            {column.sample_values.length > 3 && '...'}
                          </td>
                          <td className="px-4 py-3">
                            {topSuggestion ? (
                              <span className="text-green-400">
                                {topSuggestion.target_table}.{topSuggestion.target_column}
                              </span>
                            ) : (
                              <span className="text-gray-400">-</span>
                            )}
                          </td>
                          <td className="px-4 py-3">
                            {topSuggestion && (
                              <div className="flex items-center">
                                <div className={`w-2 h-2 rounded-full mr-2 ${
                                  topSuggestion.confidence > 0.7 ? 'bg-green-500' :
                                  topSuggestion.confidence > 0.4 ? 'bg-yellow-500' :
                                  'bg-red-500'
                                }`}></div>
                                {Math.round(topSuggestion.confidence * 100)}%
                              </div>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          {columns.length > 0 && (
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => navigate('/')}
                className="px-4 py-2 text-sm font-medium text-gray-300 bg-gray-700 rounded-lg hover:bg-gray-600"
              >
                Back
              </button>
              <button
                onClick={handleProceedToCrosswalk}
                className="px-6 py-2 text-sm font-medium text-white bg-orange-600 rounded-lg hover:bg-orange-700"
              >
                Proceed to Crosswalk Mapping
                <i className="fas fa-arrow-right ml-2"></i>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UploadScreen;