import type { ReactNode } from 'react';
import { useCallback, useEffect, useRef } from 'react';
import {
  BottomSheetBackdrop,
  BottomSheetModal,
  BottomSheetScrollView,
  BottomSheetView,
  type BottomSheetBackdropProps,
} from '@gorhom/bottom-sheet';
import X from 'lucide-react-native/icons/x';
import { Pressable, Text, View } from 'react-native';

export interface SheetProps {
  visible: boolean;
  onClose: () => void;
  title?: string;
  /** Usa lista rolável (Select/DropdownMenu); por padrão dimensiona pelo conteúdo. */
  scrollable?: boolean;
  children?: ReactNode;
}

export function Sheet({ visible, onClose, title, scrollable, children }: SheetProps) {
  const ref = useRef<BottomSheetModal>(null);

  useEffect(() => {
    if (visible) {
      ref.current?.present();
    } else {
      ref.current?.dismiss();
    }
  }, [visible]);

  const renderBackdrop = useCallback(
    (props: BottomSheetBackdropProps) => (
      <BottomSheetBackdrop
        {...props}
        disappearsOnIndex={-1}
        appearsOnIndex={0}
        pressBehavior="close"
      />
    ),
    []
  );

  const body = (
    <>
      {title ? (
        <View className="flex-row items-center justify-between px-4 pb-2">
          <Text className="text-lg font-semibold text-zinc-900">{title}</Text>
          <Pressable
            accessibilityRole="button"
            accessibilityLabel="Fechar"
            onPress={onClose}
            className="rounded-md p-2 active:bg-zinc-100"
          >
            <X size={18} color="#71717a" />
          </Pressable>
        </View>
      ) : null}
      {children}
    </>
  );

  return (
    <BottomSheetModal
      ref={ref}
      enableDynamicSizing
      onDismiss={onClose}
      backdropComponent={renderBackdrop}
      backgroundStyle={{ backgroundColor: '#ffffff' }}
      handleIndicatorStyle={{ backgroundColor: '#d4d4d8' }}
    >
      {scrollable ? (
        <BottomSheetScrollView className="pb-6">{body}</BottomSheetScrollView>
      ) : (
        <BottomSheetView className="pb-6">{body}</BottomSheetView>
      )}
    </BottomSheetModal>
  );
}
