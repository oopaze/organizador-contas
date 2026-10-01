import type { ReactNode } from 'react';
import { Text, View } from 'react-native';
import { cn } from './ui/utils';

export interface InlineMessageProps {
  tone?: 'error' | 'success';
  children: ReactNode;
}

/** Banner inline usado em diálogo/tela no lugar dos toasts do PWA. */
export function InlineMessage({ tone = 'error', children }: InlineMessageProps) {
  return (
    <View className={cn('rounded-md px-3 py-2', tone === 'error' ? 'bg-red-100' : 'bg-green-100')}>
      <Text className={cn('text-sm', tone === 'error' ? 'text-red-800' : 'text-green-800')}>
        {children}
      </Text>
    </View>
  );
}
