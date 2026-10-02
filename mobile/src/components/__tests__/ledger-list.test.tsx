import { fireEvent, render, screen } from '@testing-library/react-native';
import { LedgerList } from '../ledger-list';
import type { LedgerEntry, LedgerResult } from '../../services';

function buildEntry(overrides: Partial<LedgerEntry> = {}): LedgerEntry {
  return {
    date: '2026-10-01',
    description: 'Padaria',
    amount: '18.50',
    direction: 'outgoing',
    paid_at: '2026-10-01',
    category: 'food',
    transaction_id: 1,
    sub_transaction_id: null,
    transaction_identifier: 'Padaria',
    is_card: false,
    running_balance: '-18.50',
    ...overrides,
  };
}

function buildLedger(entries: LedgerEntry[]): LedgerResult {
  return {
    entries,
    summary: {
      realized_balance: '-18.50',
      projected_balance: '-18.50',
      payable: '0.00',
      receivable: '0.00',
      incoming_total: '0.00',
      outgoing_total: '18.50',
    },
  };
}

test('mostra entradas do extrato com valor formatado', async () => {
  await render(<LedgerList ledger={buildLedger([buildEntry()])} />);

  expect(screen.getByText('Padaria')).toBeTruthy();
  expect(screen.getByText(/^-R\$\s?18,50$/)).toBeTruthy();
});

test('receita mostra valor com sinal positivo', async () => {
  await render(
    <LedgerList
      ledger={buildLedger([
        buildEntry({ description: 'Salário', direction: 'incoming', amount: '5000.00' }),
      ])}
    />
  );

  expect(screen.getByText(/\+R\$\s?5\.000,00/)).toBeTruthy();
});

test('mostra cartão, previsto e saldo corrente', async () => {
  await render(
    <LedgerList
      ledger={buildLedger([buildEntry({ is_card: true, paid_at: null })] )}
    />
  );

  expect(screen.getByText('Cartão')).toBeTruthy();
  expect(screen.getByText('Previsto')).toBeTruthy();
  expect(screen.getByText(/Saldo: -R\$\s?18,50/)).toBeTruthy();
});

test('mostra esqueletos enquanto carrega', async () => {
  await render(<LedgerList ledger={undefined} loading />);

  expect(screen.getByTestId('ledger-loading')).toBeTruthy();
});

test('mostra estado vazio quando não há lançamentos', async () => {
  await render(<LedgerList ledger={buildLedger([])} />);

  expect(screen.getByText('Nenhum lançamento no período')).toBeTruthy();
});

test('mostra erro com ação de tentar novamente', async () => {
  const onRetry = jest.fn();
  await render(<LedgerList ledger={undefined} error="Falha ao carregar o extrato" onRetry={onRetry} />);

  expect(screen.getByText('Falha ao carregar o extrato')).toBeTruthy();
  await fireEvent.press(screen.getByText('Tentar novamente'));
  expect(onRetry).toHaveBeenCalledTimes(1);
});
