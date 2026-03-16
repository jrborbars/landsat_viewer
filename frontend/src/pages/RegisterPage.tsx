import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { useAuthStore } from '../store/authStore';
import { authService } from '../services/api';
import { checkPasswordStrength } from '../utils/passwordStrength';
import type { RegisterData, PasswordStrength } from '../types/auth';

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register: registerUser } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState<PasswordStrength | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterData>();

  const password = watch('password');

  // Check password strength when password changes
  useEffect(() => {
    if (password && password.length >= 8) {
      const strength = checkPasswordStrength(password);
      setPasswordStrength(strength);
    } else {
      setPasswordStrength(null);
    }
  }, [password]);

  const onSubmit = async (data: RegisterData) => {
    try {
      setIsLoading(true);

      // Check if password is strong enough
      if (passwordStrength && !passwordStrength.is_strong) {
        toast.error('Please choose a stronger password');
        return;
      }

      await registerUser(data);
      toast.success('Registration successful! Please check your email for confirmation.');
      navigate('/login');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Registration failed';

      // Show specific validation errors
      const errorDetails = error.response?.data?.detail;
      if (Array.isArray(errorDetails)) {
        // Handle Pydantic validation errors
        const validationErrors = errorDetails.map((detail: any) =>
          `${detail.loc?.join('.') || 'Unknown'}: ${detail.msg || 'Invalid value'}`
        ).join('; ');
        toast.error(`Validation Error: ${validationErrors}`);
      } else if (typeof errorDetails === 'string') {
        toast.error(errorDetails);
      } else {
        toast.error(errorMessage);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-secondary-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-secondary-900">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-secondary-600">
            Already have an account?{' '}
            <button
              onClick={() => navigate('/login')}
              className="font-medium text-primary-600 hover:text-primary-500"
            >
              Sign in
            </button>
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div className="card">
            <div className="space-y-4">
              <div>
                <label htmlFor="full_name" className="block text-sm font-medium text-secondary-700">
                  Full Name
                </label>
                <input
                  id="full_name"
                  type="text"
                  autoComplete="name"
                  required
                  className={`input-field mt-1 ${errors.full_name ? 'border-error-500' : ''}`}
                  placeholder="Enter your full name"
                  {...register('full_name', {
                    required: 'Full name is required',
                    minLength: {
                      value: 2,
                      message: 'Full name must be at least 2 characters',
                    },
                  })}
                />
                {errors.full_name && (
                  <p className="mt-1 text-sm text-error-600">{errors.full_name.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-secondary-700">
                  Email address
                </label>
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  required
                  className={`input-field mt-1 ${errors.email ? 'border-error-500' : ''}`}
                  placeholder="Enter your email"
                  {...register('email', {
                    required: 'Email is required',
                    pattern: {
                      value: /^\S+@\S+$/i,
                      message: 'Invalid email address',
                    },
                  })}
                />
                {errors.email && (
                  <p className="mt-1 text-sm text-error-600">{errors.email.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="phone_number" className="block text-sm font-medium text-secondary-700">
                  Phone Number (Optional)
                </label>
                <input
                  id="phone_number"
                  type="tel"
                  autoComplete="tel"
                  className={`input-field mt-1 ${errors.phone_number ? 'border-error-500' : ''}`}
                  placeholder="+1234567890"
                  {...register('phone_number', {
                    pattern: {
                      value: /^\+[1-9]\d{9,14}$/,
                      message: 'Phone number must be in international format (e.g., +1234567890)',
                    },
                  })}
                />
                {errors.phone_number && (
                  <p className="mt-1 text-sm text-error-600">{errors.phone_number.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-secondary-700">
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  autoComplete="new-password"
                  required
                  className={`input-field mt-1 ${errors.password ? 'border-error-500' : ''}`}
                  placeholder="Create a strong password"
                  {...register('password', {
                    required: 'Password is required',
                    minLength: {
                      value: 8,
                      message: 'Password must be at least 8 characters',
                    },
                  })}
                />
                {errors.password && (
                  <p className="mt-1 text-sm text-error-600">{errors.password.message}</p>
                )}

                {password && passwordStrength && (
                  <div className="mt-2">
                    <div className="w-full bg-secondary-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-300 ${
                          passwordStrength.is_strong
                            ? 'bg-success-500'
                            : passwordStrength.score >= 3
                            ? 'bg-warning-500'
                            : 'bg-error-500'
                        }`}
                        style={{ width: `${(passwordStrength.score / 5) * 100}%` }}
                      />
                    </div>
                    <div className="mt-2 text-sm">
                      <p className={`font-medium ${
                        passwordStrength.is_strong ? 'text-success-600' : 'text-warning-600'
                      }`}>
                        Strength: {passwordStrength.strength.replace('_', ' ')}
                      </p>
                      {!passwordStrength.is_strong && (
                        <div className="mt-1 text-secondary-600">
                          <p className="font-medium">Password requirements:</p>
                          <ul className="text-xs mt-1 space-y-1">
                            <li className={passwordStrength.requirements.length ? 'text-success-600' : 'text-error-600'}>
                              ✓ At least 12 characters
                            </li>
                            <li className={passwordStrength.requirements.uppercase ? 'text-success-600' : 'text-error-600'}>
                              ✓ At least one uppercase letter
                            </li>
                            <li className={passwordStrength.requirements.lowercase ? 'text-success-600' : 'text-error-600'}>
                              ✓ At least one lowercase letter
                            </li>
                            <li className={passwordStrength.requirements.digits ? 'text-success-600' : 'text-error-600'}>
                              ✓ At least one number
                            </li>
                            <li className={passwordStrength.requirements.special_chars ? 'text-success-600' : 'text-error-600'}>
                              ✓ At least one special character
                            </li>
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              <div>
                <label htmlFor="password_confirm" className="block text-sm font-medium text-secondary-700">
                  Confirm Password
                </label>
                <input
                  id="password_confirm"
                  type="password"
                  autoComplete="new-password"
                  required
                  className={`input-field mt-1 ${errors.password_confirm ? 'border-error-500' : ''}`}
                  placeholder="Confirm your password"
                  {...register('password_confirm', {
                    required: 'Please confirm your password',
                    validate: (value) =>
                      value === password || 'Passwords do not match',
                  })}
                />
                {errors.password_confirm && (
                  <p className="mt-1 text-sm text-error-600">{errors.password_confirm.message}</p>
                )}
              </div>
            </div>

            <div className="mt-6">
              <button
                type="submit"
                disabled={isLoading || (passwordStrength ? !passwordStrength.is_strong : true)}
                className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <div className="flex items-center justify-center">
                    <div className="loading-spinner w-4 h-4 mr-2" />
                    Creating account...
                  </div>
                ) : (
                  'Create account'
                )}
              </button>
            </div>

            <div className="mt-4 text-center text-sm text-secondary-600">
              By creating an account, you agree to our{' '}
              <button className="text-primary-600 hover:text-primary-500">
                Terms of Service
              </button>{' '}
              and{' '}
              <button className="text-primary-600 hover:text-primary-500">
                Privacy Policy
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RegisterPage;
