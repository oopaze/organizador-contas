import { TextInput, View, type TextInputProps } from 'react-native';
import { Label } from './label';
import { cn } from './utils';

export interface InputProps extends TextInputProps {
  label?: string;
  containerClassName?: string;
}

export function Input({
  label,
  className,
  containerClassName,
  accessibilityLabel,
  ...props
}: InputProps) {
  return (
    <View className={cn('gap-2', containerClassName)}>
      {label ? <Label>{label}</Label> : null}
      <TextInput
        accessibilityLabel={accessibilityLabel ?? label}
        className={cn(
          'h-11 w-full rounded-md border border-zinc-300 bg-white px-3 text-base text-zinc-900',
          props.editable === false && 'opacity-50',
          className
        )}
        placeholderTextColor="#a1a1aa"
        {...props}
      />
    </View>
  );
}
