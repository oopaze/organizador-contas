import { Text, type TextProps } from 'react-native';
import { cn } from './utils';

export function Label({ className, ...props }: TextProps) {
  return <Text className={cn('text-sm font-medium text-zinc-900', className)} {...props} />;
}
