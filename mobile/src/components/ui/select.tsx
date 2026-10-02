import { useState } from 'react';
import Check from 'lucide-react-native/icons/check';
import ChevronDown from 'lucide-react-native/icons/chevron-down';
import { Pressable, Text } from 'react-native';
import { Sheet } from './sheet';
import { cn } from './utils';

export interface SelectOption {
  value: string;
  label: string;
}

export interface SelectProps {
  value?: string;
  onValueChange: (value: string) => void;
  options: SelectOption[];
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

export function Select({
  value,
  onValueChange,
  options,
  placeholder = 'Selecione',
  disabled,
  className,
}: SelectProps) {
  const [open, setOpen] = useState(false);
  const selected = options.find((option) => option.value === value);

  return (
    <>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel={selected?.label ?? placeholder}
        accessibilityState={{ expanded: open, disabled: disabled ?? undefined }}
        disabled={disabled}
        onPress={() => setOpen(true)}
        className={cn(
          'h-11 w-full flex-row items-center justify-between rounded-md border border-zinc-300 bg-white px-3',
          disabled && 'opacity-50',
          className
        )}
      >
        <Text className={cn('text-base', selected ? 'text-zinc-900' : 'text-zinc-500')}>
          {selected?.label ?? placeholder}
        </Text>
        <ChevronDown size={16} color="#71717a" />
      </Pressable>
      <Sheet visible={open} onClose={() => setOpen(false)} scrollable>
        {options.map((option) => {
          const isSelected = option.value === value;
          return (
            <Pressable
              key={option.value}
              accessibilityRole="button"
              accessibilityState={{ selected: isSelected }}
              onPress={() => {
                onValueChange(option.value);
                setOpen(false);
              }}
              className="flex-row items-center justify-between px-4 py-3 active:bg-zinc-100"
            >
              <Text className="text-base text-zinc-900">{option.label}</Text>
              {isSelected ? <Check size={16} color="#059669" /> : null}
            </Pressable>
          );
        })}
      </Sheet>
    </>
  );
}
