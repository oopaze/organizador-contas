import { queryClient } from '../query-client';

test('mantém o cache na memória para leitura offline', () => {
  const options = queryClient.getDefaultOptions().queries;
  expect(options?.gcTime).toBe(Infinity);
  expect(options?.staleTime).toBe(30_000);
  expect(options?.retry).toBe(1);
});
