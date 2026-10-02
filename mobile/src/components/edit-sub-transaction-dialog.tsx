import { useEffect, useState } from 'react';
import { Text, View } from 'react-native';
import { CATEGORY_OPTIONS, formatSubmitError, ISO_DATE_PATTERN } from '../lib/transaction-form';
import { InlineMessage } from './inline-message';
import { Button } from './ui/button';
import { Checkbox } from './ui/checkbox';
import { Dialog } from './ui/dialog';
import { Input } from './ui/input';
import { Select } from './ui/select';
import { toDecimalString } from '../lib/amount';
import { TRANSACTION_CATEGORIES } from '../lib/category-colors';
import { getActors, updateSubTransaction, type Actor, type SubTransaction } from '../services';

function findCategoryKey(category: string | undefined): string {
  if (!category) return '';
  const byKey = TRANSACTION_CATEGORIES.find((option) => option.key === category);
  if (byKey) return byKey.key;
  const byValue = TRANSACTION_CATEGORIES.find((option) => option.value === category);
  if (byValue) return byValue.key;
  return '';
}

function initialActorId(subTransaction: SubTransaction): string {
  if (subTransaction.actor_id != null) return String(subTransaction.actor_id);
  if (typeof subTransaction.actor === 'number') return String(subTransaction.actor);
  if (subTransaction.actor && typeof subTransaction.actor === 'object') {
    return String(subTransaction.actor.id);
  }
  return '';
}

function toNumber(value: string): number {
  const decimal = toDecimalString(value);
  return decimal === null ? Number.NaN : Number(decimal);
}

export interface EditSubTransactionDialogProps {
  visible: boolean;
  onClose: () => void;
  onUpdated: () => void;
  subTransaction: SubTransaction;
}

