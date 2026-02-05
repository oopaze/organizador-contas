import React, { useEffect, useState, useCallback } from 'react';
import { SubTransaction, getTransaction, deleteSubTransaction, paySubTransaction, Actor } from '@/services';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/app/components/ui/table';
import { Badge } from '@/app/components/ui/badge';
import { Button } from '@/app/components/ui/button';
import { Skeleton } from '@/app/components/ui/skeleton';
import { Pencil, Trash2, MoreVertical, CheckCircle } from 'lucide-react';
import { EditSubTransactionDialog } from './edit-sub-transaction-dialog';
import { ConfirmationDialog } from './confirmation-dialog';
import { toast } from 'sonner';
import { useUser } from '@/contexts/user-context';

interface SubTransactionsTableProps {
  transactionId: number;
}

export const SubTransactionsTable: React.FC<SubTransactionsTableProps> = ({
  transactionId,
}) => {
  const { user } = useUser();
  const [subTransactions, setSubTransactions] = useState<SubTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedSubTransaction, setSelectedSubTransaction] = useState<SubTransaction | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [subTransactionToDelete, setSubTransactionToDelete] = useState<SubTransaction | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [openPopoverId, setOpenPopoverId] = useState<number | null>(null);
  const [payDialogOpen, setPayDialogOpen] = useState(false);
  const [subTransactionToPay, setSubTransactionToPay] = useState<SubTransaction | null>(null);
  const [isPaying, setIsPaying] = useState(false);

  const fetchSubTransactions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const transactionDetail = await getTransaction(transactionId);
      setSubTransactions(transactionDetail.sub_transactions || []);
    } catch (err) {
      setError('Falha ao carregar subtransações');
      console.error('Error fetching subtransactions:', err);
    } finally {
      setLoading(false);
    }
  }, [transactionId]);

  useEffect(() => {
    fetchSubTransactions();
  }, [fetchSubTransactions]);

  const handleEditSubTransaction = (subTransaction: SubTransaction) => {
    setSelectedSubTransaction(subTransaction);
    setEditDialogOpen(true);
  };

  const handleEditSuccess = () => {
    fetchSubTransactions();
  };

  const handleDeleteClick = (subTransaction: SubTransaction) => {
    setSubTransactionToDelete(subTransaction);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!subTransactionToDelete) return;

    setIsDeleting(true);
    try {
      await deleteSubTransaction(subTransactionToDelete.id);
      toast.success('Subtransação excluída');
      setDeleteDialogOpen(false);
      setSubTransactionToDelete(null);
      fetchSubTransactions();
    } catch (error) {
      toast.error('Falha ao excluir subtransação');
      console.error('Error deleting subtransaction:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  const handlePayClick = (subTransaction: SubTransaction) => {
    setSubTransactionToPay(subTransaction);
    setPayDialogOpen(true);
    setOpenPopoverId(null);
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
      fetchSubTransactions();
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
            <TableHead>Ator</TableHead>
            <TableHead className="text-right">Valor</TableHead>
            <TableHead className="w-[50px]"></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {[1, 2, 3].map((i) => (
            <TableRow key={i}>
              <TableCell><Skeleton className="h-4 w-20" /></TableCell>
              <TableCell><Skeleton className="h-4 w-48" /></TableCell>
              <TableCell><Skeleton className="h-4 w-32" /></TableCell>
              <TableCell><Skeleton className="h-4 w-12" /></TableCell>
              <TableCell><Skeleton className="h-4 w-24" /></TableCell>
              <TableCell className="text-right"><Skeleton className="h-4 w-16 ml-auto" /></TableCell>
              <TableCell><Skeleton className="h-8 w-8" /></TableCell>
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
      <>
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <p className="text-muted-foreground text-sm mb-4">
            Nenhuma subtransação encontrada
          </p>
        </div>
      </>
    );
  }

  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>#</TableHead>
            <TableHead>Data</TableHead>
            <TableHead>Nome</TableHead>
            <TableHead>Descrição</TableHead>
            <TableHead>Parcela</TableHead>
            <TableHead>Ator</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="text-right">Valor</TableHead>
            <TableHead className="w-[50px]"></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {subTransactions.map((subTransaction) => {
            const amount = parseFloat(subTransaction.amount);
            const isNegative = amount < 0;
            return (
              <TableRow key={subTransaction.id}>
                <TableCell className="text-sm">
                  {subTransaction.id}
                </TableCell>
                <TableCell className="text-sm">
                  {new Date(subTransaction.date).toLocaleDateString('pt-BR')}
                </TableCell>
                <TableCell className="text-sm max-w-[200px] truncate">
                  {subTransaction.description}
                </TableCell>
                <TableCell className="text-sm max-w-[200px] truncate">
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
                <TableCell className="text-sm">
                  {subTransaction.actor ? (
                    <span className="text-foreground">{(subTransaction?.actor as Actor)?.name}</span>
                  ) : (
                    <span className="text-muted-foreground">{user?.profile?.first_name} {user?.profile?.last_name} (Eu)</span>
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
                  <div className="flex gap-1 relative">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleEditSubTransaction(subTransaction)}
                      title="Editar subtransação"
                    >
                      <Pencil className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteClick(subTransaction)}
                      title="Excluir subtransação"
                    >
                      <Trash2 className="w-4 h-4 text-red-600" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        e.preventDefault();
                        setOpenPopoverId(openPopoverId === subTransaction.id ? null : subTransaction.id);
                      }}
                      onPointerDown={(e) => e.stopPropagation()}
                      title="Mais opções"
                    >
                      <MoreVertical className="w-4 h-4" />
                    </Button>
                    {openPopoverId === subTransaction.id && (
                      <div
                        className="absolute right-0 top-full mt-1 z-50 w-40 rounded-md border bg-popover p-1 shadow-md"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <div className="flex flex-col gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="justify-start w-full"
                            onClick={() => handlePayClick(subTransaction)}
                          >
                            <CheckCircle className="w-4 h-4 mr-2" />
                            {subTransaction.paid_at ? 'Despagar' : 'Pagar'}
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
      {editDialogOpen && selectedSubTransaction && (
        <EditSubTransactionDialog
          key={selectedSubTransaction.id}
          open={editDialogOpen}
          onOpenChange={setEditDialogOpen}
          subTransaction={selectedSubTransaction}
          onSuccess={handleEditSuccess}
        />
      )}

      <ConfirmationDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        onConfirm={handleConfirmDelete}
        title="Excluir subtransação"
        description={`Tem certeza que deseja excluir a subtransação "${subTransactionToDelete?.description}"? Esta ação não pode ser desfeita.`}
        confirmText="Excluir"
        cancelText="Cancelar"
        variant="danger"
        isLoading={isDeleting}
      />

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

