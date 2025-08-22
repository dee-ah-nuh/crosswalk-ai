import React, { useState } from 'react';
import { api } from '../services/api';

interface SchemaInputProps {
  profileId: number;
}

const SchemaInput: React.FC<SchemaInputProps> = ({ profileId }) => {
  const [schemaText, setSchemaText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!schemaText.trim()) {
      setError('Please enter column names');
      return;
    }

    setSubmitting(true);
    setError(null);
    setResult(null);

    try {
      // Parse column names from text (one per line)
      const columns = schemaText
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0);

      if (columns.length === 0) {
        throw new Error('No valid column names found');
      }

      const response = await api.post(`/profiles/${profileId}/source/ingest-schema`, {
        columns: columns
      });
      
      setResult({
        success: true,
        message: response.message,
        columns_count: response.columns_count,
        columns: response.columns
      });

      // Clear the input after successful submission
      setSchemaText('');

      // Trigger page refresh or emit event to parent
      setTimeout(() => {
        window.location.reload();
      }, 1000);

    } catch (error: any) {
      setError(error.response?.data?.detail || error.message || 'Failed to process schema');
    } finally {
      setSubmitting(false);
    }
  };

  const handleLoadExample = () => {
    const exampleSchema = `PATIENT_ID
CLAIMTYPE
SVC_DT
CHARGE
NPI_NUM
DR_NAME
PLAN_CODE`;
    setSchemaText(exampleSchema);
  };

  const handleClear = () => {
    setSchemaText('');
    setResult(null);
    setError(null);
  };

  return (
    <div className="space-y-4">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Schema Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Column Names
            <span className="text-xs text-gray-500 ml-1">(one per line)</span>
          </label>
          <textarea
            value={schemaText}
            onChange={(e) => setSchemaText(e.target.value)}
            rows={8}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm font-mono focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter column names, one per line:&#10;&#10;PATIENT_ID&#10;CLAIM_TYPE&#10;SERVICE_DATE&#10;AMOUNT"
          />
          
          <div className="flex justify-between items-center mt-2">
            <div className="text-xs text-gray-500">
              {schemaText.split('\n').filter(line => line.trim()).length} columns
            </div>
            
            <div className="space-x-2">
              <button
                type="button"
                onClick={handleLoadExample}
                className="text-xs text-blue-600 hover:text-blue-800 underline"
              >
                Load Example
              </button>
              
              <button
                type="button"
                onClick={handleClear}
                className="text-xs text-gray-600 hover:text-gray-800 underline"
              >
                Clear
              </button>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={submitting || !schemaText.trim()}
          className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {submitting ? (
            <>
              <i className="fas fa-spinner fa-spin mr-2"></i>
              Processing Schema...
            </>
          ) : (
            <>
              <i className="fas fa-check mr-2"></i>
              Import Schema
            </>
          )}
        </button>
      </form>

      {/* Success Message */}
      {result?.success && (
        <div className="bg-green-50 border border-green-200 rounded-md p-4">
          <div className="flex">
            <i className="fas fa-check-circle text-green-400 mt-0.5 mr-3"></i>
            <div>
              <h4 className="text-sm font-medium text-green-800">Schema Imported</h4>
              <div className="text-sm text-green-700 mt-1">
                <p>{result.message}</p>
                <p className="mt-1">
                  <span className="font-medium">{result.columns_count}</span> columns imported
                </p>
              </div>
              
              {result.columns && result.columns.length > 0 && (
                <div className="mt-3">
                  <p className="text-sm font-medium text-green-800 mb-2">Imported columns:</p>
                  <div className="flex flex-wrap gap-1">
                    {result.columns.slice(0, 8).map((column: string, index: number) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800"
                      >
                        {column}
                      </span>
                    ))}
                    {result.columns.length > 8 && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-600">
                        +{result.columns.length - 8} more
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
              <h4 className="text-sm font-medium text-red-800">Import Failed</h4>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
        <div className="flex">
          <i className="fas fa-info-circle text-blue-400 mt-0.5 mr-2"></i>
          <div className="text-sm">
            <p className="font-medium text-blue-800 mb-1">Schema-Only Mode</p>
            <ul className="text-blue-700 space-y-1">
              <li>• Enter column names one per line</li>
              <li>• No sample data will be available until you upload a file</li>
              <li>• You can still create mappings and regex rules</li>
              <li>• Useful when you know the schema but don't have the file yet</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SchemaInput;
