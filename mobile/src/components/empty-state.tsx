import type { ReactNode } from 'react';
import { Text, View } from 'react-native';

export interface EmptyStateProps {
  title: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <View className="items-center gap-2 px-6 py-12">
      <Text className="text-base font-medium text-zinc-900">{title}</Text>
      {description ? (
        <Text className="text-center text-sm text-zinc-500">{description}</Text>
      ) : null}
      {action}
    </View>
  );
}
