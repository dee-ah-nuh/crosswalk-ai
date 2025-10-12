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
  const [showRevisionModal, setShowRevisionModal] = useState(false);
  const [revisionReason, setRevisionReason] = useState('');
  const [revisionPriority, setRevisionPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [approvalComments, setApprovalComments] = useState('');

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
    setShowApprovalModal(true);
  };

  const handleSendApprovalNotification = async () => {
    if (selectedMappings.size === 0) return;
    
    try {
      // TODO: Call actual API to send approval email
      const approvalData = {
        mappingIds: Array.from(selectedMappings),
        comments: approvalComments,
        approvedBy: 'MCS Reviewer',
        approvalDate: new Date().toISOString(),
        selectedCount: selectedMappings.size
      };
      
      console.log('Sending approval notification:', approvalData);
      
      // Close modal and reset state
      setShowApprovalModal(false);
      setApprovalComments('');
      setSelectedMappings(new Set());
      
      // Silent success - UI changes provide feedback
    } catch (error) {
      console.error('Error sending approval notification:', error);
      alert('Failed to send approval notification. Please try again.');
    }
  };

  const handleCloseApprovalModal = () => {
    setShowApprovalModal(false);
    setApprovalComments('');
  };

  const handleRequestRevisions = () => {
    if (selectedMappings.size === 0) return;
    setShowRevisionModal(true);
  };

  const handleSendRevisionRequest = async () => {
    if (!revisionReason.trim()) return;
    
    try {
      // TODO: Call actual API to send revision request email
      const revisionData = {
        mappingIds: Array.from(selectedMappings),
        reason: revisionReason,
        priority: revisionPriority,
        requestedBy: 'MCS Reviewer',
        requestDate: new Date().toISOString(),
        selectedCount: selectedMappings.size
      };
      
      console.log('Sending revision request:', revisionData);
      
      // Close modal and reset state
      setShowRevisionModal(false);
      setRevisionReason('');
      setRevisionPriority('medium');
      setSelectedMappings(new Set());
      
      // Silent success - the modal closing and selection clearing is sufficient feedback
    } catch (error) {
      console.error('Error sending revision request:', error);
      alert('Failed to send revision request. Please try again.');
    }
  };

  const handleCloseRevisionModal = () => {
    setShowRevisionModal(false);
    setRevisionReason('');
    setRevisionPriority('medium');
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

      {/* Revision Request Modal */}
      {showRevisionModal && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
            {/* Email Header */}
            <div className="bg-gradient-to-r from-red-600 to-red-700 px-6 py-4 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold flex items-center">
                    <i className="fas fa-exclamation-triangle mr-2"></i>
                    Revision Request
                  </h2>
                  <p className="text-red-100 text-sm mt-1">
                    Request changes for selected crosswalk mappings
                  </p>
                </div>
                <button
                  onClick={handleCloseRevisionModal}
                  className="text-red-100 hover:text-white transition-colors"
                >
                  <i className="fas fa-times text-xl"></i>
                </button>
              </div>
            </div>

            {/* Email Body */}
            <div className="p-6">
              {/* Email Meta Info */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6 border-l-4 border-red-500">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">To:</span>
                    <span className="ml-2 text-gray-600">Crosswalk Team</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">From:</span>
                    <span className="ml-2 text-gray-600">MCS Reviewer</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Subject:</span>
                    <span className="ml-2 text-gray-600">Revision Required - {selectedMappings.size} Mappings</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Date:</span>
                    <span className="ml-2 text-gray-600">{new Date().toLocaleDateString()}</span>
                  </div>
                </div>
              </div>

              {/* Selected Mappings Summary */}
              <div className="mb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-3">
                  Affected Mappings ({selectedMappings.size})
                </h3>
                <div className="bg-gray-50 rounded-md p-3 max-h-32 overflow-y-auto">
                  <div className="text-sm text-gray-600">
                    {Array.from(selectedMappings).map(id => {
                      const mapping = mappings.find(m => m.id === id);
                      return mapping ? (
                        <div key={id} className="flex justify-between py-1 border-b border-gray-200 last:border-b-0">
                          <span className="font-medium">{mapping.source_column_name}</span>
                          <span className="text-gray-500">{mapping.file_group_name}</span>
                        </div>
                      ) : null;
                    })}
                  </div>
                </div>
              </div>

              {/* Priority Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Priority Level
                </label>
                <div className="flex space-x-4">
                  {[
                    { value: 'low', label: 'Low', color: 'bg-green-100 text-green-800 border-green-300' },
                    { value: 'medium', label: 'Medium', color: 'bg-yellow-100 text-yellow-800 border-yellow-300' },
                    { value: 'high', label: 'High', color: 'bg-red-100 text-red-800 border-red-300' }
                  ].map((priority) => (
                    <label key={priority.value} className="flex items-center cursor-pointer">
                      <input
                        type="radio"
                        name="priority"
                        value={priority.value}
                        checked={revisionPriority === priority.value}
                        onChange={(e) => setRevisionPriority(e.target.value as 'low' | 'medium' | 'high')}
                        className="sr-only"
                      />
                      <span className={`px-3 py-2 rounded-md border text-sm font-medium transition-all ${
                        revisionPriority === priority.value 
                          ? priority.color + ' ring-2 ring-offset-2 ring-gray-400' 
                          : 'bg-gray-100 text-gray-600 border-gray-300 hover:bg-gray-200'
                      }`}>
                        {priority.label}
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Revision Reason */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Revision Details <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={revisionReason}
                  onChange={(e) => setRevisionReason(e.target.value)}
                  placeholder="Please provide specific details about what needs to be revised and why. Include any guidance or suggestions for the team..."
                  rows={6}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-red-500 resize-none"
                />
                <div className="mt-1 text-sm text-gray-500">
                  {revisionReason.length}/500 characters
                </div>
              </div>

              {/* Common Revision Templates */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Quick Templates
                </label>
                <div className="grid grid-cols-1 gap-2">
                  {[
                    "Missing required MCDM column mapping",
                    "Data type mismatch - please verify source data format",
                    "Business logic needs clarification",
                    "Source column formatting requires adjustment"
                  ].map((template, index) => (
                    <button
                      key={index}
                      onClick={() => setRevisionReason(template)}
                      className="text-left px-3 py-2 text-sm text-gray-600 bg-gray-50 hover:bg-gray-100 rounded border border-gray-200 transition-colors"
                    >
                      {template}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Email Footer/Actions */}
            <div className="bg-gray-50 px-6 py-4 flex justify-between items-center">
              <div className="text-sm text-gray-500">
                This will notify the crosswalk team via email
              </div>
              <div className="flex space-x-3">
                <button
                  onClick={handleCloseRevisionModal}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSendRevisionRequest}
                  disabled={!revisionReason.trim()}
                  className="px-6 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
                >
                  <i className="fas fa-paper-plane mr-2"></i>
                  Send Revision Request
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Approval Notification Modal */}
      {showApprovalModal && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
            {/* Email Header */}
            <div className="bg-gradient-to-r from-green-600 to-green-700 px-6 py-4 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold flex items-center">
                    <i className="fas fa-check-circle mr-2"></i>
                    Production Approval
                  </h2>
                  <p className="text-green-100 text-sm mt-1">
                    Approve selected mappings for production deployment
                  </p>
                </div>
                <button
                  onClick={handleCloseApprovalModal}
                  className="text-green-100 hover:text-white transition-colors"
                >
                  <i className="fas fa-times text-xl"></i>
                </button>
              </div>
            </div>

            {/* Email Body */}
            <div className="p-6">
              {/* Email Meta Info */}
              <div className="bg-green-50 rounded-lg p-4 mb-6 border-l-4 border-green-500">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">To:</span>
                    <span className="ml-2 text-gray-600">Development Team, QA Team</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">From:</span>
                    <span className="ml-2 text-gray-600">MCS Reviewer</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Subject:</span>
                    <span className="ml-2 text-gray-600">✅ APPROVED - {selectedMappings.size} Mappings for Production</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Date:</span>
                    <span className="ml-2 text-gray-600">{new Date().toLocaleDateString()}</span>
                  </div>
                </div>
              </div>

              {/* Approval Summary */}
              <div className="bg-green-100 border border-green-200 rounded-lg p-4 mb-6">
                <div className="flex items-center mb-2">
                  <i className="fas fa-thumbs-up text-green-600 mr-2"></i>
                  <h3 className="font-medium text-green-800">Approval Status: APPROVED</h3>
                </div>
                <p className="text-green-700 text-sm">
                  The following {selectedMappings.size} crosswalk mappings have been reviewed and approved for production deployment.
                </p>
              </div>

              {/* Approved Mappings Summary */}
              <div className="mb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-3">
                  Approved Mappings ({selectedMappings.size})
                </h3>
                <div className="bg-gray-50 rounded-md p-3 max-h-32 overflow-y-auto">
                  <div className="text-sm text-gray-600">
                    {Array.from(selectedMappings).map(id => {
                      const mapping = mappings.find(m => m.id === id);
                      return mapping ? (
                        <div key={id} className="flex justify-between py-1 border-b border-gray-200 last:border-b-0">
                          <span className="font-medium">{mapping.source_column_name}</span>
                          <div className="flex items-center space-x-2">
                            <span className="text-gray-500">{mapping.file_group_name}</span>
                            <i className="fas fa-check text-green-500 text-xs"></i>
                          </div>
                        </div>
                      ) : null;
                    })}
                  </div>
                </div>
              </div>

              {/* Deployment Instructions */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <h4 className="font-medium text-blue-800 mb-2">Next Steps:</h4>
                <ul className="text-blue-700 text-sm space-y-1">
                  <li>• Mappings are ready for production deployment</li>
                  <li>• Please coordinate with DevOps for deployment scheduling</li>
                  <li>• Post-deployment validation recommended</li>
                  <li>• Monitor data quality metrics after deployment</li>
                </ul>
              </div>

              {/* Approval Comments */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Approval Comments (Optional)
                </label>
                <textarea
                  value={approvalComments}
                  onChange={(e) => setApprovalComments(e.target.value)}
                  placeholder="Add any additional notes, deployment instructions, or comments for the team..."
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-green-500 resize-none"
                />
                <div className="mt-1 text-sm text-gray-500">
                  {approvalComments.length}/300 characters
                </div>
              </div>

              {/* Quick Comment Templates */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Quick Comments
                </label>
                <div className="grid grid-cols-1 gap-2">
                  {[
                    "All mappings validated and ready for production deployment",
                    "Please deploy during next maintenance window",
                    "Excellent work - all mappings meet quality standards",
                    "Deploy with standard monitoring and validation procedures"
                  ].map((template, index) => (
                    <button
                      key={index}
                      onClick={() => setApprovalComments(template)}
                      className="text-left px-3 py-2 text-sm text-gray-600 bg-gray-50 hover:bg-gray-100 rounded border border-gray-200 transition-colors"
                    >
                      {template}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Email Footer/Actions */}
            <div className="bg-gray-50 px-6 py-4 flex justify-between items-center">
              <div className="text-sm text-gray-500">
                This will notify the development and QA teams
              </div>
              <div className="flex space-x-3">
                <button
                  onClick={handleCloseApprovalModal}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSendApprovalNotification}
                  className="px-6 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 transition-colors flex items-center"
                >
                  <i className="fas fa-check-circle mr-2"></i>
                  Send Approval Notification
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MCSReviewScreen;