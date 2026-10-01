import { cloneElement, isValidElement, useState, type ReactNode } from 'react';
import { Pressable, Text } from 'react-native';
import { Sheet } from './sheet';
import { cn } from './utils';

export interface DropdownMenuItem {
  label: string;
  onPress: () => void;
  destructive?: boolean;
}

export interface DropdownMenuProps {
  items: DropdownMenuItem[];
  /** Elemento tocável (ex.: `<Button>`); recebe o onPress que abre o menu. */
  trigger: ReactNode;
}

export function DropdownMenu({ items, trigger }: DropdownMenuProps) {
  const [open, setOpen] = useState(false);

  const triggerElement = isValidElement<{ onPress?: () => void }>(trigger)
    ? cloneElement(trigger, { onPress: () => setOpen(true) })
    : trigger;

  return (
    <>
      {triggerElement}
      <Sheet visible={open} onClose={() => setOpen(false)} scrollable>
        {items.map((item, index) => (
          <Pressable
            key={`${item.label}-${index}`}
            accessibilityRole="button"
            onPress={() => {
              setOpen(false);
              item.onPress();
            }}
            className="px-4 py-3 active:bg-zinc-100"
          >
            <Text
              className={cn('text-base', item.destructive ? 'text-red-600' : 'text-zinc-900')}
            >
              {item.label}
            </Text>
          </Pressable>
        ))}
      </Sheet>
    </>
  );
}
