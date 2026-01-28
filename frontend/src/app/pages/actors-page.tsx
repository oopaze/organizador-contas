import React, { useEffect, useState, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/app/components/ui/table';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/app/components/ui/collapsible';
import { Skeleton } from '@/app/components/ui/skeleton';
import { Button } from '@/app/components/ui/button';
import { Users, ChevronRight, ChevronLeft, Trash2, Plus, Pencil, Wallet, TrendingUp, UserCheck } from 'lucide-react';
import { Actor, getActors, getActor, deleteActor } from '@/services';
import { ActorSubTransactionsTable } from '@/app/components/actor-sub-transactions-table';
import { ConfirmationDialog } from '@/app/components/confirmation-dialog';
import { AddActorDialog } from '@/app/components/add-actor-dialog';
import { EditActorDialog } from '@/app/components/edit-actor-dialog';
import { toast } from 'sonner';

export const ActorsPage: React.FC = () => {
  const [actors, setActors] = useState<Actor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [actorToDelete, setActorToDelete] = useState<Actor | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [actorToEdit, setActorToEdit] = useState<Actor | null>(null);
  const [actorDetails, setActorDetails] = useState<Record<number, Actor>>({});
  const [loadingActors, setLoadingActors] = useState<Set<number>>(new Set());
  const [actorErrors, setActorErrors] = useState<Record<number, string | null>>({});

  // Month/Year filter
  const [selectedMonth, setSelectedMonth] = useState<string>(() => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  });

  // Format selected month for display (e.g., "Janeiro 2026")
  const formatMonthDisplay = (monthValue: string) => {
    const [year, month] = monthValue.split('-').map(Number);
    const date = new Date(year, month - 1, 1);
    const label = date.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
    return label.charAt(0).toUpperCase() + label.slice(1);
  };

  // Navigate to previous month
  const goToPreviousMonth = () => {
    const [year, month] = selectedMonth.split('-').map(Number);
    const date = new Date(year, month - 2, 1);
    setSelectedMonth(`${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`);
  };

  // Navigate to next month
  const goToNextMonth = () => {
    const [year, month] = selectedMonth.split('-').map(Number);
    const date = new Date(year, month, 1);
    setSelectedMonth(`${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`);
  };

  const fetchActors = useCallback(async () => {
    setLoading(true);
    setError(null);
    setActorDetails({}); // Clear cached details when month changes
    setExpandedRows(new Set()); // Close expanded rows when month changes
    try {
      const dueDate = `${selectedMonth}-01`; // Convert YYYY-MM to YYYY-MM-DD
      const data = await getActors({ due_date: dueDate });
      setActors(data);
    } catch (err) {
      setError('Falha ao carregar atores');
      console.error('Error fetching actors:', err);
    } finally {
      setLoading(false);
    }
  }, [selectedMonth]);

  useEffect(() => {
    fetchActors();
  }, [fetchActors]);

  const toggleRow = async (id: number) => {
    const isCurrentlyExpanded = expandedRows.has(id);

    setExpandedRows(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });

    // Fetch actor details when expanding (if not already loaded)
    if (!isCurrentlyExpanded && !actorDetails[id]) {
      setLoadingActors(prev => new Set(prev).add(id));
      setActorErrors(prev => ({ ...prev, [id]: null }));

      try {
        const dueDate = `${selectedMonth}-01`; // Convert YYYY-MM to YYYY-MM-DD
        const detail = await getActor(id, { due_date: dueDate });
        setActorDetails(prev => ({ ...prev, [id]: detail }));
      } catch (err) {
        console.error('Error fetching actor details:', err);
        setActorErrors(prev => ({ ...prev, [id]: 'Falha ao carregar subtransações' }));
      } finally {
        setLoadingActors(prev => {
          const newSet = new Set(prev);
          newSet.delete(id);
          return newSet;
        });
      }
    }
  };

  const handleDeleteClick = (actor: Actor, e: React.MouseEvent) => {
    e.stopPropagation();
    setActorToDelete(actor);
    setDeleteDialogOpen(true);
  };

  const handleEditClick = (actor: Actor, e: React.MouseEvent) => {
    e.stopPropagation();
    setActorToEdit(actor);
    setEditDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!actorToDelete) return;

    setIsDeleting(true);
    try {
      await deleteActor(actorToDelete.id);
      toast.success(`Ator "${actorToDelete.name}" excluído com sucesso`);
      setDeleteDialogOpen(false);
      setActorToDelete(null);
      await fetchActors();
    } catch (err) {
      console.error('Error deleting actor:', err);
      toast.error('Falha ao excluir ator');
    } finally {
      setIsDeleting(false);
    }
  };

  // Calculate actor insights
  const totalSpent = actors.reduce((sum, actor) => sum + (actor.total_spent || 0), 0);
  const activeActors = actors.filter(actor => (actor.total_spent || 0) > 0);
  const topSpender = activeActors.length > 0
    ? activeActors.reduce((top, actor) =>
        (actor.total_spent || 0) > (top.total_spent || 0) ? actor : top
      )
    : null;

  return (
    <>
      {/* Month Navigation */}
      <div className="mb-6 flex justify-center">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" onClick={goToPreviousMonth}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-lg font-semibold text-gray-900 min-w-[200px] text-center">
            {formatMonthDisplay(selectedMonth)}
          </span>
          <Button variant="outline" size="icon" onClick={goToNextMonth}>
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Gasto</CardTitle>
            <Wallet className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              R$ {totalSpent.toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Soma de todos os atores
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Maior Gastador</CardTitle>
            <TrendingUp className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {topSpender ? topSpender.name : '-'}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {topSpender ? `R$ ${topSpender.total_spent?.toFixed(2)}` : 'Nenhum gasto no período'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Atores Ativos</CardTitle>
            <UserCheck className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {activeActors.length}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              De {actors.length} atores cadastrados
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              <CardTitle>Atores</CardTitle>
            </div>
            <CardDescription>Gerencie os atores das suas transações</CardDescription>
          </div>
          <Button onClick={() => setAddDialogOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Adicionar Ator
          </Button>
        </CardHeader>
      <CardContent>
        {loading ? (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[50px]"></TableHead>
                <TableHead>Nome</TableHead>
                <TableHead className="w-[100px] text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {[1, 2, 3, 4, 5].map((i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-4 w-4" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-48" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-8 w-8 ml-auto" /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        ) : error ? (
          <div className="text-center py-8 text-red-500">
            {error}
          </div>
        ) : actors.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            Nenhum ator encontrado
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[50px]"></TableHead>
                <TableHead>Nome</TableHead>
                <TableHead>Gasto</TableHead>
                <TableHead className="w-[100px] text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {actors.map((actor) => {
                const isExpanded = expandedRows.has(actor.id);
                return (
                  <Collapsible key={actor.id} asChild open={isExpanded}>
                    <>
                      <CollapsibleTrigger asChild>
                        <TableRow
                          className="cursor-pointer hover:bg-muted/50"
                          onClick={() => toggleRow(actor.id)}
                        >
                          <TableCell>
                            <ChevronRight
                              className={`h-4 w-4 transition-transform duration-200 ${
                                isExpanded ? 'rotate-90' : ''
                              }`}
                            />
                          </TableCell>
                          <TableCell className="font-medium">{actor.name}</TableCell>
                          <TableCell className="font-medium">
                            R$ {actor.total_spent?.toFixed(2) || Number(0).toFixed(2)}
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex items-center justify-end gap-1">
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 text-muted-foreground hover:text-primary"
                                onClick={(e) => handleEditClick(actor, e)}
                              >
                                <Pencil className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 text-muted-foreground hover:text-destructive"
                                onClick={(e) => handleDeleteClick(actor, e)}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      </CollapsibleTrigger>
                      <CollapsibleContent asChild>
                        <TableRow className="bg-muted/30 hover:bg-muted/30">
                          <TableCell colSpan={4} className="p-0">
                            <div className="px-8 py-4">
                              <h4 className="text-sm font-medium mb-2 text-muted-foreground">
                                Subtransações vinculadas
                              </h4>
                              <ActorSubTransactionsTable
                                subTransactions={actorDetails[actor.id]?.sub_transactions}
                                loading={loadingActors.has(actor.id)}
                                error={actorErrors[actor.id]}
                              />
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
        )}
      </CardContent>

      <ConfirmationDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        onConfirm={handleConfirmDelete}
        title="Excluir ator"
        description={`Tem certeza que deseja excluir o ator "${actorToDelete?.name}"? Esta ação não pode ser desfeita.`}
        confirmText="Excluir"
        cancelText="Cancelar"
        variant="danger"
        isLoading={isDeleting}
      />

      <AddActorDialog
        open={addDialogOpen}
        onOpenChange={setAddDialogOpen}
        onSuccess={fetchActors}
      />

      <EditActorDialog
        open={editDialogOpen}
        onOpenChange={setEditDialogOpen}
        onSuccess={fetchActors}
        actor={actorToEdit}
      />
    </Card>
    </>
  );
};

