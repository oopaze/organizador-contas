import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import * as DocumentPicker from 'expo-document-picker';
import { getLoans, uploadPixReceipt } from '../../services';
import { UploadPixReceiptDialog } from '../upload-pix-receipt-dialog';

jest.mock('expo-document-picker', () => ({ getDocumentAsync: jest.fn() }));
jest.mock('../../services', () => ({
  getLoans: jest.fn().mockResolvedValue([]),
  uploadPixReceipt: jest.fn(),
}));

const mockedUploadPixReceipt = uploadPixReceipt as jest.Mock;

beforeEach(() => {
  jest.clearAllMocks();
  (getLoans as jest.Mock).mockResolvedValue([]);
  (DocumentPicker.getDocumentAsync as jest.Mock).mockResolvedValue({
    canceled: false,
    assets: [{ uri: 'file://pix.pdf', name: 'pix.pdf', mimeType: 'application/pdf', size: 10 }],
  });
});

async function selectFileAndSubmit() {
  await fireEvent.press(screen.getByText('Selecionar arquivo'));
  await waitFor(() => expect(screen.getByText('pix.pdf')).toBeTruthy());
  await fireEvent.press(screen.getByText('Enviar comprovante'));
}

test('quando a IA não extrai, encaminha o arquivo para entrada manual', async () => {
  const parseError = Object.assign(new Error('Não foi possível ler o comprovante'), {
    response: { status: 422, data: { file_id: 77, error: 'Não foi possível ler o comprovante' } },
  });
  mockedUploadPixReceipt.mockRejectedValue(parseError);
  const onParseFailed = jest.fn();
  const onUploaded = jest.fn();
  const onClose = jest.fn();

  await render(
    <UploadPixReceiptDialog
      visible
      preselectedLoanId={3}
      onClose={onClose}
      onUploaded={onUploaded}
      onParseFailed={onParseFailed}
    />
  );

  await selectFileAndSubmit();

  await waitFor(() => expect(onParseFailed).toHaveBeenCalledWith(77, 3));
  expect(onClose).toHaveBeenCalled();
  expect(onUploaded).not.toHaveBeenCalled();
});

test('mostra o erro do backend no diálogo quando não há arquivo anexado', async () => {
  mockedUploadPixReceipt.mockRejectedValue(new Error('Comprovante ilegível'));

  await render(
    <UploadPixReceiptDialog
      visible
      preselectedLoanId={3}
      onClose={() => {}}
      onUploaded={() => {}}
    />
  );

  await selectFileAndSubmit();

  await waitFor(() => expect(screen.getByText('Comprovante ilegível')).toBeTruthy());
});

test('envia o comprovante e devolve o pagamento registrado', async () => {
  const result = { payment: { id: 1, amount: '250.00' }, extracted: {} };
  mockedUploadPixReceipt.mockResolvedValue(result);
  const onUploaded = jest.fn();
  const onClose = jest.fn();

  await render(
    <UploadPixReceiptDialog
      visible
      preselectedLoanId={3}
      onClose={onClose}
      onUploaded={onUploaded}
    />
  );

  await selectFileAndSubmit();

  await waitFor(() => expect(onUploaded).toHaveBeenCalledWith(result));
  expect(onClose).toHaveBeenCalled();
});
