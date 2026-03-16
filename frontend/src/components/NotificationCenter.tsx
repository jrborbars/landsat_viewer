import React, { useState } from 'react';
import { useNotifications } from '../hooks/useNotifications';
import toast from 'react-hot-toast';

interface NotificationCenterProps {
  className?: string;
}

const NotificationCenter: React.FC<NotificationCenterProps> = ({ className = '' }) => {
  const { events, isConnected, error, reconnect } = useNotifications();
  const [isExpanded, setIsExpanded] = useState(false);

  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case 'job_status':
        return '📊';
      case 'image_processing_started':
        return '🚀';
      case 'image_processing_completed':
        return '✅';
      case 'location_created':
        return '📍';
      case 'heartbeat':
        return '💚';
      default:
        return '📢';
    }
  };

  const getEventColor = (eventType: string) => {
    switch (eventType) {
      case 'job_status':
        return 'text-blue-600';
      case 'image_processing_started':
        return 'text-orange-600';
      case 'image_processing_completed':
        return 'text-green-600';
      case 'location_created':
        return 'text-purple-600';
      case 'heartbeat':
        return 'text-gray-500';
      default:
        return 'text-secondary-600';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const recentEvents = events.slice(-5); // Show last 5 events

  return (
    <div className={`relative ${className}`}>
      {/* Connection Status */}
      <div className="flex items-center space-x-2 mb-2">
        <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
        <span className="text-xs text-secondary-600">
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
        {!isConnected && (
          <button
            onClick={reconnect}
            className="text-xs text-primary-600 hover:text-primary-700"
          >
            Reconnect
          </button>
        )}
      </div>

      {/* Notification Bell */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="relative p-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 rounded-lg transition-colors duration-200"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 17h5l-5 5v-5zM4.868 12.683A17.925 17.925 0 0112 21c7.962 0 12-1.21 12-2.683m-12 2.683a17.925 17.925 0 01-7.132-8.317M12 21c4.411 0 8-4.03 8-9s-3.589-9-8-9-8 4.03-8 9a9.06 9.06 0 01.968 4.317"
          />
        </svg>

        {recentEvents.length > 0 && (
          <span className="absolute -top-1 -right-1 bg-primary-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
            {recentEvents.length > 9 ? '9+' : recentEvents.length}
          </span>
        )}
      </button>

      {/* Notification Panel */}
      {isExpanded && (
        <div className="absolute right-0 top-full mt-2 w-80 bg-white rounded-lg shadow-lg border border-secondary-200 z-50">
          <div className="p-4 border-b border-secondary-200">
            <div className="flex justify-between items-center">
              <h3 className="font-semibold text-secondary-900">Notifications</h3>
              <button
                onClick={() => setIsExpanded(false)}
                className="text-secondary-400 hover:text-secondary-600"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <div className="max-h-96 overflow-y-auto">
            {error && (
              <div className="p-4 bg-error-50 border-l-4 border-error-400">
                <div className="flex">
                  <div className="ml-3">
                    <p className="text-sm text-error-700">{error}</p>
                    <button
                      onClick={reconnect}
                      className="mt-2 text-sm text-error-800 hover:text-error-900"
                    >
                      Try again
                    </button>
                  </div>
                </div>
              </div>
            )}

            {recentEvents.length === 0 ? (
              <div className="p-4 text-center text-secondary-500">
                <p>No notifications yet</p>
              </div>
            ) : (
              <div className="divide-y divide-secondary-100">
                {recentEvents.map((event, index) => (
                  <div key={index} className="p-4 hover:bg-secondary-50">
                    <div className="flex items-start space-x-3">
                      <span className="text-lg">{getEventIcon(event.type)}</span>
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm font-medium ${getEventColor(event.type)}`}>
                          {event.type.replace('_', ' ').toUpperCase()}
                        </p>
                        <p className="text-sm text-secondary-600 mt-1">
                          {event.data.message || event.data.status || 'Notification received'}
                        </p>
                        <p className="text-xs text-secondary-400 mt-1">
                          {formatTimestamp(event.timestamp)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Backdrop for mobile */}
      {isExpanded && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsExpanded(false)}
        />
      )}
    </div>
  );
};

export default NotificationCenter;
