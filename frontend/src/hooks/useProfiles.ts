import { useState, useCallback } from 'react';
import { Profile, UseProfilesReturn } from '../types';
import { api } from '../services/api';

export const useProfiles = (): UseProfilesReturn => {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshProfiles = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await api.getProfiles();
      setProfiles(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch profiles');
      console.error('Error fetching profiles:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const createProfile = useCallback(async (name: string, clientId: string) => {
    setError(null);

    try {
      await api.createProfile(name, clientId);
      // Refresh the profiles list
      await refreshProfiles();
    } catch (err: any) {
      setError(err.message || 'Failed to create profile');
      console.error('Error creating profile:', err);
      throw err; // Re-throw to let the component handle it
    }
  }, [refreshProfiles]);

  return {
    profiles,
    loading,
    error,
    createProfile,
    refreshProfiles,
  };
};
