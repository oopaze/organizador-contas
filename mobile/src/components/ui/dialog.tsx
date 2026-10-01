import type { ReactNode } from 'react';
import {
  KeyboardAvoidingView,
  Modal,
  Platform,
  Pressable,
  Text,
  View,
} from 'react-native';
import X from 'lucide-react-native/icons/x';
import { cn } from './utils';

export interface DialogProps {
  visible: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  footer?: ReactNode;
  /** Esconde o botão X (usado pelo AlertDialog, que só oferece confirmar/cancelar). */
  showClose?: boolean;
  className?: string;
  children?: ReactNode;
}

export function Dialog({
  visible,
  onClose,
  title,
  description,
  footer,
  showClose = true,
  className,
  children,
}: DialogProps) {
  if (!visible) return null;

  return (
    <Modal visible transparent animationType="fade" statusBarTranslucent onRequestClose={onClose}>
      <View className="flex-1 items-center justify-center p-4">
        <Pressable
          accessibilityLabel="Fechar diálogo"
          onPress={onClose}
          className="absolute inset-0 bg-black/50"
        />
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          className="w-full max-w-lg"
        >
          <View className={cn('rounded-lg bg-white p-6 shadow-lg', className)}>
            {title || description ? (
              <View className="gap-2">
                {title ? (
                  <Text className="pr-8 text-lg font-semibold text-zinc-900">{title}</Text>
                ) : null}
                {description ? (
                  <Text className="text-sm text-zinc-500">{description}</Text>
                ) : null}
              </View>
            ) : null}
            {children ? <View className="mt-4 gap-4">{children}</View> : null}
            {footer ? <View className="mt-6 flex-row justify-end gap-2">{footer}</View> : null}
            {showClose ? (
              <Pressable
                accessibilityRole="button"
                accessibilityLabel="Fechar"
                onPress={onClose}
                className="absolute right-3 top-3 rounded-md p-2 active:bg-zinc-100"
              >
                <X size={18} color="#71717a" />
              </Pressable>
            ) : null}
          </View>
        </KeyboardAvoidingView>
      </View>
    </Modal>
  );
}
