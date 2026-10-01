import type { ReactNode } from 'react';
import { Pressable, Text, type PressableProps } from 'react-native';
import { cn } from './utils';

type Variant = 'default' | 'outline' | 'ghost' | 'destructive';
type Size = 'default' | 'sm' | 'lg' | 'icon';

const variantClasses: Record<Variant, string> = {
  default: 'bg-emerald-600 active:bg-emerald-700',
  outline: 'border border-zinc-300 bg-white active:bg-zinc-100',
  ghost: 'bg-transparent active:bg-zinc-100',
  destructive: 'bg-red-600 active:bg-red-700',
};

const textClasses: Record<Variant, string> = {
  default: 'text-white',
  outline: 'text-zinc-900',
  ghost: 'text-zinc-900',
  destructive: 'text-white',
};

const sizeClasses: Record<Size, string> = {
  default: 'h-11 px-4',
  sm: 'h-9 px-3',
  lg: 'h-12 px-6',
  icon: 'h-11 w-11',
};

export interface ButtonProps extends PressableProps {
  variant?: Variant;
  size?: Size;
  children: ReactNode;
}

export function Button({
  variant = 'default',
  size = 'default',
  className,
  children,
  ...props
}: ButtonProps) {
  return (
    <Pressable
      accessibilityRole="button"
      className={cn(
        'flex-row items-center justify-center gap-2 rounded-md',
        variantClasses[variant],
        sizeClasses[size],
        props.disabled && 'opacity-50',
        className
      )}
      {...props}
    >
      {typeof children === 'string' ? (
        <Text className={cn('text-base font-medium', textClasses[variant])}>{children}</Text>
      ) : (
        children
      )}
    </Pressable>
  );
}
