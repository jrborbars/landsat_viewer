import React, { useState } from 'react';
import { format } from 'date-fns';
import type { Location, Image } from '../types/location';

interface LocationListProps {
  locations: Location[];
  onViewImages: (location: Location) => void;
}

const LocationList: React.FC<LocationListProps> = ({ locations, onViewImages }) => {
  const getStatusColor = (status: Image['status']) => {
    switch (status) {
      case 'completed': return 'text-success-600 bg-success-50 border-success-100';
      case 'failed': return 'text-error-600 bg-error-50 border-error-100';
      case 'downloading':
      case 'processing': return 'text-primary-600 bg-primary-50 border-primary-100 animate-pulse';
      default: return 'text-secondary-600 bg-secondary-50 border-secondary-100';
    }
  };

  const getStatusIcon = (status: Image['status']) => {
    switch (status) {
      case 'completed': return (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
        </svg>
      );
      case 'failed': return (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
        </svg>
      );
      default: return (
        <div className="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin" />
      );
    }
  };

  return (
    <div className="p-4 space-y-4">
      {locations.map((location) => (
        <div
          key={location.id}
          className="bg-white border-2 border-secondary-100 rounded-2xl p-5 hover:border-primary-200 hover:shadow-xl transition-all duration-300 group"
        >
          <div className="flex justify-between items-start mb-3">
            <h3 className="font-bold text-secondary-900 text-lg group-hover:text-primary-600 transition-colors">
              {location.name}
            </h3>
            <span className={`px-3 py-1 text-xs font-bold rounded-full border ${
              location.is_active
                ? 'bg-success-50 text-success-700 border-success-100'
                : 'bg-secondary-50 text-secondary-600 border-secondary-100'
            }`}>
              {location.is_active ? 'ACTIVE' : 'INACTIVE'}
            </span>
          </div>

          {location.description && (
            <p className="text-sm text-secondary-500 mb-4 line-clamp-2 italic">
              "{location.description}"
            </p>
          )}

          <div className="space-y-2.5 mb-5">
            <div className="flex justify-between text-xs">
              <span className="text-secondary-400 font-medium uppercase tracking-wider">Area</span>
              <span className="text-secondary-700 font-bold bg-secondary-50 px-2 py-0.5 rounded">
                {location.area_hectares || '0.00'} ha
              </span>
            </div>
            
            {/* Image Processing Status Summary */}
            {location.images && location.images.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {location.images.map((img) => (
                  <div 
                    key={img.id}
                    title={`${img.scene_id}: ${img.status}`}
                    className={`flex items-center space-x-1 px-2 py-1 rounded-md border text-[10px] font-bold uppercase ${getStatusColor(img.status)}`}
                  >
                    {getStatusIcon(img.status)}
                    <span>{img.status}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="flex space-x-2 pt-2 border-t border-secondary-50">
            <button 
              onClick={() => onViewImages(location)}
              className="flex-1 flex items-center justify-center space-x-2 bg-primary-600 hover:bg-primary-700 text-white text-xs font-bold py-2.5 rounded-xl shadow-lg shadow-primary-100 transition-all active:scale-95"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span>VIEW IMAGES</span>
            </button>
            <button className="p-2.5 bg-secondary-100 hover:bg-secondary-200 text-secondary-600 rounded-xl transition-all">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
            </button>
            <button className="p-2.5 bg-error-50 hover:bg-error-100 text-error-600 rounded-xl transition-all">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default LocationList;
