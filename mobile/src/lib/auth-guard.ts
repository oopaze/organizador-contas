/**
 * Decide se a navegação deve mandar o usuário para a tela de login.
 *
 * - enquanto a sessão está sendo resolvida (`isLoading`), não redireciona;
 * - quem já está no login não é redirecionado de novo;
 * - resolvido e sem usuário, redireciona.
 */
export function shouldRedirectToLogin(
  isAuthenticated: boolean,
  isLoading: boolean,
  inAuthGroup: boolean
): boolean {
  if (isLoading || inAuthGroup) return false;
  return !isAuthenticated;
}