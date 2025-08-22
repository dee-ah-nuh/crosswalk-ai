import { useState, useCallback } from 'react';
import { CrosswalkMapping, ValidationSummary, UseCrosswalkReturn } from '../types';
import { api } from '../services/api';

export const useCrosswalk = (profileId?: number): UseCrosswalkReturn => {
  const [mappings, setMappings] = useState<CrosswalkMapping[]>([]);
  const [validationSummary, setValidationSummary] = useState<ValidationSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshMappings = useCallback(async () => {
    if (!profileId) {
      setMappings([]);
      setValidationSummary(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Fetch mappings and validation summary in parallel
      const [mappingsData, summaryData] = await Promise.all([
        api.getCrosswalkMappings(profileId),
        api.getValidationSummary(profileId)
      ]);

      setMappings(mappingsData);
      setValidationSummary(summaryData);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch crosswalk data');
      console.error('Error fetching crosswalk data:', err);
    } finally {
      setLoading(false);
    }
  }, [profileId]);

  const updateMappings = useCallback(async (updatedMappings: CrosswalkMapping[]) => {
    if (!profileId) {
      throw new Error('No profile selected');
    }

    setError(null);

    try {
      await api.updateCrosswalkMappings(profileId, updatedMappings);
      
      // Update local state
      setMappings(updatedMappings);
      
      // Refresh validation summary
      const summaryData = await api.getValidationSummary(profileId);
      setValidationSummary(summaryData);
    } catch (err: any) {
      setError(err.message || 'Failed to update mappings');
      console.error('Error updating mappings:', err);
      throw err; // Re-throw to let the component handle it
    }
  }, [profileId]);

  return {
    mappings,
    validationSummary,
    loading,
    error,
    updateMappings,
    refreshMappings,
  };
};
