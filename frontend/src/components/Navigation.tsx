import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const Navigation: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const navigationItems = [
    {
      path: '/upload',
      label: 'Upload Data',
      icon: 'fas fa-cloud-upload-alt',
      description: 'Upload source files & configure project'
    },
    {
      path: '/crosswalk',
      label: 'Crosswalk Mapping',
      icon: 'fas fa-exchange-alt',
      description: 'Map source columns to data model'
    },
    {
      path: '/mcs-review',
      label: 'MCS Review',
      icon: 'fas fa-clipboard-check',
      description: 'Review & approve mappings'
    }
  ];

  const currentStep = navigationItems.findIndex(item => item.path === location.pathname);

  return (
    <div className="h-screen bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="bg-gray-900 border-b border-gray-700 shadow-sm">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">Crosswalk AI</h1>
              <p className="text-sm text-gray-300 mt-1">
                Intelligent healthcare data mapping with 827-field data model
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="px-3 py-1 bg-green-600 text-white rounded-full text-sm">
                <i className="fas fa-brain mr-2"></i>
                AI-Powered
              </div>
              <div className="px-3 py-1 bg-orange-600 text-white rounded-full text-sm">
                827 Fields Ready
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="max-w-4xl mx-auto">
          
          {/* Workflow Steps */}
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-white mb-4">Healthcare Data Crosswalk Workflow</h2>
            <p className="text-gray-300">
              Choose your workflow step or follow the complete process from upload to production
            </p>
          </div>

          {/* Step Navigation Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {navigationItems.map((item, index) => (
              <div
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`relative bg-gray-800 rounded-xl p-6 cursor-pointer transition-all duration-200 border-2 ${
                  location.pathname === item.path
                    ? 'border-orange-500 bg-gray-700 shadow-lg'
                    : 'border-gray-600 hover:border-gray-500 hover:bg-gray-700'
                }`}
              >
                {/* Step Number */}
                <div className={`absolute -top-3 -left-3 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                  index <= currentStep
                    ? 'bg-orange-600 text-white'
                    : 'bg-gray-600 text-gray-300'
                }`}>
                  {index + 1}
                </div>

                {/* Card Content */}
                <div className="text-center">
                  <div className={`text-4xl mb-4 ${
                    location.pathname === item.path ? 'text-orange-500' : 'text-gray-400'
                  }`}>
                    <i className={item.icon}></i>
                  </div>
                  
                  <h3 className="text-lg font-semibold text-white mb-2">
                    {item.label}
                  </h3>
                  
                  <p className="text-sm text-gray-400 mb-4">
                    {item.description}
                  </p>

                  {/* Status Indicator */}
                  {location.pathname === item.path ? (
                    <div className="inline-flex items-center px-3 py-1 rounded-full bg-orange-600 text-white text-xs">
                      <i className="fas fa-circle mr-2"></i>
                      Current Step
                    </div>
                  ) : index < currentStep ? (
                    <div className="inline-flex items-center px-3 py-1 rounded-full bg-green-600 text-white text-xs">
                      <i className="fas fa-check mr-2"></i>
                      Completed
                    </div>
                  ) : (
                    <div className="inline-flex items-center px-3 py-1 rounded-full bg-gray-600 text-gray-300 text-xs">
                      <i className="fas fa-clock mr-2"></i>
                      Pending
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Workflow Flow Diagram */}
          <div className="bg-gray-800 rounded-xl p-6 mb-8">
            <h3 className="text-lg font-semibold text-white mb-4 text-center">
              Complete Workflow Process
            </h3>
            
            <div className="flex items-center justify-center space-x-4">
              <div className="flex items-center">
                <div className="w-12 h-12 rounded-full bg-blue-600 flex items-center justify-center text-white">
                  <i className="fas fa-cloud-upload-alt"></i>
                </div>
                <div className="ml-3 text-sm">
                  <div className="font-medium text-white">Upload</div>
                  <div className="text-gray-400">Source Data</div>
                </div>
              </div>
              
              <div className="w-8 h-1 bg-gray-600"></div>
              
              <div className="flex items-center">
                <div className="w-12 h-12 rounded-full bg-orange-600 flex items-center justify-center text-white">
                  <i className="fas fa-brain"></i>
                </div>
                <div className="ml-3 text-sm">
                  <div className="font-medium text-white">AI Mapping</div>
                  <div className="text-gray-400">Auto-suggest</div>
                </div>
              </div>
              
              <div className="w-8 h-1 bg-gray-600"></div>
              
              <div className="flex items-center">
                <div className="w-12 h-12 rounded-full bg-purple-600 flex items-center justify-center text-white">
                  <i className="fas fa-exchange-alt"></i>
                </div>
                <div className="ml-3 text-sm">
                  <div className="font-medium text-white">Crosswalk</div>
                  <div className="text-gray-400">Review & Map</div>
                </div>
              </div>
              
              <div className="w-8 h-1 bg-gray-600"></div>
              
              <div className="flex items-center">
                <div className="w-12 h-12 rounded-full bg-green-600 flex items-center justify-center text-white">
                  <i className="fas fa-clipboard-check"></i>
                </div>
                <div className="ml-3 text-sm">
                  <div className="font-medium text-white">MCS Review</div>
                  <div className="text-gray-400">Approve</div>
                </div>
              </div>
              
              <div className="w-8 h-1 bg-gray-600"></div>
              
              <div className="flex items-center">
                <div className="w-12 h-12 rounded-full bg-blue-500 flex items-center justify-center text-white">
                  <i className="fas fa-rocket"></i>
                </div>
                <div className="ml-3 text-sm">
                  <div className="font-medium text-white">Production</div>
                  <div className="text-gray-400">Deploy</div>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="text-center">
            <h3 className="text-lg font-medium text-white mb-4">Quick Actions</h3>
            <div className="flex justify-center space-x-4">
              <button
                onClick={() => navigate('/upload')}
                className="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
              >
                <i className="fas fa-play mr-2"></i>
                Start New Project
              </button>
              <button
                onClick={() => navigate('/crosswalk')}
                className="px-6 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors border border-gray-600"
              >
                <i className="fas fa-list mr-2"></i>
                View Existing Mappings
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Navigation;