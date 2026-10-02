import { useContext, type ReactNode } from 'react';
import { Modal, Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaInsetsContext } from 'react-native-safe-area-context';
import X from 'lucide-react-native/icons/x';

export interface SheetProps {
  visible: boolean;
  onClose: () => void;
  title?: string;
  /** Usa lista rolável (Select/DropdownMenu); por padrão dimensiona pelo conteúdo. */
  scrollable?: boolean;
  children?: ReactNode;
}

/**
 * Bottom sheet em Modal do RN (não no @gorhom/bottom-sheet): a janela nativa
 * do Modal empilha acima do Modal do Dialog no Android, então Select/Dropdown
 * abertos de dentro de um diálogo ficam tocáveis.
 */
export function Sheet({ visible, onClose, title, scrollable, children }: SheetProps) {
  // Com edge-to-edge, a barra de navegação do Android sobrepõe o painel:
  // o inset inferior afasta o conteúdo (menus de card, select, mês) dos botões.
  const bottomInset = useContext(SafeAreaInsetsContext)?.bottom ?? 0;

  if (!visible) return null;

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
    <Modal
      visible
      transparent
      animationType="slide"
      onRequestClose={onClose}
      statusBarTranslucent
      testID="sheet-modal"
    >
      <View className="flex-1 justify-end bg-black/40">
        <Pressable accessibilityLabel="Fechar" className="flex-1" onPress={onClose} />
        <View
          testID="sheet-panel"
          style={{ paddingBottom: bottomInset }}
          className="max-h-[85%] rounded-t-2xl bg-white"
        >
          {scrollable ? (
            <ScrollView className="pb-6" keyboardShouldPersistTaps="handled">
              {body}
            </ScrollView>
          ) : (
            <View className="pb-6">{body}</View>
          )}
        </View>
      </View>
    </Modal>
  );
}
