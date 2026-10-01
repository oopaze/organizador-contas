import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import { applyReconciliation, previewReconciliation, type ReconcilePreview } from '../../services';
import { ReconcileBillDialog } from '../reconcile-bill-dialog';

jest.mock('../../services', () => ({
  previewReconciliation: jest.fn(),
  applyReconciliation: jest.fn(),
}));

const PREVIEW: ReconcilePreview = {
  bill: { id: 9, identifier: 'Fatura Nubank', due_date: '2026-10-10' },
  pairs: [
    {
      bill_sub_transaction_id: 1,
      real_sub_transaction_id: 11,
      real_transaction_id: 21,
      confidence: 0.9,
      reason: 'mesmo valor',
      bill: {
        id: 1,
        date: '2026-10-01',
        description: 'Padaria',
        amount: '25.90',
        installment_info: null,
        category: '',
      },
      real: {
        id: 11,
        date: '2026-10-01',
        description: 'Padaria',
        amount: '25.90',
        installment_info: null,
        category: '',
      },
    },
  ],
  unmatched_bill: [],
  unmatched_real: [],
  suggested_categories: [{ sub_transaction_id: 1, category: 'Mercado' }],
};

beforeEach(() => {
  jest.clearAllMocks();
});

test('mostra os pares e aplica a conciliação selecionada', async () => {
  (previewReconciliation as jest.Mock).mockResolvedValue(PREVIEW);
  (applyReconciliation as jest.Mock).mockResolvedValue({
    merged: 1,
    categorized: 1,
    unmatched_remaining: 0,
    closed_open_bills: [3],
  });
  const onReconciled = jest.fn();

  await render(
    <ReconcileBillDialog
      visible
      onClose={() => {}}
      transactionIds={[5]}
      onReconciled={onReconciled}
    />
  );

  expect(await screen.findByText('Pares encontrados')).toBeTruthy();
  expect(screen.getByText('90% de confiança')).toBeTruthy();
  expect(screen.getByText('Categoria: Mercado')).toBeTruthy();

  await fireEvent.press(screen.getByText('Conciliar 1'));

  await waitFor(() =>
    expect(applyReconciliation).toHaveBeenCalledWith({
      pairs: [{ bill_sub_transaction_id: 1, real_sub_transaction_id: 11 }],
      categories: [{ sub_transaction_id: 1, category: 'Mercado' }],
    })
  );
  expect(onReconciled).toHaveBeenCalledWith(expect.objectContaining({ merged: 1 }));
});

test('mostra falha ao carregar a prévia com opção de tentar de novo', async () => {
  (previewReconciliation as jest.Mock).mockRejectedValueOnce(new Error('sem rede'));

  await render(
    <ReconcileBillDialog visible onClose={() => {}} transactionIds={[5]} onReconciled={() => {}} />
  );

  expect(await screen.findByText('Falha ao carregar a conciliação.')).toBeTruthy();
  expect(screen.getByText('Tentar de novo')).toBeTruthy();
});
