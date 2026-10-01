import Home from 'lucide-react-native/icons/home';
import Target from 'lucide-react-native/icons/target';
import HandCoins from 'lucide-react-native/icons/hand-coins';
import Users from 'lucide-react-native/icons/users';
import Menu from 'lucide-react-native/icons/menu';
import { Tabs } from 'expo-router/js-tabs';

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: '#059669',
        tabBarInactiveTintColor: '#71717a',
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Início',
          tabBarIcon: ({ color, size }) => <Home color={color} size={size} />,
        }}
      />
      <Tabs.Screen
        name="planning"
        options={{
          title: 'Planejamento',
          tabBarIcon: ({ color, size }) => <Target color={color} size={size} />,
        }}
      />
      <Tabs.Screen
        name="loans"
        options={{
          title: 'Empréstimos',
          tabBarIcon: ({ color, size }) => <HandCoins color={color} size={size} />,
        }}
      />
      <Tabs.Screen
        name="actors"
        options={{
          title: 'Atores',
          tabBarIcon: ({ color, size }) => <Users color={color} size={size} />,
        }}
      />
      <Tabs.Screen
        name="more"
        options={{
          title: 'Mais',
          tabBarIcon: ({ color, size }) => <Menu color={color} size={size} />,
        }}
      />
    </Tabs>
  );
}