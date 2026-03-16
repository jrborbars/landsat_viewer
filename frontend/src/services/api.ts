import axios, { AxiosInstance, AxiosResponse } from 'axios';
import type {
  LoginCredentials,
  RegisterData,
  AuthResponse,
  TokenResponse
} from '../types/auth';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.REACT_APP_API_URL || '/api/v1',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            // Try to refresh token
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
              const response = await this.refreshToken(refreshToken);
              const { access_token } = response.data;

              localStorage.setItem('access_token', access_token);
              originalRequest.headers.Authorization = `Bearer ${access_token}`;

              return this.client(originalRequest);
            }
          } catch (refreshError) {
            // Refresh failed, redirect to login
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Authentication methods
  async login(credentials: LoginCredentials): Promise<AxiosResponse<{
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
  }>> {
    const formData = new URLSearchParams();
    formData.append('username', credentials.email); // OAuth2 expects 'username'
    formData.append('password', credentials.password);
    return this.client.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  }

  async register(data: RegisterData): Promise<AxiosResponse<any>> {
    return this.client.post('/auth/register', data);
  }

  async refreshToken(refreshToken: string): Promise<AxiosResponse<TokenResponse>> {
    return this.client.post('/auth/refresh', { refresh_token: refreshToken });
  }

  async getCurrentUser(): Promise<AxiosResponse<any>> {
    return this.client.get('/auth/me');
  }



  async confirmEmail(token: string): Promise<AxiosResponse<any>> {
    return this.client.post('/auth/confirm-email', { token });
  }

  async forgotPassword(email: string): Promise<AxiosResponse<any>> {
    return this.client.post('/auth/forgot-password', { email });
  }

  async resetPassword(token: string, newPassword: string): Promise<AxiosResponse<any>> {
    return this.client.post('/auth/reset-password', {
      token,
      new_password: newPassword,
      new_password_confirm: newPassword,
    });
  }

  // Location methods
  async getLocations(params?: {
    page?: number;
    page_size?: number;
    include_inactive?: boolean;
  }): Promise<AxiosResponse<any>> {
    return this.client.get('/locations/', { params });
  }

  async getLocation(locationId: string): Promise<AxiosResponse<any>> {
    return this.client.get(`/locations/${locationId}`);
  }

  async createLocation(locationData: any): Promise<AxiosResponse<any>> {
    return this.client.post('/locations/', locationData);
  }

  async updateLocation(locationId: string, locationData: any): Promise<AxiosResponse<any>> {
    return this.client.put(`/locations/${locationId}`, locationData);
  }

  async deleteLocation(locationId: string): Promise<AxiosResponse<any>> {
    return this.client.delete(`/locations/${locationId}`);
  }

  async requestLandsatImages(locationId: string, imageRequest: any): Promise<AxiosResponse<any>> {
    return this.client.post(`/locations/${locationId}/request-images`, imageRequest);
  }

  async getLocationStats(): Promise<AxiosResponse<any>> {
    return this.client.get('/locations/stats/summary');
  }
}

// Create singleton instance
export const apiService = new ApiService();

// Export auth service as a convenience
export const authService = {
  login: (credentials: LoginCredentials) => apiService.login(credentials),
  register: (data: RegisterData) => apiService.register(data),
  refreshToken: (refreshToken: string) => apiService.refreshToken(refreshToken),
  getCurrentUser: () => apiService.getCurrentUser(),
  confirmEmail: (token: string) => apiService.confirmEmail(token),
  forgotPassword: (email: string) => apiService.forgotPassword(email),
  resetPassword: (token: string, newPassword: string) => apiService.resetPassword(token, newPassword),
};

export const locationService = {
  getLocations: (params?: any) => apiService.getLocations(params),
  getLocation: (locationId: string) => apiService.getLocation(locationId),
  createLocation: (locationData: any) => apiService.createLocation(locationData),
  updateLocation: (locationId: string, locationData: any) => apiService.updateLocation(locationId, locationData),
  deleteLocation: (locationId: string) => apiService.deleteLocation(locationId),
  requestLandsatImages: (locationId: string, imageRequest: any) => apiService.requestLandsatImages(locationId, imageRequest),
  getLocationStats: () => apiService.getLocationStats(),
};
