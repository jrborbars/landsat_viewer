import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import RegisterPage from '../RegisterPage';
import { useAuthStore } from '../../store/authStore';

// Mock the auth store
jest.mock('../../store/authStore', () => ({
  useAuthStore: jest.fn(),
}));

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
}));

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

const mockRegister = jest.fn();

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('RegisterPage', () => {
  beforeEach(() => {
    (useAuthStore as unknown as jest.Mock).mockReturnValue({
      register: mockRegister,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders registration form', () => {
    renderWithProviders(<RegisterPage />);

    expect(screen.getByText('Create your account')).toBeInTheDocument();
    expect(screen.getByLabelText('Full Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Email address')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByLabelText('Confirm Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create account' })).toBeInTheDocument();
  });

  test('shows password strength when typing', async () => {
    renderWithProviders(<RegisterPage />);

    const passwordInput = screen.getByLabelText('Password');
    fireEvent.change(passwordInput, { target: { value: 'MyStrongP@ssw0rd123' } });

    await waitFor(() => {
      expect(screen.getByText('Strength: strong')).toBeInTheDocument();
    });
  });

  test('disables submit button for weak password', async () => {
    renderWithProviders(<RegisterPage />);

    const passwordInput = screen.getByLabelText('Password');
    fireEvent.change(passwordInput, { target: { value: 'weak' } });

    await waitFor(() => {
      const submitButton = screen.getByRole('button', { name: 'Create account' });
      expect(submitButton).toBeDisabled();
    });
  });

  test('enables submit button for strong password', async () => {
    renderWithProviders(<RegisterPage />);

    const passwordInput = screen.getByLabelText('Password');
    fireEvent.change(passwordInput, { target: { value: 'MyStrongP@ssw0rd123' } });

    await waitFor(() => {
      const submitButton = screen.getByRole('button', { name: 'Create account' });
      expect(submitButton).not.toBeDisabled();
    });
  });

  test('shows validation errors for invalid input', async () => {
    renderWithProviders(<RegisterPage />);

    const emailInput = screen.getByLabelText('Email address');
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.blur(emailInput);

    await waitFor(() => {
      expect(screen.getByText('Invalid email address')).toBeInTheDocument();
    });
  });

  test('submits form with valid data', async () => {
    mockRegister.mockResolvedValueOnce({});

    renderWithProviders(<RegisterPage />);

    fireEvent.change(screen.getByLabelText('Full Name'), { target: { value: 'Test User' } });
    fireEvent.change(screen.getByLabelText('Email address'), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'MyStrongP@ssw0rd123' } });
    fireEvent.change(screen.getByLabelText('Confirm Password'), { target: { value: 'MyStrongP@ssw0rd123' } });

    const submitButton = screen.getByRole('button', { name: 'Create account' });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith({
        full_name: 'Test User',
        email: 'test@example.com',
        password: 'MyStrongP@ssw0rd123',
        password_confirm: 'MyStrongP@ssw0rd123',
      });
    });
  });
});
