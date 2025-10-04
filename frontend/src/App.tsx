import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import UploadScreen from './components/UploadScreen';
import CrosswalkTemplateGrid from './components/CrosswalkTemplateGrid';
import MCSReviewScreen from './components/MCSReviewScreen';
import { crosswalkApi, Client, FileGroup, CrosswalkSummary } from './services/crosswalkApi';
import PI20DataModelGrid from './components/PI20DataModelGrid';

function App() {
  const [clients, setClients] = useState<Client[]>([]);
  const [fileGroups, setFileGroups] = useState<FileGroup[]>([]);
  const [selectedClient, setSelectedClient] = useState<string>('');
  const [selectedFileGroup, setSelectedFileGroup] = useState<string>('');
  const [selectedVersion, setSelectedVersion] = useState<string>('V00');
  const [selectedStream, setSelectedStream] = useState<string>('S00');
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

  // Component to wrap crosswalk with filters
  const CrosswalkWithFilters: React.FC = () => (
    <div className="h-screen bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="bg-gray-900 border-b border-gray-700 shadow-sm">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">Crosswalk AI</h1>
              <p className="text-sm text-gray-300 mt-1">
                Manage your data mapping templates with ease
              </p>
            </div>
            
            {summary && (
              <div className="flex items-center space-x-6 text-sm">
                <div className="text-center">
                  <div className="text-lg font-semibold text-orange-600">{summary.total_mappings}</div>
                  <div className="text-gray-300">Mappings</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-green-600">{summary.total_clients}</div>
                  <div className="text-gray-300">Clients</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-purple-600">{summary.total_file_groups}</div>
                  <div className="text-gray-300">File Groups</div>
                </div>
              </div>
            )}
          </div>
        </div>
        
        {/* Filters */}
        <div className="px-6 py-3 bg-gray-800 border-t border-gray-700">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-white">Client:</label>
              <select
                value={selectedClient}
                onChange={(e) => setSelectedClient(e.target.value)}
                className="border border-gray-600 rounded-md px-3 py-1 text-sm bg-gray-700 text-white min-w-[150px]"
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
              <label className="text-sm font-medium text-white">File Group:</label>
              <select
                value={selectedFileGroup}
                onChange={(e) => setSelectedFileGroup(e.target.value)}
                className="border border-gray-600 rounded-md px-3 py-1 text-sm bg-gray-700 text-white min-w-[150px]"
              >
                <option value="">All File Groups</option>
                {fileGroups.map(fg => (
                  <option key={fg.file_group} value={fg.file_group}>
                    {fg.file_group} ({fg.mapping_count})
                  </option>
                ))}
              </select>
            </div>
            
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-white">Version:</label>
              <select
                value={selectedVersion}
                onChange={(e) => setSelectedVersion(e.target.value)}
                className="border border-gray-600 rounded-md px-3 py-1 text-sm bg-gray-700 text-white min-w-[100px]"
              >
                <option value="V00">V00</option>
                <option value="V01">V01</option>
                <option value="V02">V02</option>
                <option value="V03">V03</option>
              </select>
            </div>
            
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-white">Stream:</label>
              <select
                value={selectedStream}
                onChange={(e) => setSelectedStream(e.target.value)}
                className="border border-gray-600 rounded-md px-3 py-1 text-sm bg-gray-700 text-white min-w-[100px]"
              >
                <option value="S00">S00</option>
                <option value="S02">S02</option>
                <option value="S03">S03</option>
                <option value="S04">S04</option>
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
          version={selectedVersion}
          stream={selectedStream}
        />
      </div>
    </div>
  );

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigation />} />
        <Route path="/upload" element={<UploadScreen />} />
        <Route path="/crosswalk" element={<CrosswalkWithFilters />} />
        <Route path="/mcs-review" element={<MCSReviewScreen />} />
        <Route path="/data-model" element={<PI20DataModelGrid />} />
      </Routes>
    </Router>
  );
}

export default App;