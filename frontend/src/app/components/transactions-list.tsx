import React, { useMemo, useState } from 'react';
import {
  Transaction,
  deleteTransaction,
} from '@/services';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/app/components/ui/table';
import { Button } from '@/app/components/ui/button';
import { Badge } from '@/app/components/ui/badge';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/app/components/ui/collapsible';
import { Trash2, ChevronRight, Pencil, Plus } from 'lucide-react';
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
                <TableHead>Data</TableHead>
                <TableHead>Identificador</TableHead>
                <TableHead>Tipo</TableHead>
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
                            <TableCell className={`text-right ${transaction.transaction_type === 'incoming' ? 'text-green-600' : 'text-red-600'}`}>
                              R$ {parseFloat(transaction.total_amount).toFixed(2)}
                            </TableCell>
                            <TableCell className={`text-right ${transaction.transaction_type === 'incoming' ? 'text-green-600' : 'text-red-600'}`}>
                              R$ {transaction.amount_from_actor?.toFixed(2)}
                            </TableCell>
                            <TableCell>
                              <div className="flex gap-1">
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
                              </div>
                            </TableCell>
                          </TableRow>
                        </CollapsibleTrigger>
                        <CollapsibleContent asChild>
                          <TableRow className="bg-muted/30 hover:bg-muted/30">
                            <TableCell colSpan={7} className="p-4">
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
    </div>
  );
};
