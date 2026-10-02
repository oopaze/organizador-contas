import Check from 'lucide-react-native/icons/check';
import { Pressable, type PressableProps } from 'react-native';
import { cn } from './utils';

export interface CheckboxProps extends Omit<PressableProps, 'onPress'> {
  checked: boolean;
  onCheckedChange?: (checked: boolean) => void;
}

export function Checkbox({
  checked,
  onCheckedChange,
  disabled,
  className,
  ...props
}: CheckboxProps) {
  return (
    <Pressable
      {...props}
      disabled={disabled}
      accessibilityRole="checkbox"
      accessibilityState={{ checked, disabled: disabled ?? undefined }}
      onPress={() => onCheckedChange?.(!checked)}
      className={cn(
        'h-5 w-5 items-center justify-center rounded border',
        checked ? 'border-emerald-600 bg-emerald-600' : 'border-zinc-300 bg-white',
        disabled && 'opacity-50',
        className
      )}
    >
      {checked ? <Check size={14} color="#ffffff" /> : null}
    </Pressable>
  );
}
