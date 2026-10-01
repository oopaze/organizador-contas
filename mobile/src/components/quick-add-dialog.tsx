import { useEffect, useState } from 'react';
import { Text, View } from 'react-native';
import { formatSubmitError, ISO_DATE_PATTERN } from '../lib/transaction-form';
import { InlineMessage } from './inline-message';
import { Button } from './ui/button';
import { Dialog } from './ui/dialog';
import { Input } from './ui/input';
import { Select } from './ui/select';
import { toDecimalString } from '../lib/amount';
import { toIsoDate } from '../lib/date';
import { formatCurrency } from '../lib/format';
import {
  getActors,
  quickAddTransaction,
  type Actor,
  type PaymentMethod,
  type TransactionType,
} from '../services';

interface FormErrors {
  amount?: string;
  description?: string;
  date?: string;
  cardLabel?: string;
}

function today(): string {
  return toIsoDate(new Date());
}

export interface QuickAddDialogProps {
  visible: boolean;
  onClose: () => void;
  onCreated: () => void;
}

export function QuickAddDialog({ visible, onClose, onCreated }: QuickAddDialogProps) {
  const [direction, setDirection] = useState<TransactionType>('outgoing');
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>('cash');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [date, setDate] = useState(today);
  const [installments, setInstallments] = useState('1');
  const [actorId, setActorId] = useState('none');
  const [cardLabel, setCardLabel] = useState('');
  const [actors, setActors] = useState<Actor[]>([]);
  const [loadingActors, setLoadingActors] = useState(false);
  const [actorsError, setActorsError] = useState<string | null>(null);
  const [errors, setErrors] = useState<FormErrors>({});
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!visible) return;

    setDirection('outgoing');
    setPaymentMethod('cash');
    setAmount('');
    setDescription('');
    setDate(today());
    setInstallments('1');
    setActorId('none');
    setCardLabel('');
    setErrors({});
    setError(null);
    setSuccessMessage(null);
    setSaving(false);

    let cancelled = false;
    setLoadingActors(true);
    setActorsError(null);
    getActors()
      .then((list) => {
        if (!cancelled) setActors(list);
      })
      .catch(() => {
        if (!cancelled) {
          setActors([]);
          setActorsError('Falha ao carregar atores');
        }
      })
      .finally(() => {
        if (!cancelled) setLoadingActors(false);
      });

    return () => {
      cancelled = true;
    };
  }, [visible]);

  const handleSubmit = async () => {
    if (saving || successMessage) return;

    const nextErrors: FormErrors = {};
    if (toDecimalString(amount) === null || Number(toDecimalString(amount)) <= 0) {
      nextErrors.amount = 'Informe um valor válido';
    }
    if (!description.trim()) nextErrors.description = 'Informe a descrição';
    if (!ISO_DATE_PATTERN.test(date)) nextErrors.date = 'Informe uma data válida (AAAA-MM-DD)';
    if (paymentMethod === 'credit' && !cardLabel.trim()) nextErrors.cardLabel = 'Informe o cartão';
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;

    setSaving(true);
    setError(null);
    try {
      const result = await quickAddTransaction({
        direction,
        payment_method: paymentMethod,
        amount: toDecimalString(amount) as string,
        description: description.trim(),
        date,
        installments: Math.max(1, parseInt(installments, 10) || 1),
        actor_id: actorId === 'none' ? undefined : Number(actorId),
        is_paid: false,
        ...(paymentMethod === 'credit' ? { card_label: cardLabel.trim() } : {}),
      });
      onCreated();
      setSuccessMessage(
        result.open_bill_total
          ? `Lançamento criado. Fatura em aberto: ${formatCurrency(result.open_bill_total)}`
          : 'Lançamento criado!'
      );
    } catch (submitError) {
      setError(formatSubmitError(submitError, 'Falha ao lançar'));
    } finally {
      setSaving(false);
    }
  };

  const handleClose = () => {
    setSuccessMessage(null);
    onClose();
  };

  return (
    <Dialog
      visible={visible}
      onClose={handleClose}
      title="Novo Lançamento"
      description="Entra como não pago; a categoria é sugerida pela IA e você paga depois."
      footer={
        successMessage ? (
          <Button onPress={handleClose}>Fechar</Button>
        ) : (
          <>
            <Button variant="outline" onPress={handleClose} disabled={saving}>
              Cancelar
            </Button>
            <Button onPress={() => void handleSubmit()} disabled={saving || loadingActors}>
              {saving ? 'Lançando...' : 'Lançar'}
            </Button>
          </>
        )
      }
    >
      {error ? <InlineMessage>{error}</InlineMessage> : null}
      {successMessage ? <InlineMessage tone="success">{successMessage}</InlineMessage> : null}

      <View className="flex-row gap-2">
        <Button
          className="flex-1"
          variant={direction === 'outgoing' ? 'default' : 'outline'}
          onPress={() => setDirection('outgoing')}
        >
          Despesa
        </Button>
        <Button
          className="flex-1"
          variant={direction === 'incoming' ? 'default' : 'outline'}
          onPress={() => setDirection('incoming')}
        >
          Receita
        </Button>
      </View>

      <Input
        label="Valor"
        keyboardType="decimal-pad"
        placeholder="0,00"
        value={amount}
        onChangeText={setAmount}
      />
      {errors.amount ? <Text className="-mt-2 text-sm text-red-600">{errors.amount}</Text> : null}

      <Input
        label="Descrição"
        placeholder="Ex: Padaria"
        value={description}
        onChangeText={setDescription}
      />
      {errors.description ? (
        <Text className="-mt-2 text-sm text-red-600">{errors.description}</Text>
      ) : null}

      <View className="flex-row gap-4">
        <Input
          label="Data"
          containerClassName="flex-1"
          placeholder="AAAA-MM-DD"
          value={date}
          onChangeText={setDate}
        />
        <Input
          label="Parcelas"
          containerClassName="flex-1"
          keyboardType="number-pad"
          value={installments}
          onChangeText={setInstallments}
        />
      </View>
      {errors.date ? <Text className="-mt-2 text-sm text-red-600">{errors.date}</Text> : null}

      <View className="gap-2">
        <Text className="text-sm font-medium text-zinc-900">Pagamento</Text>
        <View className="flex-row gap-2">
          <Button
            className="flex-1"
            variant={paymentMethod === 'cash' ? 'default' : 'outline'}
            onPress={() => setPaymentMethod('cash')}
          >
            Dinheiro/Débito/Pix
          </Button>
          <Button
            className="flex-1"
            variant={paymentMethod === 'credit' ? 'default' : 'outline'}
            onPress={() => setPaymentMethod('credit')}
          >
            Cartão
          </Button>
        </View>
      </View>

      {paymentMethod === 'credit' ? (
        <>
          <Input
            label="Cartão"
            placeholder="Ex.: Nubank"
            value={cardLabel}
            onChangeText={setCardLabel}
          />
          {errors.cardLabel ? (
            <Text className="-mt-2 text-sm text-red-600">{errors.cardLabel}</Text>
          ) : (
            <Text className="text-xs text-zinc-500">Vai para a fatura em aberto do cartão.</Text>
          )}
        </>
      ) : null}

      <View className="gap-2">
        <Text className="text-sm font-medium text-zinc-900">Ator (opcional)</Text>
        {loadingActors ? (
          <Text className="text-sm text-zinc-500">Carregando atores...</Text>
        ) : (
          <Select
            value={actorId}
            onValueChange={setActorId}
            options={[
              { value: 'none', label: 'Nenhum' },
              ...actors.map((actor) => ({ value: String(actor.id), label: actor.name })),
            ]}
            placeholder="Selecione um ator"
          />
        )}
        {actorsError ? <Text className="text-sm text-red-600">{actorsError}</Text> : null}
      </View>
    </Dialog>
  );
}
