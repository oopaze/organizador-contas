import type { ReactNode } from 'react';
import {
  KeyboardAvoidingView,
  Modal,
  Pressable,
  ScrollView,
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
    <Modal
      visible
      transparent
      animationType="fade"
      statusBarTranslucent
      onRequestClose={onClose}
      testID="dialog-modal"
    >
      <KeyboardAvoidingView behavior="padding" className="flex-1">
        <View className="flex-1 items-center justify-center p-4">
          <Pressable
            accessibilityLabel="Fechar diálogo"
            onPress={onClose}
            className="absolute inset-0 bg-black/50"
          />
          <View
            className={cn('max-h-full w-full max-w-lg rounded-lg bg-white p-6 shadow-lg', className)}
          >
            {showClose ? (
              <Pressable
                accessibilityRole="button"
                accessibilityLabel="Fechar"
                onPress={onClose}
                className="absolute right-2 top-2 z-10 h-11 w-11 items-center justify-center rounded-md active:bg-zinc-100"
              >
                <X size={18} color="#71717a" />
              </Pressable>
            ) : null}
            <ScrollView
              testID="dialog-scroll"
              keyboardShouldPersistTaps="handled"
              showsVerticalScrollIndicator={false}
            >
              {title || description ? (
                <View className="gap-2">
                  {title ? (
                    <Text className="pr-12 text-lg font-semibold text-zinc-900">{title}</Text>
                  ) : null}
                  {description ? (
                    <Text className="text-sm text-zinc-500">{description}</Text>
                  ) : null}
                </View>
              ) : null}
              {children ? <View className="mt-4 gap-4">{children}</View> : null}
              {footer ? <View className="mt-6 flex-row justify-end gap-2">{footer}</View> : null}
            </ScrollView>
          </View>
        </View>
      </KeyboardAvoidingView>
    </Modal>
  );
}
