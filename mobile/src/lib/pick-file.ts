import * as DocumentPicker from 'expo-document-picker';

export interface PickedFile {
  uri: string;
  name: string;
  mimeType: string | null;
  size: number | null;
}

/** Parte `file` do multipart no formato aceito pelo FormData do React Native. */
export interface UploadFilePart {
  uri: string;
  name: string;
  type: string;
}

export function toUploadFilePart(file: PickedFile): UploadFilePart {
  return {
    uri: file.uri,
    name: file.name,
    type: file.mimeType ?? 'application/octet-stream',
  };
}

/** Abre o seletor de arquivos do sistema; devolve null se o usuário cancelar. */
export async function pickFile(mimeTypes: string[]): Promise<PickedFile | null> {
  const result = await DocumentPicker.getDocumentAsync({
    type: mimeTypes,
    copyToCacheDirectory: true,
    multiple: false,
  });

  if (result.canceled) return null;

  const asset = result.assets[0];
  if (!asset) return null;

  return {
    uri: asset.uri,
    name: asset.name,
    mimeType: asset.mimeType ?? null,
    size: asset.size ?? null,
  };
}
