export interface User {
  id: string;  // UUIDv7 as string
  email: string;
  full_name: string;
  phone_number?: string;
  email_confirmed: boolean;
  is_active: boolean;
  is_superuser: boolean;
  last_login?: string;
  created_at: string;
  updated_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  password_confirm: string;
  full_name: string;
  phone_number?: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface PasswordStrength {
  score: number;
  strength: 'very_weak' | 'weak' | 'fair' | 'good' | 'strong' | 'very_strong';
  requirements: {
    length: boolean;
    uppercase: boolean;
    lowercase: boolean;
    digits: boolean;
    special_chars: boolean;
    not_common: boolean;
  };
  is_strong: boolean;
}
