import React, { useState, useEffect } from 'react';
import ProjectSidebar from './components/ProjectSidebar';
import CrosswalkGrid from './components/CrosswalkGrid';
import DetailPanel from './components/DetailPanel';
import { useProfiles } from './hooks/useProfiles';
import { useCrosswalk } from './hooks/useCrosswalk';
import { Profile } from './types';

const App: React.FC = () => {
  const [selectedProfile, setSelectedProfile] = useState<Profile | null>(null);
  const [selectedSourceColumn, setSelectedSourceColumn] = useState<any>(null);
  
  const { profiles, loading: profilesLoading, createProfile, refreshProfiles } = useProfiles();
  const { 
    mappings, 
    loading: mappingsLoading, 
    updateMappings, 
    validationSummary,
    refreshMappings 
  } = useCrosswalk(selectedProfile?.id);

  useEffect(() => {
    refreshProfiles();
  }, []);

  useEffect(() => {
    if (selectedProfile) {
      refreshMappings();
    }
  }, [selectedProfile]);

  const handleProfileSelect = (profile: Profile) => {
    setSelectedProfile(profile);
    setSelectedSourceColumn(null);
  };

  const handleRowSelect = (mapping: any) => {
    setSelectedSourceColumn(mapping);
  };

  const handleMappingsUpdate = async (updatedMappings: any[]) => {
    if (selectedProfile) {
      await updateMappings(updatedMappings);
      await refreshMappings();
    }
  };

  return (
    <div className="h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <i className="fas fa-exchange-alt text-blue-600 text-xl"></i>
            <h1 className="text-xl font-semibold text-gray-900">
              Interactive Crosswalk & ETL Helper
            </h1>
          </div>
          
          {selectedProfile && validationSummary && (
            <div className="flex items-center space-x-4 text-sm">
              <div className="flex items-center space-x-2">
                <span className="text-gray-600">Mapping Progress:</span>
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${validationSummary.mapping_percentage}%` }}
                  ></div>
                </div>
                <span className="font-medium text-gray-900">
                  {validationSummary.mapping_percentage}%
                </span>
              </div>
              
              <div className="flex items-center space-x-1 text-green-600">
                <i className="fas fa-check-circle"></i>
                <span>{validationSummary.mapped_columns} mapped</span>
              </div>
              
              <div className="flex items-center space-x-1 text-orange-600">
                <i className="fas fa-exclamation-triangle"></i>
                <span>{validationSummary.unmapped_columns} unmapped</span>
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <div className="sidebar bg-white border-r border-gray-200 flex-shrink-0">
          <ProjectSidebar
            profiles={profiles}
            selectedProfile={selectedProfile}
            onProfileSelect={handleProfileSelect}
            onCreateProfile={createProfile}
            loading={profilesLoading}
          />
        </div>

        {/* Center Grid */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {selectedProfile ? (
            <CrosswalkGrid
              profileId={selectedProfile.id}
              mappings={mappings}
              loading={mappingsLoading}
              onMappingsUpdate={handleMappingsUpdate}
              onRowSelect={handleRowSelect}
              selectedRow={selectedSourceColumn}
            />
          ) : (
            <div className="flex-1 flex items-center justify-center bg-gray-50">
              <div className="text-center">
                <i className="fas fa-project-diagram text-gray-400 text-4xl mb-4"></i>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Select a Project
                </h3>
                <p className="text-gray-600 max-w-sm">
                  Choose a project from the sidebar or create a new one to start mapping your data columns.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Right Detail Panel */}
        {selectedProfile && (
          <div className="detail-panel bg-white border-l border-gray-200 flex-shrink-0">
            <DetailPanel
              profile={selectedProfile}
              selectedColumn={selectedSourceColumn}
              validationSummary={validationSummary}
              onRefresh={refreshMappings}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
