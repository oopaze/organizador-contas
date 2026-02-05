import React, { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { SubTransaction, paySubTransaction } from '@/services';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/app/components/ui/table';
import { Badge } from '@/app/components/ui/badge';
import { Button } from '@/app/components/ui/button';
import { Skeleton } from '@/app/components/ui/skeleton';
import { ConfirmationDialog } from './confirmation-dialog';
import { MoreVertical, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

interface ActorSubTransactionsTableProps {
  subTransactions?: SubTransaction[];
  loading?: boolean;
  error?: string | null;
  onUpdate?: () => void;
}

export const ActorSubTransactionsTable: React.FC<ActorSubTransactionsTableProps> = ({
  subTransactions = [],
  loading = false,
  error = null,
  onUpdate,
}) => {
  const [openPopoverId, setOpenPopoverId] = useState<number | null>(null);
  const [popoverPosition, setPopoverPosition] = useState<{ top: number; left: number } | null>(null);
  const [payDialogOpen, setPayDialogOpen] = useState(false);
  const [subTransactionToPay, setSubTransactionToPay] = useState<SubTransaction | null>(null);
  const [isPaying, setIsPaying] = useState(false);
  const buttonRefs = useRef<{ [key: number]: HTMLButtonElement | null }>({});
  const dropdownRef = useRef<HTMLDivElement | null>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (openPopoverId !== null) {
        const button = buttonRefs.current[openPopoverId];
        const dropdown = dropdownRef.current;
        const target = event.target as Node;

        // Don't close if clicking on the button or the dropdown
        if (button?.contains(target) || dropdown?.contains(target)) {
          return;
        }

        setOpenPopoverId(null);
        setPopoverPosition(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [openPopoverId]);

  const handleTogglePopover = (subTransactionId: number, buttonElement: HTMLButtonElement) => {
    if (openPopoverId === subTransactionId) {
      setOpenPopoverId(null);
      setPopoverPosition(null);
    } else {
      const rect = buttonElement.getBoundingClientRect();
      // For fixed positioning, use viewport coordinates directly
      setPopoverPosition({
        top: rect.bottom + 4,
        left: rect.right - 160, // 160 = dropdown width (w-40)
      });
      setOpenPopoverId(subTransactionId);
    }
  };

  const handlePayClick = (subTransaction: SubTransaction) => {
    setSubTransactionToPay(subTransaction);
    setPayDialogOpen(true);
    setOpenPopoverId(null);
    setPopoverPosition(null);
  };

  const handleConfirmPay = async () => {
    if (!subTransactionToPay) return;

    const wasPaid = !!subTransactionToPay.paid_at;
    setIsPaying(true);
    try {
      await paySubTransaction(subTransactionToPay.id);
      toast.success(wasPaid ? 'Subtransação marcada como não paga' : 'Subtransação marcada como paga');
      setPayDialogOpen(false);
      setSubTransactionToPay(null);
      onUpdate?.();
    } catch (error) {
      toast.error(wasPaid ? 'Falha ao desmarcar subtransação como paga' : 'Falha ao marcar subtransação como paga');
      console.error('Error paying subtransaction:', error);
    } finally {
      setIsPaying(false);
    }
  };

  if (loading) {
    return (
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Data</TableHead>
            <TableHead>Nome</TableHead>
            <TableHead>Descrição</TableHead>
            <TableHead>Parcela</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="text-right">Valor</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {[1, 2, 3].map((i) => (
            <TableRow key={i}>
              <TableCell><Skeleton className="h-4 w-20" /></TableCell>
              <TableCell><Skeleton className="h-4 w-48" /></TableCell>
              <TableCell><Skeleton className="h-4 w-32" /></TableCell>
              <TableCell><Skeleton className="h-4 w-12" /></TableCell>
              <TableCell><Skeleton className="h-4 w-16" /></TableCell>
              <TableCell className="text-right"><Skeleton className="h-4 w-16 ml-auto" /></TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    );
  }

  if (error) {
    return (
      <div className="text-center py-4 text-red-500 text-sm">
        {error}
      </div>
    );
  }

  if (subTransactions.length === 0) {
    return (
      <div className="text-center py-4 text-muted-foreground text-sm">
        Nenhuma subtransação vinculada a este ator
      </div>
    );
  }

  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Data</TableHead>
            <TableHead>Nome</TableHead>
            <TableHead>Fonte</TableHead>
            <TableHead>Descrição</TableHead>
            <TableHead>Parcela</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="text-right">Valor</TableHead>
            <TableHead className="w-[60px]"></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {subTransactions.map((subTransaction) => {
            const amount = parseFloat(subTransaction.amount);
            const isNegative = amount < 0;
            return (
              <TableRow key={subTransaction.id}>
                <TableCell className="text-sm">
                  {new Date(subTransaction.date).toLocaleDateString('pt-BR')}
                </TableCell>
                <TableCell className="text-sm max-w-[200px] truncate">
                  {subTransaction.description}
                </TableCell>
                <TableCell className="text-sm max-w-[300px] truncate">
                  {subTransaction.transaction_identifier}
                </TableCell>
                <TableCell className="text-sm max-w-[300px] truncate">
                  {subTransaction.user_provided_description || (
                    <span className="text-muted-foreground">-</span>
                  )}
                </TableCell>
                <TableCell>
                  {subTransaction.installment_info && subTransaction.installment_info !== 'not installment' ? (
                    <Badge variant="outline" className="text-xs">
                      {subTransaction.installment_info.replace('installment ', '').replace(' of ', '/')}
                    </Badge>
                  ) : (
                    <span className="text-xs text-muted-foreground">À vista</span>
                  )}
                </TableCell>
                <TableCell>
                  {subTransaction.paid_at ? (
                    <Badge className="bg-green-100 text-green-800">Pago</Badge>
                  ) : (
                    <Badge className="bg-red-100 text-red-800">Pendente</Badge>
                  )}
                </TableCell>
                <TableCell className={`text-right text-sm ${isNegative ? 'text-green-600' : 'text-red-600'}`}>
                  R$ {Math.abs(amount).toFixed(2)}
                </TableCell>
                <TableCell>
                  <div className="flex items-center justify-end gap-1">
                    <Button
                      ref={(el) => { buttonRefs.current[subTransaction.id] = el; }}
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        e.preventDefault();
                        handleTogglePopover(subTransaction.id, e.currentTarget);
                      }}
                      onPointerDown={(e) => e.stopPropagation()}
                      title="Mais opções"
                    >
                      <MoreVertical className="w-4 h-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>

      {/* Portal dropdown menu */}
      {openPopoverId !== null && popoverPosition && createPortal(
        <div
          ref={dropdownRef}
          className="fixed z-[9999] w-40 rounded-md border bg-popover p-1 shadow-md"
          style={{
            top: popoverPosition.top,
            left: popoverPosition.left,
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex flex-col gap-1">
            {subTransactions.find(st => st.id === openPopoverId) && (
              <Button
                variant="ghost"
                size="sm"
                className="justify-start w-full"
                onClick={() => {
                  const st = subTransactions.find(s => s.id === openPopoverId);
                  if (st) handlePayClick(st);
                }}
              >
                <CheckCircle className="w-4 h-4 mr-2" />
                {subTransactions.find(st => st.id === openPopoverId)?.paid_at ? 'Despagar' : 'Pagar'}
              </Button>
            )}
          </div>
        </div>,
        document.body
      )}

      <ConfirmationDialog
        open={payDialogOpen}
        onOpenChange={setPayDialogOpen}
        onConfirm={handleConfirmPay}
        title={subTransactionToPay?.paid_at ? 'Despagar subtransação' : 'Pagar subtransação'}
        description={subTransactionToPay?.paid_at
          ? `Tem certeza que deseja marcar a subtransação "${subTransactionToPay?.description}" como não paga?`
          : `Tem certeza que deseja marcar a subtransação "${subTransactionToPay?.description}" como paga?`
        }
        confirmText={subTransactionToPay?.paid_at ? 'Despagar' : 'Pagar'}
        cancelText="Cancelar"
        variant="warning"
        icon={CheckCircle}
        isLoading={isPaying}
      />
    </>
  );
};

