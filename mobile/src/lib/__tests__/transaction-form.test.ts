import { formatUploadError } from '../transaction-form';

test('mantém a mensagem real do backend', () => {
  expect(formatUploadError(new Error('PDF protegido: senha inválida'), 'Falha ao enviar')).toBe(
    'PDF protegido: senha inválida'
  );
});

test('troca falha de rede por mensagem clara', () => {
  expect(
    formatUploadError(new TypeError('Network request failed'), 'Falha ao enviar')
  ).toBe('Sem conexão — tente de novo quando voltar.');
});

test('usa o fallback quando o erro não tem mensagem', () => {
  expect(formatUploadError({}, 'Falha ao enviar')).toBe('Falha ao enviar');
});
