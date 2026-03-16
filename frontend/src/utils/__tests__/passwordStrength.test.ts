import { checkPasswordStrength } from '../passwordStrength';

describe('checkPasswordStrength', () => {
  test('returns very_weak for short password', () => {
    const result = checkPasswordStrength('short');
    expect(result.strength).toBe('very_weak');
    expect(result.score).toBe(1); // only length
    expect(result.is_strong).toBe(false);
  });

  test('returns weak for password with only length', () => {
    const result = checkPasswordStrength('verylongpassword');
    expect(result.strength).toBe('weak');
    expect(result.score).toBe(2); // length + not_common
    expect(result.is_strong).toBe(false);
  });

  test('returns strong for password with all requirements', () => {
    const result = checkPasswordStrength('MyStrongP@ssw0rd123');
    expect(result.strength).toBe('strong');
    expect(result.score).toBe(6);
    expect(result.is_strong).toBe(true);
    expect(result.requirements.length).toBe(true);
    expect(result.requirements.uppercase).toBe(true);
    expect(result.requirements.lowercase).toBe(true);
    expect(result.requirements.digits).toBe(true);
    expect(result.requirements.special_chars).toBe(true);
    expect(result.requirements.not_common).toBe(true);
  });

  test('returns very_weak for common password', () => {
    const result = checkPasswordStrength('password123');
    expect(result.strength).toBe('very_weak');
    expect(result.score).toBe(4); // length, lowercase, digits, but common
    expect(result.is_strong).toBe(false);
    expect(result.requirements.not_common).toBe(false);
  });

  test('returns fair for password with some requirements', () => {
    const result = checkPasswordStrength('Password123');
    expect(result.strength).toBe('fair');
    expect(result.score).toBe(4); // length, uppercase, lowercase, digits
    expect(result.is_strong).toBe(true);
  });
});
