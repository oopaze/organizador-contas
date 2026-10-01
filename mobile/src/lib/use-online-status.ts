import { useNetInfo } from '@react-native-community/netinfo';

export function useOnlineStatus(): boolean {
  const { isConnected } = useNetInfo();
  return isConnected !== false;
}
