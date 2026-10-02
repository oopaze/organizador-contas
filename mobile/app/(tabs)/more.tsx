import { router } from 'expo-router';
import { Text, View } from 'react-native';
import { MoreMenu } from '../../src/components/more-menu';
import { useAuth } from '../../src/contexts/auth-context';

export default function MoreScreen() {
  const { logout } = useAuth();

  return (
    <View className="flex-1 gap-4 bg-zinc-50 p-4">
      <Text className="text-lg font-semibold text-zinc-900">Mais</Text>
      <MoreMenu onNavigate={(href) => router.push(href)} onLogout={logout} />
    </View>
  );
}