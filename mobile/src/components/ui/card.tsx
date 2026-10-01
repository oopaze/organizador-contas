import { Text, View, type TextProps, type ViewProps } from 'react-native';
import { cn } from './utils';

export function Card({ className, ...props }: ViewProps) {
  return (
    <View
      className={cn('flex-col gap-6 rounded-xl border border-zinc-200 bg-white', className)}
      {...props}
    />
  );
}

export function CardHeader({ className, ...props }: ViewProps) {
  return <View className={cn('gap-1.5 px-6 pt-6', className)} {...props} />;
}

export function CardTitle({ className, ...props }: TextProps) {
  return (
    <Text
      className={cn('text-lg font-semibold leading-none text-zinc-900', className)}
      {...props}
    />
  );
}

export function CardDescription({ className, ...props }: TextProps) {
  return <Text className={cn('text-sm text-zinc-500', className)} {...props} />;
}

export function CardContent({ className, children, ...props }: ViewProps) {
  return (
    <View className={cn('px-6 pb-6', className)} {...props}>
      {typeof children === 'string' || typeof children === 'number' ? (
        <Text className="text-base text-zinc-900">{children}</Text>
      ) : (
        children
      )}
    </View>
  );
}
