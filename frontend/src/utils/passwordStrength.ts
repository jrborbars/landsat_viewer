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

export function checkPasswordStrength(password: string): PasswordStrength {
  const requirements = {
    length: password.length >= 12,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    digits: /\d/.test(password),
    special_chars: /[^a-zA-Z0-9]/.test(password),
    not_common: !['password', '123456', 'password123', 'admin', 'qwerty'].includes(password.toLowerCase()),
  };

  let score = 0;
  score += requirements.length ? 1 : 0;
  score += requirements.uppercase ? 1 : 0;
  score += requirements.lowercase ? 1 : 0;
  score += requirements.digits ? 1 : 0;
  score += requirements.special_chars ? 1 : 0;
  score += requirements.not_common ? 1 : 0;

  const strengthLevels = {
    0: 'very_weak',
    1: 'weak',
    2: 'fair',
    3: 'good',
    4: 'strong',
    5: 'very_strong',
  } as const;

  return {
    score,
    strength: strengthLevels[score as keyof typeof strengthLevels] || 'very_weak',
    requirements,
    is_strong: score >= 4,
  };
}
