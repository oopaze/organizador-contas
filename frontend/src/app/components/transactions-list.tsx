import React, { useMemo, useState } from 'react';
import {
  Transaction,
  deleteTransaction,
  payTransaction,
  recalculateTransactionAmount,
} from '@/services';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/app/components/ui/table';
import { Button } from '@/app/components/ui/button';
import { Badge } from '@/app/components/ui/badge';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/app/components/ui/collapsible';
import { Checkbox } from '@/app/components/ui/checkbox';
import { Label } from '@/app/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/app/components/ui/dialog';
import { Trash2, ChevronRight, Pencil, Plus, MoreVertical, CheckCircle, Calculator, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';
import { SubTransactionsTable } from './sub-transactions-table';
import { EditTransactionDialog } from './edit-transaction-dialog';
import { AddSubTransactionDialog } from './add-sub-transaction-dialog';
import { ConfirmationDialog } from './confirmation-dialog';

interface TransactionsListProps {
  type: 'expenses' | 'income' | 'all';
  transactions?: Transaction[];
  onUpdate: () => void;
  loading?: boolean;
}

const parseTypeToTransactionType = {
  expenses: 'outgoing',
  income: 'incoming',
  all: undefined,
}

const parseTypeToPortuguese = {
  expenses: 'despesa',
  income: 'receita',
  all: 'transação',
}

export const TransactionsList: React.FC<TransactionsListProps> = ({
  type,
  transactions = [],
  onUpdate,
  loading,
}) => {
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [transactionToEdit, setTransactionToEdit] = useState<Transaction | null>(null);
  const [addSubDialogOpen, setAddSubDialogOpen] = useState(false);
  const [transactionIdForSub, setTransactionIdForSub] = useState<number | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [transactionToDelete, setTransactionToDelete] = useState<Transaction | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [openPopoverId, setOpenPopoverId] = useState<number | null>(null);
  const [payDialogOpen, setPayDialogOpen] = useState(false);
  const [transactionToPay, setTransactionToPay] = useState<Transaction | null>(null);
  const [isPaying, setIsPaying] = useState(false);
  const [paySubTransactions, setPaySubTransactions] = useState(true);
  const [recalculateDialogOpen, setRecalculateDialogOpen] = useState(false);
  const [transactionToRecalculate, setTransactionToRecalculate] = useState<Transaction | null>(null);
  const [isRecalculating, setIsRecalculating] = useState(false);

  const handleEditClick = (transaction: Transaction, e: React.MouseEvent) => {
    e.stopPropagation();
    setTransactionToEdit(transaction);
    setEditDialogOpen(true);
  };

  const handleAddSubClick = (transactionId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    setTransactionIdForSub(transactionId);
    setAddSubDialogOpen(true);
  };

  const toggleRow = (id: number) => {
    setExpandedRows(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const filteredTransaction = useMemo(() => transactions.filter(t => {
    if (type === 'all') return true;
    return t.transaction_type === parseTypeToTransactionType[type];
  }), [transactions, type]);

  const handleDeleteClick = (transaction: Transaction, e: React.MouseEvent) => {
    e.stopPropagation();
    setTransactionToDelete(transaction);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!transactionToDelete) return;

    setIsDeleting(true);
    try {
      await deleteTransaction(transactionToDelete.id);
      toast.success('Transação excluída com sucesso');
      setDeleteDialogOpen(false);
      setTransactionToDelete(null);
      onUpdate();
    } catch (error) {
      toast.error('Falha ao excluir transação');
    } finally {
      setIsDeleting(false);
    }
  };

  const handlePayClick = (transaction: Transaction, e: React.MouseEvent) => {
    e.stopPropagation();
    setTransactionToPay(transaction);
    setPayDialogOpen(true);
    setOpenPopoverId(null);
  };

  const handleConfirmPay = async () => {
    if (!transactionToPay) return;

    const wasPaid = transactionToPay.is_paid;
    setIsPaying(true);
    try {
      await payTransaction(transactionToPay.id, { updateSubTransactions: paySubTransactions });
      toast.success(wasPaid ? 'Transação marcada como não paga' : 'Transação marcada como paga');
      setPayDialogOpen(false);
      setTransactionToPay(null);
      setPaySubTransactions(true); // Reset to default
      onUpdate();
    } catch (error) {
      toast.error(wasPaid ? 'Falha ao desmarcar transação como paga' : 'Falha ao marcar transação como paga');
    } finally {
      setIsPaying(false);
    }
  };

  const handleRecalculateClick = (transaction: Transaction, e: React.MouseEvent) => {
    e.stopPropagation();
    setTransactionToRecalculate(transaction);
    setRecalculateDialogOpen(true);
    setOpenPopoverId(null);
  };

  const handleConfirmRecalculate = async () => {
    if (!transactionToRecalculate) return;

    setIsRecalculating(true);
    try {
      await recalculateTransactionAmount(transactionToRecalculate.id);
      toast.success('Valor recalculado com sucesso');
      setRecalculateDialogOpen(false);
      setTransactionToRecalculate(null);
      onUpdate();
    } catch (error) {
      toast.error('Falha ao recalcular valor');
    } finally {
      setIsRecalculating(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-8 text-gray-500">
        Carregando...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Incoming Transactions */}
      {filteredTransaction.length > 0 && (
        <div>
          <h3 className="font-medium text-gray-900 mb-3">Receitas</h3>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-8"></TableHead>
                <TableHead>#</TableHead>
                <TableHead>Data</TableHead>
                <TableHead>Identificador</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Valor</TableHead>
                <TableHead className="text-right">Valor de Terceiros</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredTransaction
                .map((transaction) => {
                  const isExpanded = expandedRows.has(transaction.id);
                  return (
                    <Collapsible
                      key={transaction.id}
                      open={isExpanded}
                      onOpenChange={() => toggleRow(transaction.id)}
                      asChild
                    >
                      <>
                        <CollapsibleTrigger asChild>
                          <TableRow className="cursor-pointer hover:bg-muted/50">
                            <TableCell className="w-8 p-2">
                              <ChevronRight
                                className={`w-4 h-4 text-muted-foreground transition-transform duration-200 ${isExpanded ? 'rotate-90' : ''}`}
                              />
                            </TableCell>
                            <TableCell>
                              {transaction.id}
                            </TableCell>
                            <TableCell>
                              {new Date(transaction.due_date).toLocaleDateString('pt-BR')}
                            </TableCell>
                            <TableCell>{transaction.transaction_identifier}</TableCell>
                            <TableCell>
                              {transaction.is_salary && (
                                <Badge className="bg-green-100 text-green-800">Salário</Badge>
                              )}
                              {transaction.transaction_type === 'incoming' && !transaction.is_salary && (
                                <Badge variant="secondary">Receita</Badge>
                              )}
                              {transaction.transaction_type === 'outgoing' && (
                                <Badge variant="secondary">Despesa</Badge>
                              )}
                            </TableCell>
                            <TableCell>
                              {transaction.transaction_type === 'outgoing' ? (
                                transaction.is_paid ? (
                                  <Badge className="bg-green-100 text-green-800">Pago</Badge>
                                ) : (
                                  <Badge className="bg-red-100 text-red-800">Pendente</Badge>
                                )
                              ) : (
                                <span className="text-muted-foreground">-</span>
                              )}
                            </TableCell>
                            <TableCell className={`text-right ${transaction.transaction_type === 'incoming' ? 'text-green-600' : 'text-red-600'}`}>
                              R$ {parseFloat(transaction.total_amount).toFixed(2)}
                            </TableCell>
                            <TableCell className={`text-right ${transaction.transaction_type === 'incoming' ? 'text-green-600' : 'text-red-600'}`}>
                              R$ {transaction.amount_from_actor?.toFixed(2)}
                            </TableCell>
                            <TableCell>
                              <div className="flex gap-1 relative">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={(e) => handleAddSubClick(transaction.id, e)}
                                  title="Adicionar subtransação"
                                >
                                  <Plus className="w-4 h-4" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={(e) => handleEditClick(transaction, e)}
                                  title="Editar transação"
                                >
                                  <Pencil className="w-4 h-4" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={(e) => handleDeleteClick(transaction, e)}
                                  title="Excluir transação"
                                >
                                  <Trash2 className="w-4 h-4 text-red-600" />
                                </Button>
                                {transaction.transaction_type === 'outgoing' && (
                                  <>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        e.preventDefault();
                                        setOpenPopoverId(openPopoverId === transaction.id ? null : transaction.id);
                                      }}
                                      onPointerDown={(e) => e.stopPropagation()}
                                      title="Mais opções"
                                    >
                                      <MoreVertical className="w-4 h-4" />
                                    </Button>
                                    {openPopoverId === transaction.id && (
                                      <div
                                        className="absolute right-0 top-full mt-1 z-50 w-40 rounded-md border bg-popover p-1 shadow-md"
                                        onClick={(e) => e.stopPropagation()}
                                      >
                                        <div className="flex flex-col gap-1">
                                          <Button
                                            variant="ghost"
                                            size="sm"
                                            className="justify-start w-full"
                                            onClick={(e) => handlePayClick(transaction, e)}
                                          >
                                            <CheckCircle className="w-4 h-4 mr-2" />
                                            {transaction.is_paid ? 'Despagar' : 'Pagar'}
                                          </Button>
                                          <Button
                                            variant="ghost"
                                            size="sm"
                                            className="justify-start w-full"
                                            onClick={(e) => handleRecalculateClick(transaction, e)}
                                          >
                                            <Calculator className="w-4 h-4 mr-2" />
                                            Recalcular
                                          </Button>
                                        </div>
                                      </div>
                                    )}
                                  </>
                                )}
                              </div>
                            </TableCell>
                          </TableRow>
                        </CollapsibleTrigger>
                        <CollapsibleContent asChild>
                          <TableRow className="bg-muted/30 hover:bg-muted/30">
                            <TableCell colSpan={9} className="p-4">
                              <div className="rounded-md border bg-background p-4">
                                <SubTransactionsTable transactionId={transaction.id} />
                              </div>
                            </TableCell>
                          </TableRow>
                        </CollapsibleContent>
                      </>
                    </Collapsible>
                  );
                })}
            </TableBody>
          </Table>
        </div>
      )}

      {filteredTransaction.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          Nenhuma {parseTypeToPortuguese[type]} encontrada
        </div>
      )}

      <EditTransactionDialog
        open={editDialogOpen}
        onOpenChange={setEditDialogOpen}
        onSuccess={() => {
          setEditDialogOpen(false);
          onUpdate();
        }}
        transaction={transactionToEdit}
      />

      {transactionIdForSub && (
        <AddSubTransactionDialog
          open={addSubDialogOpen}
          onOpenChange={setAddSubDialogOpen}
          transactionId={transactionIdForSub}
          onSuccess={() => {
            setAddSubDialogOpen(false);
            onUpdate();
          }}
        />
      )}

      <ConfirmationDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        onConfirm={handleConfirmDelete}
        title="Excluir transação"
        description={`Tem certeza que deseja excluir a transação "${transactionToDelete?.transaction_identifier}"? Esta ação não pode ser desfeita.`}
        confirmText="Excluir"
        cancelText="Cancelar"
        variant="danger"
        isLoading={isDeleting}
      />

      <Dialog open={payDialogOpen} onOpenChange={setPayDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-full bg-muted text-amber-500">
                <AlertTriangle className="h-5 w-5" />
              </div>
              <DialogTitle>{transactionToPay?.is_paid ? 'Despagar transação' : 'Pagar transação'}</DialogTitle>
            </div>
            <DialogDescription className="pt-2">
              {transactionToPay?.is_paid
                ? `Tem certeza que deseja marcar a transação "${transactionToPay?.transaction_identifier}" como não paga?`
                : `Tem certeza que deseja marcar a transação "${transactionToPay?.transaction_identifier}" como paga?`
              }
            </DialogDescription>
          </DialogHeader>
          <div className="flex items-center space-x-2 py-4">
            <Checkbox
              id="paySubTransactions"
              checked={paySubTransactions}
              onCheckedChange={(checked) => setPaySubTransactions(checked === true)}
            />
            <Label htmlFor="paySubTransactions" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
              {transactionToPay?.is_paid
                ? 'Marcar todas as subtransações como não pagas também'
                : 'Marcar todas as subtransações como pagas também'
              }
            </Label>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setPayDialogOpen(false);
                setPaySubTransactions(true);
              }}
              disabled={isPaying}
            >
              Cancelar
            </Button>
            <Button
              onClick={handleConfirmPay}
              disabled={isPaying}
            >
              {isPaying ? 'Aguarde...' : (transactionToPay?.is_paid ? 'Despagar' : 'Pagar')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ConfirmationDialog
        open={recalculateDialogOpen}
        onOpenChange={setRecalculateDialogOpen}
        onConfirm={handleConfirmRecalculate}
        title="Recalcular valor"
        description={`Tem certeza que deseja recalcular o valor da transação "${transactionToRecalculate?.transaction_identifier}" com base nas subtransações? Esta ação não pode ser desfeita.`}
        confirmText="Recalcular"
        cancelText="Cancelar"
        variant="warning"
        icon={Calculator}
        isLoading={isRecalculating}
      />
    </div>
  );
};
