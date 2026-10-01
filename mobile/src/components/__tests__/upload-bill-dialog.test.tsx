import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import * as DocumentPicker from 'expo-document-picker';
import { uploadBill } from '../../services';
import { UploadBillDialog } from '../upload-bill-dialog';

jest.mock('expo-document-picker', () => ({ getDocumentAsync: jest.fn() }));
jest.mock('../../services', () => ({
  uploadBill: jest.fn(),
  getCards: jest.fn().mockResolvedValue([]),
  createCard: jest.fn(),
}));

const mockedUploadBill = uploadBill as jest.Mock;

beforeEach(() => {
  jest.clearAllMocks();
});

test('mostra o erro do backend quando o upload falha', async () => {
  (DocumentPicker.getDocumentAsync as jest.Mock).mockResolvedValue({
    canceled: false,
    assets: [{ uri: 'file://f.pdf', name: 'f.pdf', mimeType: 'application/pdf', size: 10 }],
  });
  mockedUploadBill.mockRejectedValue(new Error('PDF protegido: senha inválida'));

  await render(<UploadBillDialog visible onClose={() => {}} onUploaded={() => {}} />);

  await fireEvent.press(screen.getByText('Selecionar arquivo'));

  await waitFor(() => expect(screen.getByText('f.pdf')).toBeTruthy());

  await fireEvent.press(screen.getByText('Enviar Fatura'));

  await waitFor(() => expect(screen.getByText('PDF protegido: senha inválida')).toBeTruthy());
  expect(mockedUploadBill).toHaveBeenCalledWith(expect.any(FormData));
});

test('sem rede mostra mensagem clara no diálogo', async () => {
  (DocumentPicker.getDocumentAsync as jest.Mock).mockResolvedValue({
    canceled: false,
    assets: [{ uri: 'file://f.pdf', name: 'f.pdf', mimeType: 'application/pdf', size: 10 }],
  });
  mockedUploadBill.mockRejectedValue(new TypeError('Network request failed'));

  await render(<UploadBillDialog visible onClose={() => {}} onUploaded={() => {}} />);

  await fireEvent.press(screen.getByText('Selecionar arquivo'));
  await waitFor(() => expect(screen.getByText('f.pdf')).toBeTruthy());
  await fireEvent.press(screen.getByText('Enviar Fatura'));

  await waitFor(() =>
    expect(screen.getByText('Sem conexão — tente de novo quando voltar.')).toBeTruthy()
  );
});
