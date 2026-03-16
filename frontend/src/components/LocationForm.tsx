import React from 'react';
import { useForm } from 'react-hook-form';
import type { LocationCreate } from '../types/location';

interface LocationFormProps {
  coordinates: any; // Now accepting the full calculated data
  onSubmit: (data: LocationCreate) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

const LocationForm: React.FC<LocationFormProps> = ({
  coordinates,
  onSubmit,
  onCancel,
  isLoading = false,
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LocationCreate>({
    defaultValues: {
      name: '',
      description: '',
    },
  });

  const handleFormSubmit = (data: LocationCreate) => {
    onSubmit(data);
  };

  return (
    <div className="bg-white rounded-lg shadow-2xl border-2 border-primary-100 p-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold text-secondary-900">Save Selected Area</h3>
        <button
          onClick={onCancel}
          className="text-secondary-400 hover:text-secondary-600 transition-colors"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="mb-6 space-y-2 p-4 bg-secondary-50 rounded-xl border border-secondary-100">
        <div className="flex justify-between text-sm">
          <span className="text-secondary-500 font-medium">Center:</span>
          <span className="text-secondary-900 font-bold">
            {coordinates[0].toFixed(4)}, {coordinates[1].toFixed(4)}
          </span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-secondary-500 font-medium">Type:</span>
          <span className="text-primary-600 font-bold px-2 py-0.5 bg-primary-50 rounded-md">Polygon</span>
        </div>
      </div>

      <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-5">
        <div>
          <label htmlFor="name" className="block text-sm font-bold text-secondary-700 mb-2">
            Location Name *
          </label>
          <input
            id="name"
            type="text"
            className={`w-full px-4 py-3 rounded-xl border-2 transition-all focus:ring-4 focus:ring-primary-100 outline-none ${
              errors.name ? 'border-error-300 bg-error-50' : 'border-secondary-200 focus:border-primary-500'
            }`}
            placeholder="e.g. Amazon Rainforest Sector A"
            {...register('name', {
              required: 'Location name is required',
              minLength: {
                value: 2,
                message: 'Name must be at least 2 characters',
              },
            })}
          />
          {errors.name && (
            <p className="mt-2 text-sm font-medium text-error-600 flex items-center">
              <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              {errors.name.message}
            </p>
          )}
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-bold text-secondary-700 mb-2">
            Description (Optional)
          </label>
          <textarea
            id="description"
            rows={3}
            className="w-full px-4 py-3 rounded-xl border-2 border-secondary-200 focus:border-primary-500 focus:ring-4 focus:ring-primary-100 outline-none transition-all resize-none"
            placeholder="Add some details about this area..."
            {...register('description')}
          />
        </div>

        <div className="flex space-x-3 pt-4">
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 px-4 py-3 rounded-xl font-bold text-secondary-600 bg-secondary-100 hover:bg-secondary-200 transition-all disabled:opacity-50"
            disabled={isLoading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="flex-1 px-4 py-3 rounded-xl font-bold text-white bg-primary-600 hover:bg-primary-700 shadow-lg shadow-primary-200 transition-all disabled:opacity-50 flex items-center justify-center"
            disabled={isLoading}
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              'Save Location'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default LocationForm;
