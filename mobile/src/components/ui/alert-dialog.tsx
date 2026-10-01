import { Button } from './button';
import { Dialog } from './dialog';

export interface AlertDialogProps {
  visible: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  title?: string;
  description?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  destructive?: boolean;
}

export function AlertDialog({
  visible,
  onConfirm,
  onCancel,
  title,
  description,
  confirmLabel = 'Confirmar',
  cancelLabel = 'Cancelar',
  destructive,
}: AlertDialogProps) {
  return (
    <Dialog
      visible={visible}
      onClose={onCancel}
      title={title}
      description={description}
      showClose={false}
      footer={
        <>
          <Button variant="outline" onPress={onCancel}>
            {cancelLabel}
          </Button>
          <Button variant={destructive ? 'destructive' : 'default'} onPress={onConfirm}>
            {confirmLabel}
          </Button>
        </>
      }
    />
  );
}
