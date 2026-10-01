import { forwardRef, useImperativeHandle, useState, type ReactNode } from 'react';
import { ScrollView, View, type ScrollViewProps, type ViewProps } from 'react-native';

/**
 * Mock manual de `@gorhom/bottom-sheet` para o Jest.
 *
 * O pacote real depende de Reanimated/Gesture Handler nativos e não renderiza no
 * jest-expo. Como este diretório fica ao lado de `node_modules`, o Jest aplica o
 * mock automaticamente a qualquer teste que importe o pacote (sem `jest.mock`).
 *
 * O contrato exposto é o que os overlays usam: `present()`/`dismiss()` no ref,
 * `children`, `onDismiss` e os wrappers de conteúdo.
 */

export interface BottomSheetModalHandle {
  present: () => void;
  dismiss: () => void;
}

interface BottomSheetModalMockProps {
  children?: ReactNode;
  onDismiss?: () => void;
}

export const BottomSheetModal = forwardRef<BottomSheetModalHandle, BottomSheetModalMockProps>(
  function BottomSheetModalMock({ children, onDismiss }, ref) {
    const [presented, setPresented] = useState(false);

    useImperativeHandle(ref, () => ({
      present: () => setPresented(true),
      dismiss: () => {
        setPresented(false);
        onDismiss?.();
      },
    }));

    if (!presented) return null;
    return <View testID="bottom-sheet-modal">{children}</View>;
  }
);

export function BottomSheetView({ children, ...props }: ViewProps) {
  return <View {...props}>{children}</View>;
}

export function BottomSheetModalProvider({ children }: { children?: ReactNode }) {
  return <>{children}</>;
}

export function BottomSheetScrollView({ children, ...props }: ScrollViewProps) {
  return <ScrollView {...props}>{children}</ScrollView>;
}

export function BottomSheetBackdrop() {
  return null;
}

export default BottomSheetModal;
