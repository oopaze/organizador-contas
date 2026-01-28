import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/app/components/ui/dialog';
import { Button } from '@/app/components/ui/button';
import { AlertTriangle, Trash2, Info, HelpCircle, LucideIcon } from 'lucide-react';

export type ConfirmationDialogVariant = 'danger' | 'warning' | 'info' | 'default';

interface ConfirmationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void | Promise<void>;
  title: string;
  description?: string;
  confirmText?: string;
  cancelText?: string;
  variant?: ConfirmationDialogVariant;
  icon?: LucideIcon;
  isLoading?: boolean;
}

const variantConfig: Record<ConfirmationDialogVariant, {
  icon: LucideIcon;
  iconClassName: string;
  confirmVariant: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
}> = {
  danger: {
    icon: Trash2,
    iconClassName: 'text-destructive',
    confirmVariant: 'destructive',
  },
  warning: {
    icon: AlertTriangle,
    iconClassName: 'text-amber-500',
    confirmVariant: 'default',
  },
  info: {
    icon: Info,
    iconClassName: 'text-blue-500',
    confirmVariant: 'default',
  },
  default: {
    icon: HelpCircle,
    iconClassName: 'text-muted-foreground',
    confirmVariant: 'default',
  },
};

export const ConfirmationDialog: React.FC<ConfirmationDialogProps> = ({
  open,
  onOpenChange,
  onConfirm,
  title,
  description,
  confirmText = 'Confirmar',
  cancelText = 'Cancelar',
  variant = 'default',
  icon: CustomIcon,
  isLoading = false,
}) => {
  const config = variantConfig[variant];
  const Icon = CustomIcon || config.icon;

  const handleConfirm = async () => {
    await onConfirm();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-full bg-muted ${config.iconClassName}`}>
              <Icon className="h-5 w-5" />
            </div>
            <DialogTitle>{title}</DialogTitle>
          </div>
          {description && (
            <DialogDescription className="pt-2">
              {description}
            </DialogDescription>
          )}
        </DialogHeader>
        <DialogFooter className="mt-4">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isLoading}
          >
            {cancelText}
          </Button>
          <Button
            variant={config.confirmVariant}
            onClick={handleConfirm}
            disabled={isLoading}
          >
            {isLoading ? 'Aguarde...' : confirmText}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

