import React, { useState } from 'react';
import { Profile } from '../types';
import FileUpload from './FileUpload';
import SchemaInput from './SchemaInput';

interface ProjectSidebarProps {
  profiles: Profile[];
  selectedProfile: Profile | null;
  onProfileSelect: (profile: Profile) => void;
  onCreateProfile: (name: string, clientId: string) => Promise<void>;
  loading: boolean;
}

const ProjectSidebar: React.FC<ProjectSidebarProps> = ({
  profiles,
  selectedProfile,
  onProfileSelect,
  onCreateProfile,
  loading
}) => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newProfileName, setNewProfileName] = useState('');
  const [newClientId, setNewClientId] = useState('');
  const [activeTab, setActiveTab] = useState<'file' | 'schema'>('file');

  const handleCreateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newProfileName.trim()) {
      await onCreateProfile(newProfileName.trim(), newClientId.trim());
      setNewProfileName('');
      setNewClientId('');
      setShowCreateForm(false);
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Projects</h2>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <i className="fas fa-plus mr-1"></i>
            New
          </button>
        </div>

        {/* Create Project Form */}
        {showCreateForm && (
          <form onSubmit={handleCreateProfile} className="space-y-3 mb-4 p-3 bg-gray-50 rounded-md">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Project Name *
              </label>
              <input
                type="text"
                value={newProfileName}
                onChange={(e) => setNewProfileName(e.target.value)}
                className="w-full px-2 py-1 border border-gray-300 rounded-sm text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter project name"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Client ID
              </label>
              <input
                type="text"
                value={newClientId}
                onChange={(e) => setNewClientId(e.target.value)}
                className="w-full px-2 py-1 border border-gray-300 rounded-sm text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., CCA"
              />
            </div>
            <div className="flex space-x-2">
              <button
                type="submit"
                className="flex-1 px-3 py-1.5 text-xs font-medium text-white bg-blue-600 rounded-sm hover:bg-blue-700 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                Create
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="flex-1 px-3 py-1.5 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded-sm hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>

      {/* Projects List */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="p-4 text-center">
            <i className="fas fa-spinner fa-spin text-gray-400"></i>
            <p className="text-sm text-gray-600 mt-2">Loading projects...</p>
          </div>
        ) : profiles.length === 0 ? (
          <div className="p-4 text-center">
            <i className="fas fa-folder-open text-gray-400 text-2xl mb-2"></i>
            <p className="text-sm text-gray-600">No projects yet</p>
            <p className="text-xs text-gray-500 mt-1">Create your first project above</p>
          </div>
        ) : (
          <div className="space-y-1 p-2">
            {profiles.map((profile) => (
              <button
                key={profile.id}
                onClick={() => onProfileSelect(profile)}
                className={`w-full text-left p-3 rounded-md text-sm transition-colors ${
                  selectedProfile?.id === profile.id
                    ? 'bg-blue-50 border border-blue-200 text-blue-900'
                    : 'hover:bg-gray-50 border border-transparent'
                }`}
              >
                <div className="font-medium text-gray-900">{profile.name}</div>
                {profile.client_id && (
                  <div className="text-xs text-gray-600 mt-1">
                    Client: {profile.client_id}
                  </div>
                )}
                <div className="flex items-center text-xs text-gray-500 mt-1">
                  <i className={`fas ${profile.has_physical_file ? 'fa-file' : 'fa-list'} mr-1`}></i>
                  {profile.has_physical_file ? 'File uploaded' : 'Schema only'}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Data Input Section */}
      {selectedProfile && (
        <div className="border-t border-gray-200 p-4">
          <h3 className="text-sm font-medium text-gray-900 mb-3">Data Input</h3>
          
          {/* Tab Navigation */}
          <div className="flex border-b border-gray-200 mb-3">
            <button
              onClick={() => setActiveTab('file')}
              className={`flex-1 py-2 px-1 text-xs font-medium border-b-2 transition-colors ${
                activeTab === 'file'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <i className="fas fa-upload mr-1"></i>
              Upload File
            </button>
            <button
              onClick={() => setActiveTab('schema')}
              className={`flex-1 py-2 px-1 text-xs font-medium border-b-2 transition-colors ${
                activeTab === 'schema'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <i className="fas fa-list mr-1"></i>
              Schema
            </button>
          </div>

          {/* Tab Content */}
          {activeTab === 'file' ? (
            <FileUpload profileId={selectedProfile.id} />
          ) : (
            <SchemaInput profileId={selectedProfile.id} />
          )}
        </div>
      )}
    </div>
  );
};

export default ProjectSidebar;
