import { createContext, useContext, type ReactNode } from 'react';
import Circle from 'lucide-react-native/icons/circle';
import { Pressable, View, type PressableProps } from 'react-native';
import { cn } from './utils';

interface RadioGroupContextValue {
  value: string;
  onValueChange: (value: string) => void;
}

const RadioGroupContext = createContext<RadioGroupContextValue | null>(null);

export interface RadioGroupProps {
  value: string;
  onValueChange: (value: string) => void;
  children: ReactNode;
  className?: string;
  accessibilityLabel?: string;
}

export function RadioGroup({
  value,
  onValueChange,
  children,
  className,
  accessibilityLabel,
}: RadioGroupProps) {
  return (
    <RadioGroupContext.Provider value={{ value, onValueChange }}>
      <View
        accessibilityRole="radiogroup"
        accessibilityLabel={accessibilityLabel}
        className={cn('gap-3', className)}
      >
        {children}
      </View>
    </RadioGroupContext.Provider>
  );
}

export interface RadioGroupItemProps extends Omit<PressableProps, 'onPress'> {
  value: string;
}

export function RadioGroupItem({ value, disabled, className, ...props }: RadioGroupItemProps) {
  const context = useContext(RadioGroupContext);
  if (!context) {
    throw new Error('RadioGroupItem precisa estar dentro de RadioGroup');
  }

  const selected = context.value === value;

  return (
    <Pressable
      {...props}
      disabled={disabled}
      accessibilityRole="radio"
      accessibilityState={{ checked: selected, disabled: disabled ?? undefined }}
      onPress={() => context.onValueChange(value)}
      className={cn(
        'h-5 w-5 items-center justify-center rounded-full border',
        selected ? 'border-emerald-600' : 'border-zinc-300 bg-white',
        disabled && 'opacity-50',
        className
      )}
    >
      {selected ? <Circle size={8} color="#059669" fill="#059669" /> : null}
    </Pressable>
  );
}
