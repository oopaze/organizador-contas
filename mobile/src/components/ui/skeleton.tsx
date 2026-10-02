import { View, type ViewProps } from 'react-native';
import { cn } from './utils';

export function Skeleton({ className, ...props }: ViewProps) {
  return <View className={cn('animate-pulse rounded-md bg-zinc-200', className)} {...props} />;
}
