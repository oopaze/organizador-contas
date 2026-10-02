import { useState } from 'react';
import { Linking, Text, View } from 'react-native';
import Download from 'lucide-react-native/icons/download';
import Pencil from 'lucide-react-native/icons/pencil';
import Trash from 'lucide-react-native/icons/trash';
import { EmptyState } from './empty-state';
import { InlineMessage } from './inline-message';
import { AlertDialog } from './ui/alert-dialog';
import { Button } from './ui/button';
import { Skeleton } from './ui/skeleton';
import { parseIsoDate } from '../lib/date';
import { resolveFileUrl } from '../lib/file-url';
import { formatCurrency } from '../lib/format';
import { formatSubmitError } from '../lib/transaction-form';
import { deleteLoanPayment, type LoanPayment } from '../services';

export interface LoanPaymentsListProps {
  payments?: LoanPayment[];
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
  /** Abre o diálogo de edição; sem ele o botão Editar não aparece. */
  onEdit?: (payment: LoanPayment) => void;
  /** Chamado após apagar com sucesso para a tela reler os dados. */
  onChanged: () => void;
}

function PaymentCard({
  payment,
  onEdit,
  onDelete,
}: {
  payment: LoanPayment;
  onEdit?: (payment: LoanPayment) => void;
  onDelete: (payment: LoanPayment) => void;
}) {
  const fileUrl = resolveFileUrl(payment.file_url);

  return (
    <View className="gap-2 rounded-lg border border-zinc-200 bg-white p-3">
      <View className="flex-row items-center justify-between gap-3">
        <Text className="text-sm font-medium text-zinc-900">
          {parseIsoDate(payment.paid_at).toLocaleDateString('pt-BR')}
        </Text>
        <Text className="text-sm font-semibold text-emerald-700">
          {formatCurrency(payment.amount)}
        </Text>
      </View>

      <Text className="text-sm text-zinc-600">{payment.note?.trim() || '—'}</Text>

      <View className="flex-row items-center justify-end gap-2">
        {fileUrl ? (
          <Button
            variant="ghost"
            size="sm"
            accessibilityLabel="Abrir comprovante do pagamento"
            onPress={() => void Linking.openURL(fileUrl)}
          >
            <Download size={16} color="#4f46e5" />
            <Text className="text-sm font-medium text-indigo-600">Baixar</Text>
          </Button>
        ) : null}
        {onEdit ? (
          <Button
            variant="ghost"
            size="icon"
            accessibilityLabel="Editar pagamento"
            onPress={() => onEdit(payment)}
          >
            <Pencil size={16} color="#18181b" />
          </Button>
        ) : null}
        <Button
          variant="ghost"
          size="icon"
          accessibilityLabel="Remover pagamento"
          onPress={() => onDelete(payment)}
        >
          <Trash size={16} color="#dc2626" />
        </Button>
      </View>
    </View>
  );
}

export function LoanPaymentsList({
  payments,
  loading,
  error,
  onRetry,
  onEdit,
  onChanged,
}: LoanPaymentsListProps) {
  const [paymentToDelete, setPaymentToDelete] = useState<LoanPayment | null>(null);
  const [working, setWorking] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const items = payments ?? [];

  const handleConfirmDelete = async () => {
    if (!paymentToDelete || working) return;

    setWorking(true);
    setActionError(null);
    try {
      await deleteLoanPayment(paymentToDelete.id);
      setPaymentToDelete(null);
      onChanged();
    } catch (submitError) {
      setPaymentToDelete(null);
      setActionError(formatSubmitError(submitError, 'Falha ao remover o pagamento'));
    } finally {
      setWorking(false);
    }
  };

  if (loading && items.length === 0) {
    return (
      <View testID="loan-payments-loading" className="gap-2">
        {[0, 1].map((index) => (
          <Skeleton key={index} className="h-20 w-full" />
        ))}
      </View>
    );
  }

  if (error && items.length === 0) {
    return (
      <EmptyState
        title={error}
        action={
          onRetry ? (
            <Button variant="outline" onPress={onRetry}>
              Tentar novamente
            </Button>
          ) : undefined
        }
      />
    );
  }

  if (items.length === 0) {
    return <EmptyState title="Nenhum pagamento ainda." />;
  }

  return (
    <View className="gap-2">
      {actionError ? <InlineMessage>{actionError}</InlineMessage> : null}

      {items.map((payment) => (
        <PaymentCard
          key={payment.id}
          payment={payment}
          onEdit={onEdit}
          onDelete={setPaymentToDelete}
        />
      ))}

      <AlertDialog
        visible={paymentToDelete !== null}
        onCancel={() => setPaymentToDelete(null)}
        onConfirm={() => void handleConfirmDelete()}
        title="Remover pagamento"
        description="Tem certeza que deseja remover este pagamento? Esta ação não pode ser desfeita."
        confirmLabel="Excluir"
        cancelLabel="Cancelar"
        destructive
      />
    </View>
  );
}
