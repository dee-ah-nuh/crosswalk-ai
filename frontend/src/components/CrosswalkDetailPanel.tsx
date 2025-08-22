import React, { useState } from 'react';
import { CrosswalkMapping } from '../services/crosswalkApi';

interface CrosswalkDetailPanelProps {
  mapping: CrosswalkMapping;
  onUpdateMapping: (updates: Partial<CrosswalkMapping>) => void;
  onClose: () => void;
}

const CrosswalkDetailPanel: React.FC<CrosswalkDetailPanelProps> = ({
  mapping,
  onUpdateMapping,
  onClose
}) => {
  const [formData, setFormData] = useState<Partial<CrosswalkMapping>>({
    source_column_name: mapping.source_column_name || '',
    file_group_name: mapping.file_group_name || '',
    mcdm_column_name: mapping.mcdm_column_name || '',
    mcdm_table: mapping.mcdm_table || '',
    in_model: mapping.in_model || 'Y',
    source_column_formatting: mapping.source_column_formatting || '',
    data_profile_info: mapping.data_profile_info || '',
    skipped_flag: mapping.skipped_flag || false,
    custom_data_type: mapping.custom_data_type || '',
  });

  const handleSave = () => {
    onUpdateMapping(formData);
    onClose();
  };

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-gray-800 shadow-xl z-50 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <h2 className="text-lg font-semibold text-white">Edit Mapping</h2>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white p-1 rounded"
        >
          <i className="fas fa-times"></i>
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Source Column Name */}
        <div>
          <label className="block text-sm font-medium text-white mb-1">
            Source Column Name
          </label>
          <input
            type="text"
            value={formData.source_column_name || ''}
            onChange={(e) => setFormData({...formData, source_column_name: e.target.value})}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
          />
        </div>

        {/* File Group */}
        <div>
          <label className="block text-sm font-medium text-white mb-1">
            File Group
          </label>
          <select
            value={formData.file_group_name || ''}
            onChange={(e) => setFormData({...formData, file_group_name: e.target.value})}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
          >
            <option value="">Select File Group</option>
            <option value="CLAIM">CLAIM</option>
            <option value="CLAIM_LINE">CLAIM_LINE</option>
            <option value="MEMBER">MEMBER</option>
            <option value="PROVIDER">PROVIDER</option>
          </select>
        </div>

        {/* MCDM Column Name */}
        <div>
          <label className="block text-sm font-medium text-white mb-1">
            MCDM Column Name
          </label>
          <input
            type="text"
            value={formData.mcdm_column_name || ''}
            onChange={(e) => setFormData({...formData, mcdm_column_name: e.target.value})}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
          />
        </div>

        {/* MCDM Table */}
        <div>
          <label className="block text-sm font-medium text-white mb-1">
            MCDM Table
          </label>
          <input
            type="text"
            value={formData.mcdm_table || ''}
            onChange={(e) => setFormData({...formData, mcdm_table: e.target.value})}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
          />
        </div>

        {/* In Model */}
        <div>
          <label className="block text-sm font-medium text-white mb-1">
            In Model
          </label>
          <select
            value={formData.in_model || 'Y'}
            onChange={(e) => setFormData({...formData, in_model: e.target.value})}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
          >
            <option value="Y">Y</option>
            <option value="N">N</option>
          </select>
        </div>

        {/* Custom Data Type - only show when In Model is N */}
        {formData.in_model === 'N' && (
          <div>
            <label className="block text-sm font-medium text-white mb-1">
              Data Type <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              value={formData.custom_data_type || ''}
              onChange={(e) => setFormData({...formData, custom_data_type: e.target.value})}
              placeholder="e.g. VARCHAR(50), INTEGER, DATE"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
            />
            <p className="text-xs text-gray-400 mt-1">
              Required when field is not in the model
            </p>
          </div>
        )}

        {/* Source Column Formatting */}
        <div>
          <label className="block text-sm font-medium text-white mb-1">
            Source Column Formatting
          </label>
          <textarea
            value={formData.source_column_formatting || ''}
            onChange={(e) => setFormData({...formData, source_column_formatting: e.target.value})}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
            rows={3}
          />
        </div>

        {/* Data Profile Info */}
        <div>
          <label className="block text-sm font-medium text-white mb-1">
            Data Profile Info
          </label>
          <textarea
            value={formData.data_profile_info || ''}
            onChange={(e) => setFormData({...formData, data_profile_info: e.target.value})}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
            rows={3}
          />
        </div>

        {/* Skipped Flag */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="skipped_flag"
            checked={formData.skipped_flag || false}
            onChange={(e) => setFormData({...formData, skipped_flag: e.target.checked})}
            className="h-4 w-4 text-orange-600 focus:ring-orange-500 bg-gray-700 border-gray-600 rounded"
          />
          <label htmlFor="skipped_flag" className="ml-2 text-sm font-medium text-white">
            Skip this field
          </label>
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-700 flex space-x-3">
        <button
          onClick={onClose}
          className="flex-1 px-4 py-2 border border-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
        >
          Cancel
        </button>
        <button
          onClick={handleSave}
          className="flex-1 px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-orange-500"
        >
          Save Changes
        </button>
      </div>
    </div>
  );
};

export default CrosswalkDetailPanel;