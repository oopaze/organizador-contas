import { TextInput, type TextInputProps } from 'react-native';
import { cn } from './utils';

export function Textarea({ className, ...props }: TextInputProps) {
  return (
    <TextInput
      className={cn(
        'min-h-24 w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-base text-zinc-900',
        className
      )}
      placeholderTextColor="#a1a1aa"
      {...props}
      multiline
      textAlignVertical="top"
    />
  );
}
