import { create } from 'zustand';
import { locationService } from '../services/api';
import type { Location, LocationCreate, Image } from '../types/location';

interface LocationState {
  locations: Location[];
  isLoading: boolean;
  error: string | null;

  // Actions
  loadLocations: () => Promise<void>;
  createLocation: (locationData: LocationCreate) => Promise<void>;
  updateLocation: (id: string, locationData: Partial<Location>) => Promise<void>;
  deleteLocation: (id: string) => Promise<void>;
  getLocation: (id: string) => Location | undefined;
  updateImageStatus: (imageId: string, status: Image['status'], message?: string) => void;
  clearError: () => void;
}

export const useLocationStore = create<LocationState>((set, get) => ({
  locations: [],
  isLoading: false,
  error: null,

  loadLocations: async () => {
    try {
      set({ isLoading: true, error: null });
      const response = await locationService.getLocations();
      set({ locations: response.data.locations, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to load locations',
        isLoading: false
      });
    }
  },

  createLocation: async (locationData: LocationCreate) => {
    try {
      set({ error: null });
      const response = await locationService.createLocation(locationData);

      // Add new location to the list
      set((state) => ({
        locations: [...state.locations, response.data],
      }));
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to create location',
      });
      throw error;
    }
  },

  updateLocation: async (id: string, locationData: Partial<Location>) => {
    try {
      set({ error: null });
      const response = await locationService.updateLocation(id, locationData);

      // Update location in the list
      set((state) => ({
        locations: state.locations.map((location) =>
          location.id === id ? response.data : location
        ),
      }));
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to update location',
      });
      throw error;
    }
  },

  deleteLocation: async (id: string) => {
    try {
      set({ error: null });
      await locationService.deleteLocation(id);

      // Remove location from the list
      set((state) => ({
        locations: state.locations.filter((location) => location.id !== id),
      }));
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to delete location',
      });
      throw error;
    }
  },

  getLocation: (id: string) => {
    return get().locations.find((location) => location.id === id);
  },

  updateImageStatus: (imageId: string, status: Image['status'], message?: string) => {
    set((state) => ({
      locations: state.locations.map((loc) => ({
        ...loc,
        images: loc.images?.map((img) => 
          img.id === imageId ? { ...img, status, error_message: message } : img
        )
      }))
    }));
  },

  clearError: () => {
    set({ error: null });
  },
}));