export function EditSubTransactionDialog({
  visible,
  onClose,
  onUpdated,
  subTransaction,
}: EditSubTransactionDialogProps) {
  const [description, setDescription] = useState(subTransaction.description ?? '');
  const [userProvidedDescription, setUserProvidedDescription] = useState(
    subTransaction.user_provided_description ?? ''
  );
  const [date, setDate] = useState(subTransaction.date ?? '');
  const [amount, setAmount] = useState(subTransaction.amount ?? '');
  const [installmentInfo, setInstallmentInfo] = useState(subTransaction.installment_info ?? '');
  const [category, setCategory] = useState(findCategoryKey(subTransaction.category));
  const [selectedActorId, setSelectedActorId] = useState(() => initialActorId(subTransaction));
  const [shouldDivideForActor, setShouldDivideForActor] = useState(false);
  const [actorAmount, setActorAmount] = useState('');
  const [actors, setActors] = useState<Actor[]>([]);
  const [loadingActors, setLoadingActors] = useState(false);
  const [actorsError, setActorsError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!visible) return;

    setDescription(subTransaction.description ?? '');
    setUserProvidedDescription(subTransaction.user_provided_description ?? '');
    setDate(subTransaction.date ?? '');
    setAmount(subTransaction.amount ?? '');
    setInstallmentInfo(subTransaction.installment_info ?? '');
    setCategory(findCategoryKey(subTransaction.category));
    setSelectedActorId(initialActorId(subTransaction));
    setShouldDivideForActor(false);
    setActorAmount('');
    setError(null);
    setSaving(false);

    let cancelled = false;
    setLoadingActors(true);
    setActorsError(null);
    getActors({ without_sub_transactions: true })
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
  }, [visible, subTransaction]);

  const amountNumber = toNumber(amount);
  const actorAmountNumber = toNumber(actorAmount);
  const isActorAmountValid =
    !shouldDivideForActor ||
    (actorAmount !== '' &&
      actorAmountNumber > 0 &&
      Number.isFinite(amountNumber) &&
      actorAmountNumber <= amountNumber);

  const hasActor =
    subTransaction.actor_id != null ||
    (subTransaction.actor != null && typeof subTransaction.actor === 'object');

  const handleSubmit = async () => {
    if (saving) return;
    if (date && !ISO_DATE_PATTERN.test(date)) {
      setError('Informe uma data válida (AAAA-MM-DD)');
      return;
    }
    if (toDecimalString(amount) === null) {
      setError('Informe um valor válido');
      return;
    }
    if (!isActorAmountValid) {
      setError('O valor do ator deve ser maior que 0 e menor ou igual ao valor total');
      return;
    }

    setSaving(true);
    setError(null);
    try {
      await updateSubTransaction(subTransaction.id, {
        date: date || undefined,
        description: description.trim() || undefined,
        user_provided_description: userProvidedDescription.trim() || undefined,
        amount: toDecimalString(amount) as string,
        installment_info: installmentInfo.trim() || undefined,
        category: category || undefined,
        actor: selectedActorId ? parseInt(selectedActorId, 10) : null,
        should_divide_for_actor: shouldDivideForActor || undefined,
        actor_amount:
          shouldDivideForActor && actorAmount !== '' ? actorAmountNumber : undefined,
      });
      onUpdated();
      onClose();
    } catch (submitError) {
      setError(formatSubmitError(submitError, 'Falha ao atualizar subtransação'));
    } finally {
      setSaving(false);
    }
  };

  const handleRemoveActor = async () => {
    if (saving) return;
    setSaving(true);
    setError(null);
    try {
      await updateSubTransaction(subTransaction.id, {
        user_provided_description: userProvidedDescription.trim() || undefined,
        actor: null,
      });
      onUpdated();
      onClose();
    } catch (submitError) {
      setError(formatSubmitError(submitError, 'Falha ao remover ator'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog
      visible={visible}
      onClose={onClose}
      title="Editar Subtransação"
      description="Atualize os dados da subtransação."
      footer={
        <>
          {hasActor ? (
            <Button
              variant="destructive"
              onPress={() => void handleRemoveActor()}
              disabled={saving}
            >
              Remover Ator
            </Button>
          ) : null}
          <Button variant="outline" onPress={onClose} disabled={saving}>
            Cancelar
          </Button>
          <Button
            onPress={() => void handleSubmit()}
            disabled={saving || loadingActors || !isActorAmountValid}
          >
            {saving ? 'Salvando...' : 'Salvar'}
          </Button>
        </>
      }
    >
      {error ? <InlineMessage>{error}</InlineMessage> : null}

      <Input
        label="Data"
        placeholder="AAAA-MM-DD"
        value={date}
        onChangeText={setDate}
      />
      {date && !ISO_DATE_PATTERN.test(date) ? (
        <Text className="-mt-2 text-sm text-red-600">Informe uma data válida (AAAA-MM-DD)</Text>
      ) : null}

      <Input
        label="Nome"
        placeholder="Ex: Americanas S/A"
        value={description}
        onChangeText={setDescription}
      />

      <Input
        label="Descrição"
        placeholder="Ex: Compras de meu cachorro"
        value={userProvidedDescription}
        onChangeText={setUserProvidedDescription}
      />

      <Input
        label="Valor"
        keyboardType="decimal-pad"
        placeholder="0,00"
        value={amount}
        onChangeText={setAmount}
      />

      <Input
        label="Parcela"
        placeholder="Ex: 1/12"
        value={installmentInfo}
        onChangeText={setInstallmentInfo}
      />

      <View className="gap-2">
        <Text className="text-sm font-medium text-zinc-900">Categoria</Text>
        <Select
          value={category || 'none'}
          onValueChange={(value) => setCategory(value === 'none' ? '' : value)}
          options={CATEGORY_OPTIONS}
          placeholder="Selecione uma categoria"
        />
      </View>

      <View className="gap-2">
        <Text className="text-sm font-medium text-zinc-900">Ator</Text>
        {loadingActors ? (
          <Text className="text-sm text-zinc-500">Carregando atores...</Text>
        ) : (
          <Select
            value={selectedActorId || 'none'}
            onValueChange={(value) => {
              if (value === 'none') {
                setSelectedActorId('');
                setShouldDivideForActor(false);
                setActorAmount('');
                return;
              }
              setSelectedActorId(value);
            }}
            options={[
              { value: 'none', label: 'Nenhum' },
              ...actors.map((actor) => ({ value: String(actor.id), label: actor.name })),
            ]}
            placeholder="Selecione um ator"
          />
        )}
        {actorsError ? <Text className="text-sm text-red-600">{actorsError}</Text> : null}
        {actors.length === 0 && !loadingActors ? (
          <Text className="text-sm text-zinc-500">
            Nenhum ator cadastrado. Crie um ator primeiro.
          </Text>
        ) : null}
      </View>

      {selectedActorId ? (
        <>
          <View className="flex-row items-center gap-2">
            <Checkbox
              checked={shouldDivideForActor}
              onCheckedChange={(checked) => {
                setShouldDivideForActor(checked);
                if (!checked) setActorAmount('');
              }}
              accessibilityLabel="Atribuir valor parcial ao ator"
            />
            <Text className="text-sm text-zinc-900">Atribuir valor parcial ao ator</Text>
          </View>

          {shouldDivideForActor ? (
            <View className="gap-2">
              <Input
                label="Valor do Ator"
                keyboardType="decimal-pad"
                placeholder="0,00"
                value={actorAmount}
                onChangeText={setActorAmount}
              />
              {actorAmount !== '' && actorAmountNumber <= 0 ? (
                <Text className="text-xs text-red-600">O valor deve ser maior que 0.</Text>
              ) : null}
              {actorAmount !== '' &&
              Number.isFinite(actorAmountNumber) &&
              amountNumber > 0 &&
              actorAmountNumber > amountNumber ? (
                <Text className="text-xs text-red-600">
                  O valor não pode ser maior que o valor total ({amount}).
                </Text>
              ) : null}
              {actorAmount !== '' && isActorAmountValid ? (
                <Text className="text-xs text-zinc-500">
                  O valor restante ({(amountNumber - actorAmountNumber).toFixed(2)}) permanecerá na
                  subtransação original.
                </Text>
              ) : null}
            </View>
          ) : null}
        </>
      ) : null}
    </Dialog>
  );
}
