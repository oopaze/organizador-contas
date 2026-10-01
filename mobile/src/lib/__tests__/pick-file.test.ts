import * as DocumentPicker from 'expo-document-picker';
import { pickFile, toUploadFilePart } from '../pick-file';

jest.mock('expo-document-picker', () => ({ getDocumentAsync: jest.fn() }));

const mockedPicker = DocumentPicker.getDocumentAsync as jest.Mock;

beforeEach(() => {
  jest.clearAllMocks();
});

test('devolve null quando o usuário cancela a seleção', async () => {
  mockedPicker.mockResolvedValue({ canceled: true, assets: null });

  await expect(pickFile(['application/pdf'])).resolves.toBeNull();
});

test('devolve o arquivo escolhido com nome, mime e tamanho', async () => {
  mockedPicker.mockResolvedValue({
    canceled: false,
    assets: [
      {
        uri: 'file://fatura.pdf',
        name: 'fatura.pdf',
        mimeType: 'application/pdf',
        size: 2048,
      },
    ],
  });

  await expect(pickFile(['application/pdf'])).resolves.toEqual({
    uri: 'file://fatura.pdf',
    name: 'fatura.pdf',
    mimeType: 'application/pdf',
    size: 2048,
  });
  expect(mockedPicker).toHaveBeenCalledWith(
    expect.objectContaining({ type: ['application/pdf'], multiple: false })
  );
});

test('monta a parte file do FormData no formato do React Native', () => {
  expect(
    toUploadFilePart({
      uri: 'file://fatura.pdf',
      name: 'fatura.pdf',
      mimeType: 'application/pdf',
      size: 2048,
    })
  ).toEqual({ uri: 'file://fatura.pdf', name: 'fatura.pdf', type: 'application/pdf' });
});

test('usa application/octet-stream quando o provedor não informa o mime', () => {
  expect(
    toUploadFilePart({
      uri: 'file://planilha.xlsx',
      name: 'planilha.xlsx',
      mimeType: null,
      size: null,
    })
  ).toEqual({
    uri: 'file://planilha.xlsx',
    name: 'planilha.xlsx',
    type: 'application/octet-stream',
  });
});
