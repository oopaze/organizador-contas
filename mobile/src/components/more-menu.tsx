import { Pressable, Text, View } from 'react-native';
import type { LucideIcon } from 'lucide-react-native';
import LogOut from 'lucide-react-native/icons/log-out';
import MessageCircle from 'lucide-react-native/icons/message-circle';
import Plug from 'lucide-react-native/icons/plug';
import Settings from 'lucide-react-native/icons/settings';

export interface MoreMenuProps {
  onNavigate: (href: string) => void;
  onLogout: () => void;
}

interface MoreDestination {
  href: string;
  label: string;
  icon: LucideIcon;
}

/** Insights IA continua no web (Task 19 cancelada) — não entra no app. */
const DESTINATIONS: MoreDestination[] = [
  { href: '/integrations', label: 'Conectores', icon: Plug },
  { href: '/chat', label: 'Chat IA', icon: MessageCircle },
  { href: '/settings', label: 'Configurações', icon: Settings },
];

export function MoreMenu({ onNavigate, onLogout }: MoreMenuProps) {
  return (
    <View className="gap-2">
      {DESTINATIONS.map(({ href, label, icon: Icon }) => (
        <Pressable
          key={href}
          accessibilityRole="button"
          onPress={() => onNavigate(href)}
          className="flex-row items-center gap-3 rounded-lg border border-zinc-200 bg-white px-4 py-3 active:bg-zinc-100"
        >
          <Icon size={20} color="#3f3f46" />
          <Text className="text-base text-zinc-900">{label}</Text>
        </Pressable>
      ))}
      <Pressable
        accessibilityRole="button"
        onPress={onLogout}
        className="flex-row items-center gap-3 rounded-lg border border-red-200 bg-white px-4 py-3 active:bg-red-50"
      >
        <LogOut size={20} color="#dc2626" />
        <Text className="text-base text-red-600">Sair</Text>
      </Pressable>
    </View>
  );
}