import React, { useState, useRef } from 'react';
import { api } from '../services/api';

interface FileUploadProps {
  profileId: number;
}

const FileUpload: React.FC<FileUploadProps> = ({ profileId }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['.csv', '.xlsx', '.xls'];
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    
    if (!validTypes.includes(fileExtension)) {
      setError('Please select a CSV or Excel file (.csv, .xlsx, .xls)');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }

    await uploadFile(file);
  };

  const uploadFile = async (file: File) => {
    setUploading(true);
    setError(null);
    setUploadResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.postFormData(`/profiles/${profileId}/source/ingest-file`, formData);
      
      setUploadResult({
        success: true,
        message: response.message,
        columns_count: response.columns_count,
        columns: response.columns
      });

      // Clear the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

      // Trigger page refresh or emit event to parent
      setTimeout(() => {
        window.location.reload();
      }, 1000);

    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to upload file');
    } finally {
      setUploading(false);
    }
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    event.stopPropagation();
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      
      // Validate file type
      const validTypes = ['.csv', '.xlsx', '.xls'];
      const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      
      if (!validTypes.includes(fileExtension)) {
        setError('Please select a CSV or Excel file (.csv, .xlsx, .xls)');
        return;
      }

      uploadFile(file);
    }
  };

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          uploading 
            ? 'border-blue-300 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400 bg-gray-50'
        }`}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        {uploading ? (
          <div className="space-y-2">
            <i className="fas fa-spinner fa-spin text-blue-600 text-2xl"></i>
            <p className="text-sm text-blue-600 font-medium">Uploading and processing file...</p>
          </div>
        ) : (
          <div className="space-y-3">
            <i className="fas fa-cloud-upload-alt text-gray-400 text-3xl"></i>
            <div>
              <p className="text-sm font-medium text-gray-900 mb-1">
                Drop your file here or click to browse
              </p>
              <p className="text-xs text-gray-600">
                Supports CSV, Excel (.xlsx, .xls) files up to 10MB
              </p>
            </div>
            
            <button
              onClick={() => fileInputRef.current?.click()}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <i className="fas fa-folder-open mr-2"></i>
              Choose File
            </button>
          </div>
        )}
      </div>

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".csv,.xlsx,.xls"
        onChange={handleFileSelect}
        className="hidden"
      />

      {/* Success Message */}
      {uploadResult?.success && (
        <div className="bg-green-50 border border-green-200 rounded-md p-4">
          <div className="flex">
            <i className="fas fa-check-circle text-green-400 mt-0.5 mr-3"></i>
            <div>
              <h4 className="text-sm font-medium text-green-800">Upload Successful</h4>
              <div className="text-sm text-green-700 mt-1">
                <p>{uploadResult.message}</p>
                <p className="mt-1">
                  <span className="font-medium">{uploadResult.columns_count}</span> columns detected
                </p>
              </div>
              
              {uploadResult.columns && uploadResult.columns.length > 0 && (
                <div className="mt-3">
                  <p className="text-sm font-medium text-green-800 mb-2">Detected columns:</p>
                  <div className="flex flex-wrap gap-1">
                    {uploadResult.columns.slice(0, 8).map((column: string, index: number) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800"
                      >
                        {column}
                      </span>
                    ))}
                    {uploadResult.columns.length > 8 && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-600">
                        +{uploadResult.columns.length - 8} more
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <i className="fas fa-exclamation-triangle text-red-400 mt-0.5 mr-3"></i>
            <div>
              <h4 className="text-sm font-medium text-red-800">Upload Failed</h4>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* File Format Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
        <div className="flex">
          <i className="fas fa-info-circle text-blue-400 mt-0.5 mr-2"></i>
          <div className="text-sm">
            <p className="font-medium text-blue-800 mb-1">Supported Formats</p>
            <ul className="text-blue-700 space-y-1">
              <li>• CSV files with comma, semicolon, or tab delimiters</li>
              <li>• Excel files (.xlsx, .xls) - first sheet will be used</li>
              <li>• First row should contain column headers</li>
              <li>• Maximum file size: 10MB</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;
