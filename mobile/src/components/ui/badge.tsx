import { isValidElement, type ReactNode } from 'react';
import { Text, View, type ViewProps } from 'react-native';
import { cn } from './utils';

type BadgeVariant = 'default' | 'secondary' | 'destructive' | 'outline';

const containerClasses: Record<BadgeVariant, string> = {
  default: 'border-transparent bg-emerald-600',
  secondary: 'border-transparent bg-zinc-100',
  destructive: 'border-transparent bg-red-600',
  outline: 'border-zinc-300 bg-white',
};

const textClasses: Record<BadgeVariant, string> = {
  default: 'text-white',
  secondary: 'text-zinc-900',
  destructive: 'text-white',
  outline: 'text-zinc-900',
};

export interface BadgeProps extends ViewProps {
  variant?: BadgeVariant;
  children?: ReactNode;
}

export function Badge({ variant = 'default', className, children, ...props }: BadgeProps) {
  return (
    <View
      className={cn(
        'flex-row items-center justify-center gap-1 self-start rounded-md border px-2 py-0.5',
        containerClasses[variant],
        className
      )}
      {...props}
    >
      {isValidElement(children) ? (
        children
      ) : (
        <Text className={cn('text-xs font-medium', textClasses[variant])}>{children}</Text>
      )}
    </View>
  );
}
