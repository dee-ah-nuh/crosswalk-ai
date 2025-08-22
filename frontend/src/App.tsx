import React, { useState, useEffect } from 'react';
import CrosswalkTemplateGrid from './components/CrosswalkTemplateGrid';
import { crosswalkApi, Client, FileGroup, CrosswalkSummary } from './services/crosswalkApi';

function App() {
  const [clients, setClients] = useState<Client[]>([]);
  const [fileGroups, setFileGroups] = useState<FileGroup[]>([]);
  const [selectedClient, setSelectedClient] = useState<string>('');
  const [selectedFileGroup, setSelectedFileGroup] = useState<string>('');
  const [summary, setSummary] = useState<CrosswalkSummary | null>(null);
  const [loading, setLoading] = useState(false);

  // Load initial data
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const [clientsData, fileGroupsData, summaryData] = await Promise.all([
          crosswalkApi.getClients(),
          crosswalkApi.getFileGroups(),
          crosswalkApi.getSummary()
        ]);
        
        setClients(clientsData);
        setFileGroups(fileGroupsData);
        setSummary(summaryData);
        
        // Auto-select first client if available
        if (clientsData.length > 0 && !selectedClient) {
          setSelectedClient(clientsData[0].client_id);
        }
      } catch (error) {
        console.error('Error loading data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Update file groups when client changes
  useEffect(() => {
    const loadFileGroups = async () => {
      if (selectedClient) {
        try {
          const fileGroupsData = await crosswalkApi.getFileGroups(selectedClient);
          setFileGroups(fileGroupsData);
          
          // Auto-select first file group if available
          if (fileGroupsData.length > 0) {
            setSelectedFileGroup(fileGroupsData[0].file_group);
          }
        } catch (error) {
          console.error('Error loading file groups:', error);
        }
      } else {
        const allFileGroups = await crosswalkApi.getFileGroups();
        setFileGroups(allFileGroups);
      }
    };

    loadFileGroups();
  }, [selectedClient]);

  return (
    <div className="h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Interactive Crosswalk & ETL Helper</h1>
              <p className="text-sm text-gray-600 mt-1">
                Manage your data mapping templates with ease
              </p>
            </div>
            
            {summary && (
              <div className="flex items-center space-x-6 text-sm">
                <div className="text-center">
                  <div className="text-lg font-semibold text-orange-600">{summary.total_mappings}</div>
                  <div className="text-gray-500">Mappings</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-green-600">{summary.total_clients}</div>
                  <div className="text-gray-500">Clients</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-purple-600">{summary.total_file_groups}</div>
                  <div className="text-gray-500">File Groups</div>
                </div>
              </div>
            )}
          </div>
        </div>
        
        {/* Filters */}
        <div className="px-6 py-3 bg-gray-50 border-t">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-900">Client:</label>
              <select
                value={selectedClient}
                onChange={(e) => setSelectedClient(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-1 text-sm bg-white min-w-[150px]"
              >
                <option value="">All Clients</option>
                {clients.map(client => (
                  <option key={client.client_id} value={client.client_id}>
                    {client.client_id} ({client.mapping_count})
                  </option>
                ))}
              </select>
            </div>
            
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-900">File Group:</label>
              <select
                value={selectedFileGroup}
                onChange={(e) => setSelectedFileGroup(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-1 text-sm bg-white min-w-[150px]"
              >
                <option value="">All File Groups</option>
                {fileGroups.map(fg => (
                  <option key={fg.file_group} value={fg.file_group}>
                    {fg.file_group} ({fg.mapping_count})
                  </option>
                ))}
              </select>
            </div>

            <div className="flex-1"></div>
            
            {loading && (
              <div className="flex items-center text-gray-500 text-sm">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-500 mr-2"></div>
                Loading...
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <CrosswalkTemplateGrid
          clientId={selectedClient || undefined}
          fileGroup={selectedFileGroup || undefined}
        />
      </div>
    </div>
  );
}

export default App;