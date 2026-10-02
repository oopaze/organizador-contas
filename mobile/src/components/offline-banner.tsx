import { Text, View } from 'react-native';
import { formatHHmm } from '../lib/date';

export interface OfflineBannerProps {
  persistedAt: number | null;
}

export function OfflineBanner({ persistedAt }: OfflineBannerProps) {
  const message =
    persistedAt === null
      ? 'Sem conexão — sem dados salvos ainda'
      : `Sem conexão — dados de ${formatHHmm(new Date(persistedAt))}`;

  return (
    <View className="bg-amber-100 px-4 py-2">
      <Text className="text-center text-sm text-amber-900">{message}</Text>
    </View>
  );
}
