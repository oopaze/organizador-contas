import type { ReactNode } from 'react';
import { Text } from 'react-native';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { cn } from './ui/utils';

export type StatCardTone = 'default' | 'positive' | 'negative' | 'warning';

const valueToneClasses: Record<StatCardTone, string> = {
  default: 'text-zinc-900',
  positive: 'text-green-600',
  negative: 'text-red-600',
  warning: 'text-orange-600',
};

export interface StatCardProps {
  title: string;
  value: string;
  subtitle?: ReactNode;
  icon?: ReactNode;
  tone?: StatCardTone;
}

export function StatCard({ title, value, subtitle, icon, tone = 'default' }: StatCardProps) {
  return (
    <Card className="gap-0">
      <CardHeader className="flex-row items-center justify-between gap-2 px-4 pb-2 pt-4">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent className="px-4 pb-4">
        <Text className={cn('text-2xl font-bold', valueToneClasses[tone])}>{value}</Text>
        {typeof subtitle === 'string' ? (
          <Text className="mt-1 text-sm text-zinc-500">{subtitle}</Text>
        ) : (
          subtitle
        )}
      </CardContent>
    </Card>
  );
}
