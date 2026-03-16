import axios from 'axios';
import { apiService } from '../api';
import type { LoginCredentials, RegisterData } from '../../types/auth';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('ApiService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('login makes correct API call', async () => {
    const mockResponse = {
      data: {
        access_token: 'token123',
        refresh_token: 'refresh123',
        token_type: 'bearer',
        expires_in: 3600,
      },
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {},
    };

    mockedAxios.create = jest.fn(() => ({
      post: jest.fn().mockResolvedValue(mockResponse),
      interceptors: {
        request: { use: jest.fn() },
        response: { use: jest.fn() },
      },
    } as any));

    const credentials: LoginCredentials = {
      email: 'test@example.com',
      password: 'password123',
    };

    const result = await apiService.login(credentials);

    expect(result.data).toEqual(mockResponse.data);
  });

  test('register makes correct API call', async () => {
    const mockResponse = {
      data: { message: 'User created' },
      status: 201,
      statusText: 'Created',
      headers: {},
      config: {},
    };

    mockedAxios.create = jest.fn(() => ({
      post: jest.fn().mockResolvedValue(mockResponse),
      interceptors: {
        request: { use: jest.fn() },
        response: { use: jest.fn() },
      },
    } as any));

    const registerData: RegisterData = {
      email: 'test@example.com',
      password: 'password123',
      password_confirm: 'password123',
      full_name: 'Test User',
    };

    const result = await apiService.register(registerData);

    expect(result.data).toEqual(mockResponse.data);
  });

  test('getCurrentUser makes correct API call', async () => {
    const mockResponse = {
      data: { id: '1', email: 'test@example.com' },
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {},
    };

    mockedAxios.create = jest.fn(() => ({
      get: jest.fn().mockResolvedValue(mockResponse),
      interceptors: {
        request: { use: jest.fn() },
        response: { use: jest.fn() },
      },
    } as any));

    const result = await apiService.getCurrentUser();

    expect(result.data).toEqual(mockResponse.data);
  });
});
