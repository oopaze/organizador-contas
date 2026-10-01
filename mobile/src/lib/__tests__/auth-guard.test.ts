import { shouldRedirectToLogin } from '../auth-guard';

test('redireciona para login quando resolvido e sem usuário', () => {
  expect(shouldRedirectToLogin(false, false, false)).toBe(true);
});

test('não redireciona enquanto carrega nem quando já está no login', () => {
  expect(shouldRedirectToLogin(false, true, false)).toBe(false);
  expect(shouldRedirectToLogin(false, false, true)).toBe(false);
});