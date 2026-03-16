import { useEffect, useState, useCallback } from 'react';
import { useAuthStore } from '../store/authStore';
import { useLocationStore } from '../store/locationStore';

export interface NotificationEvent {
  type: string;
  data: any;
  timestamp: string;
}

export interface UseNotificationsReturn {
  events: NotificationEvent[];
  isConnected: boolean;
  error: string | null;
  reconnect: () => void;
}

export const useNotifications = (): UseNotificationsReturn => {
  const { user, isTokenReady, accessToken } = useAuthStore();
  const { updateImageStatus } = useLocationStore();
  const [events, setEvents] = useState<NotificationEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let source: EventSource | null = null;
    let reconnectTimeout: NodeJS.Timeout;
    let isMounted = true;
    let retryCount = 0;
    const MAX_RETRY_DELAY = 30000;

    if (!user || !isTokenReady || !accessToken) {
      setIsConnected(false);
      return;
    }

    const connect = () => {
      if (!isMounted || !user || !isTokenReady || !accessToken) return;

      try {
        setError(null);
        // Pass token as query parameter because native EventSource doesn't support headers
        source = new EventSource(`/api/v1/events/stream?token=${accessToken}`);

        source.onopen = () => {
          if (!isMounted) {
            source?.close();
            return;
          }
          setIsConnected(true);
          setError(null);
          retryCount = 0;
          console.log('Connected to notification stream');
        };

        source.addEventListener('image_status_update', (event: MessageEvent) => {
          if (!isMounted) return;
          try {
            const payload = JSON.parse(event.data);
            updateImageStatus(payload.image_id, payload.status, payload.message || payload.error);
            
            const notification: NotificationEvent = {
              type: 'image_status_update',
              data: payload,
              timestamp: new Date().toISOString()
            };
            setEvents(prev => [...prev.slice(-49), notification]);
          } catch (err) {
            console.error('Failed to parse image_status_update:', err);
          }
        });

        source.onmessage = (event) => {
          if (!isMounted) return;
          try {
            const data: NotificationEvent = JSON.parse(event.data);
            setEvents(prev => [...prev.slice(-49), data]);
          } catch (parseError) {
            console.error('Failed to parse notification event:', parseError);
          }
        };

        source.onerror = () => {
          setIsConnected(false);
          source?.close();
          source = null;
          
          if (!isMounted || !user || !isTokenReady) return;

          const delay = Math.min(Math.pow(2, retryCount) * 1000, MAX_RETRY_DELAY);
          retryCount++;
          
          console.log(`SSE connection lost. Attempting to reconnect in ${delay/1000}s (retry ${retryCount})...`);
          
          reconnectTimeout = setTimeout(() => {
            connect();
          }, delay);
        };

      } catch (err) {
        if (isMounted) {
          setError('Failed to connect to notifications');
          console.error('Failed to create EventSource:', err);
        }
      }
    };

    connect();

    return () => {
      isMounted = false;
      if (source) {
        console.log('Closing SSE connection due to logout/unmount');
        source.close();
        source = null;
      }
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
    };
  }, [user?.id, isTokenReady, accessToken, updateImageStatus]);

  const reconnect = useCallback(() => {
    // This will be handled by the useEffect's dependency on user 
    // or we could add a trigger state if manual reconnect is needed.
  }, []);

  return { events, isConnected, error, reconnect };
};
