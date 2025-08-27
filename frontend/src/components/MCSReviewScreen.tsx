import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { crosswalkApi, CrosswalkMapping } from '../services/crosswalkApi';

interface MCSReviewScreenProps {}

interface ReviewStats {
  total_mappings: number;
  ready_for_approval: number;
  pending_review: number;
  has_issues: number;
  approved_count: number;
}

const MCSReviewScreen: React.FC<MCSReviewScreenProps> = () => {
  const navigate = useNavigate();
  const [mappings, setMappings] = useState<CrosswalkMapping[]>([]);
  const [stats, setStats] = useState<ReviewStats>({
    total_mappings: 0,
    ready_for_approval: 0,
    pending_review: 0,
    has_issues: 0,
    approved_count: 0
  });
  const [selectedMappings, setSelectedMappings] = useState<Set<number>>(new Set());
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMappings();
  }, []);

  const loadMappings = async () => {
    setLoading(true);
    try {
      const data = await crosswalkApi.getCrosswalkMappings({ limit: 500 });
      setMappings(data);
      
      // Calculate stats
      const ready = data.filter((m: CrosswalkMapping) => 
        m.mcdm_column_name && (m.mcdm_table || m.mcdm_table_name) && !m.skipped_flag
      ).length;
      const pending = data.filter((m: CrosswalkMapping) => 
        !m.mcdm_column_name && !m.skipped_flag
      ).length;
      const issues = data.filter((m: CrosswalkMapping) => 
        (!m.mcdm_column_name && !m.skipped_flag) || (!m.data_type)
      ).length;

      setStats({
        total_mappings: data.length,
        ready_for_approval: ready,
        pending_review: pending,
        has_issues: issues,
        approved_count: 0 // Would come from actual approval status
      });
    } catch (error) {
      console.error('Error loading mappings:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (mapping: CrosswalkMapping) => {
    if (mapping.skipped_flag) {
      return <span className="px-2 py-1 text-xs font-medium bg-gray-600 text-gray-300 rounded">Skipped</span>;
    }
    if (mapping.mcdm_column_name && (mapping.mcdm_table || mapping.mcdm_table_name)) {
      return <span className="px-2 py-1 text-xs font-medium bg-green-600 text-white rounded">Ready</span>;
    }
    return <span className="px-2 py-1 text-xs font-medium bg-yellow-600 text-white rounded">Pending</span>;
  };

  const handleSelectMapping = (id: number) => {
    const newSelected = new Set(selectedMappings);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedMappings(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedMappings.size === filteredMappings.length) {
      setSelectedMappings(new Set());
    } else {
      setSelectedMappings(new Set(filteredMappings.map(m => m.id)));
    }
  };

  const handleApproveSelected = () => {
    if (selectedMappings.size === 0) return;
    
    const confirmed = window.confirm(
      `Are you sure you want to approve ${selectedMappings.size} selected mappings for production deployment?`
    );
    
    if (confirmed) {
      alert(`✅ Approved ${selectedMappings.size} mappings for production!`);
      setSelectedMappings(new Set());
    }
  };

  const handleRequestRevisions = () => {
    if (selectedMappings.size === 0) return;
    
    const reason = prompt('Please provide a reason for requesting revisions:');
    if (reason) {
      alert(`📝 Sent ${selectedMappings.size} mappings back for revision:\nReason: ${reason}`);
      setSelectedMappings(new Set());
    }
  };

  const filteredMappings = mappings.filter(mapping => {
    switch (filterStatus) {
      case 'ready':
        return mapping.mcdm_column_name && (mapping.mcdm_table || mapping.mcdm_table_name) && !mapping.skipped_flag;
      case 'pending':
        return !mapping.mcdm_column_name && !mapping.skipped_flag;
      case 'issues':
        return (!mapping.mcdm_column_name && !mapping.skipped_flag) || (!mapping.data_type);
      case 'skipped':
        return mapping.skipped_flag;
      default:
        return true;
    }
  });

  if (loading) {
    return (
      <div className="h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
          <p className="text-white">Loading mappings for review...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="bg-gray-900 border-b border-gray-700 shadow-sm">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">MCS Review Dashboard</h1>
              <p className="text-sm text-gray-300 mt-1">
                Review and approve crosswalk mappings for production deployment
              </p>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={() => navigate('/crosswalk')}
                className="px-4 py-2 text-sm font-medium text-gray-300 bg-gray-700 rounded-lg hover:bg-gray-600"
              >
                <i className="fas fa-arrow-left mr-2"></i>
                Back to Crosswalk
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Dashboard */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-white">{stats.total_mappings}</div>
            <div className="text-xs text-gray-300">Total Mappings</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400">{stats.ready_for_approval}</div>
            <div className="text-xs text-gray-300">Ready</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-400">{stats.pending_review}</div>
            <div className="text-xs text-gray-300">Pending</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-400">{stats.has_issues}</div>
            <div className="text-xs text-gray-300">Issues</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-400">{stats.approved_count}</div>
            <div className="text-xs text-gray-300">Approved</div>
          </div>
        </div>
      </div>

      {/* Action Bar */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-white">Filter:</label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-3 py-1 bg-gray-700 border border-gray-600 rounded text-white text-sm"
              >
                <option value="all">All ({mappings.length})</option>
                <option value="ready">Ready ({stats.ready_for_approval})</option>
                <option value="pending">Pending ({stats.pending_review})</option>
                <option value="issues">Issues ({stats.has_issues})</option>
                <option value="skipped">Skipped</option>
              </select>
            </div>
            
            <div className="text-sm text-gray-300">
              {selectedMappings.size} selected
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleApproveSelected}
              disabled={selectedMappings.size === 0}
              className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <i className="fas fa-check mr-2"></i>
              Approve Selected ({selectedMappings.size})
            </button>
            
            <button
              onClick={handleRequestRevisions}
              disabled={selectedMappings.size === 0}
              className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <i className="fas fa-times mr-2"></i>
              Request Revisions
            </button>
          </div>
        </div>
      </div>

      {/* Mappings Table */}
      <div className="flex-1 overflow-auto">
        <div className="min-w-full bg-gray-800">
          <table className="min-w-full divide-y divide-gray-700">
            <thead className="bg-gray-700 sticky top-0">
              <tr>
                <th className="px-4 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={selectedMappings.size === filteredMappings.length && filteredMappings.length > 0}
                    onChange={handleSelectAll}
                    className="rounded border-gray-300"
                  />
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase">Source Column</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase">Target Mapping</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase">Data Type</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase">File Group</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase">Notes</th>
              </tr>
            </thead>
            <tbody className="bg-gray-800 divide-y divide-gray-700">
              {filteredMappings.map((mapping) => (
                <tr 
                  key={mapping.id}
                  className={`hover:bg-gray-700 cursor-pointer ${
                    selectedMappings.has(mapping.id) ? 'bg-gray-700 border-l-4 border-orange-500' : ''
                  }`}
                  onClick={() => handleSelectMapping(mapping.id)}
                >
                  <td className="px-4 py-4" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="checkbox"
                      checked={selectedMappings.has(mapping.id)}
                      onChange={() => handleSelectMapping(mapping.id)}
                      className="rounded border-gray-300"
                    />
                  </td>
                  <td className="px-4 py-4">
                    <div className="font-medium text-white">{mapping.source_column_name}</div>
                    <div className="text-sm text-gray-400">Order: {mapping.source_column_order}</div>
                  </td>
                  <td className="px-4 py-4">
                    {(mapping.mcdm_table || mapping.mcdm_table_name) && mapping.mcdm_column_name ? (
                      <div className="text-green-400">
                        {mapping.mcdm_table || mapping.mcdm_table_name}.{mapping.mcdm_column_name}
                      </div>
                    ) : (
                      <div className="text-gray-400">Not mapped</div>
                    )}
                  </td>
                  <td className="px-4 py-4 text-white">
                    {mapping.data_type || '-'}
                  </td>
                  <td className="px-4 py-4">
                    {getStatusBadge(mapping)}
                  </td>
                  <td className="px-4 py-4">
                    <span className="px-2 py-1 text-xs font-medium bg-blue-600 text-white rounded">
                      {mapping.file_group_name}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-sm text-gray-300 max-w-xs truncate">
                    {mapping.description || mapping.data_profile_info || '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {filteredMappings.length === 0 && (
            <div className="text-center py-12 text-gray-400">
              No mappings match the selected filter.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MCSReviewScreen;