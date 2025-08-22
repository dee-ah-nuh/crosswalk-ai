import React, { useState } from 'react';
import { api } from '../services/api';

interface RegexTesterProps {
  sourceColumn: any;
  onRuleChange: () => void;
}

const RegexTester: React.FC<RegexTesterProps> = ({ sourceColumn, onRuleChange }) => {
  const [newRule, setNewRule] = useState({
    rule_name: '',
    pattern: '',
    flags: '',
    description: ''
  });
  const [testValue, setTestValue] = useState('');
  const [testResult, setTestResult] = useState<any>(null);
  const [testing, setTesting] = useState(false);

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newRule.pattern.trim()) return;
    
    try {
      await api.post(`/source-columns/${sourceColumn.source_column_id}/regex`, newRule);
      setNewRule({ rule_name: '', pattern: '', flags: '', description: '' });
      onRuleChange();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error creating regex rule');
    }
  };

  const handleDeleteRule = async (ruleId: number) => {
    try {
      await api.delete(`/regex-rules/${ruleId}`);
      onRuleChange();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Error deleting regex rule');
    }
  };

  const handleTestRegex = async () => {
    if (!newRule.pattern.trim() || !testValue.trim()) return;
    
    setTesting(true);
    try {
      const params = new URLSearchParams({
        pattern: newRule.pattern,
        value: testValue,
        flags: newRule.flags
      });
      
      const result = await api.get(`/source-columns/${sourceColumn.source_column_id}/regex/test?${params}`);
      setTestResult(result);
    } catch (error: any) {
      setTestResult({ error: error.response?.data?.detail || 'Test failed' });
    } finally {
      setTesting(false);
    }
  };

  const testRuleAgainstSamples = async (rule: any) => {
    const sampleValues = sourceColumn.sample_values || [];
    if (sampleValues.length === 0) return null;
    
    try {
      const results = await Promise.all(
        sampleValues.slice(0, 5).map(async (value: string) => {
          const params = new URLSearchParams({
            pattern: rule.pattern,
            value,
            flags: rule.flags || ''
          });
          
          const result = await api.get(`/source-columns/${sourceColumn.source_column_id}/regex/test?${params}`);
          return { value, matches: result.matches };
        })
      );
      
      return results;
    } catch (error) {
      return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Existing Rules */}
      <div>
        <h4 className="text-sm font-medium text-gray-900 mb-3">
          Existing Rules for "{sourceColumn.source_column}"
        </h4>
        
        {sourceColumn.regex_rules && sourceColumn.regex_rules.length > 0 ? (
          <div className="space-y-2">
            {sourceColumn.regex_rules.map((rule: any) => (
              <div key={rule.id} className="bg-gray-50 rounded-md p-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="font-medium text-sm text-gray-900">
                        {rule.rule_name || 'Unnamed Rule'}
                      </span>
                      {rule.flags && (
                        <span className="px-1.5 py-0.5 text-xs bg-blue-100 text-blue-800 rounded">
                          {rule.flags}
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-700 font-mono bg-white rounded px-2 py-1 mb-1">
                      {rule.pattern}
                    </div>
                    {rule.description && (
                      <div className="text-xs text-gray-600">{rule.description}</div>
                    )}
                  </div>
                  <button
                    onClick={() => handleDeleteRule(rule.id)}
                    className="ml-2 text-red-600 hover:text-red-800 focus:outline-none"
                  >
                    <i className="fas fa-trash text-sm"></i>
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-4 text-gray-500 bg-gray-50 rounded-md">
            <i className="fas fa-code text-xl mb-1"></i>
            <p className="text-sm">No regex rules defined</p>
          </div>
        )}
      </div>

      {/* Create New Rule */}
      <div>
        <h4 className="text-sm font-medium text-gray-900 mb-3">Create New Rule</h4>
        
        <form onSubmit={handleCreateRule} className="space-y-3">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Rule Name
            </label>
            <input
              type="text"
              value={newRule.rule_name}
              onChange={(e) => setNewRule({ ...newRule, rule_name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              placeholder="e.g., digits_only"
            />
          </div>
          
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Regex Pattern *
            </label>
            <input
              type="text"
              value={newRule.pattern}
              onChange={(e) => setNewRule({ ...newRule, pattern: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm font-mono focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              placeholder="e.g., ^[0-9]+$"
              required
            />
          </div>
          
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Flags
            </label>
            <input
              type="text"
              value={newRule.flags}
              onChange={(e) => setNewRule({ ...newRule, flags: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              placeholder="e.g., i,m"
            />
            <div className="text-xs text-gray-500 mt-1">
              Common flags: i (case insensitive), m (multiline), s (dotall)
            </div>
          </div>
          
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={newRule.description}
              onChange={(e) => setNewRule({ ...newRule, description: e.target.value })}
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Describe what this pattern validates..."
            />
          </div>
          
          <button
            type="submit"
            className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <i className="fas fa-plus mr-2"></i>
            Add Rule
          </button>
        </form>
      </div>

      {/* Test Pattern */}
      <div>
        <h4 className="text-sm font-medium text-gray-900 mb-3">Test Pattern</h4>
        
        <div className="space-y-3">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Test Value
            </label>
            <div className="flex space-x-2">
              <input
                type="text"
                value={testValue}
                onChange={(e) => setTestValue(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter value to test"
              />
              <button
                onClick={handleTestRegex}
                disabled={testing || !newRule.pattern.trim() || !testValue.trim()}
                className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
              >
                {testing ? (
                  <i className="fas fa-spinner fa-spin"></i>
                ) : (
                  <i className="fas fa-play"></i>
                )}
              </button>
            </div>
          </div>
          
          {/* Quick Test with Sample Values */}
          {sourceColumn.sample_values && sourceColumn.sample_values.length > 0 && (
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Quick Test (sample values)
              </label>
              <div className="space-y-1">
                {sourceColumn.sample_values.slice(0, 3).map((value: string, index: number) => (
                  <button
                    key={index}
                    onClick={() => setTestValue(value)}
                    className="w-full text-left px-2 py-1 text-sm bg-gray-50 hover:bg-gray-100 rounded border text-gray-700"
                  >
                    {value}
                  </button>
                ))}
              </div>
            </div>
          )}
          
          {/* Test Result */}
          {testResult && (
            <div className="border rounded-md p-3">
              {testResult.error ? (
                <div className="text-red-600">
                  <i className="fas fa-exclamation-triangle mr-1"></i>
                  Error: {testResult.error}
                </div>
              ) : (
                <div>
                  <div className={`flex items-center mb-2 ${
                    testResult.matches ? 'text-green-600' : 'text-red-600'
                  }`}>
                    <i className={`fas ${testResult.matches ? 'fa-check-circle' : 'fa-times-circle'} mr-2`}></i>
                    <span className="font-medium">
                      {testResult.matches ? 'Match Found' : 'No Match'}
                    </span>
                  </div>
                  
                  {testResult.matches && (
                    <div className="space-y-1">
                      {testResult.full_match && (
                        <div className="text-sm">
                          <span className="text-gray-600">Full match:</span>
                          <span className="ml-2 font-mono bg-yellow-100 px-1 rounded">
                            {testResult.full_match}
                          </span>
                        </div>
                      )}
                      
                      {testResult.groups && testResult.groups.length > 0 && (
                        <div className="text-sm">
                          <span className="text-gray-600">Groups:</span>
                          <div className="ml-2 space-y-1">
                            {testResult.groups.map((group: string, index: number) => (
                              <div key={index} className="font-mono bg-blue-100 px-1 rounded inline-block mr-1">
                                {index + 1}: {group}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RegexTester;
