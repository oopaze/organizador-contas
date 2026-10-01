import { useState, type ReactNode } from 'react';
import { Modal, Pressable, View } from 'react-native';
import { cn } from './utils';

export interface PopoverProps {
  trigger: ReactNode;
  children?: ReactNode;
  className?: string;
}

/**
 * Conteúdo flutuante ancorado embaixo (estilo sheet) sobre um `Modal` do RN.
 * Usado no seletor de mês; a API controla abertura internamente pelo trigger.
 */
export function Popover({ trigger, children, className }: PopoverProps) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Pressable
        accessibilityRole="button"
        accessibilityState={{ expanded: open }}
        onPress={() => setOpen(true)}
        className={cn(className)}
      >
        {trigger}
      </Pressable>
      {open ? (
        <Modal
          visible
          transparent
          animationType="fade"
          statusBarTranslucent
          onRequestClose={() => setOpen(false)}
        >
          <View className="flex-1 justify-end p-4">
            <Pressable
              accessibilityLabel="Fechar"
              onPress={() => setOpen(false)}
              className="absolute inset-0 bg-black/30"
            />
            <View className="rounded-2xl bg-white p-4 shadow-lg">{children}</View>
          </View>
        </Modal>
      ) : null}
    </>
  );
}
