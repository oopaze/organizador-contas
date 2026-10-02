import { useState } from 'react';
import { Pressable, Text, View } from 'react-native';
import ChevronLeft from 'lucide-react-native/icons/chevron-left';
import ChevronRight from 'lucide-react-native/icons/chevron-right';
import { Button } from './ui/button';
import { Sheet } from './ui/sheet';
import { cn } from './ui/utils';
import { formatMonthYear, parseIsoDate } from '../lib/date';

const MONTHS = [
  'Janeiro',
  'Fevereiro',
  'Março',
  'Abril',
  'Maio',
  'Junho',
  'Julho',
  'Agosto',
  'Setembro',
  'Outubro',
  'Novembro',
  'Dezembro',
];

export interface MonthPickerProps {
  /** Mês selecionado no formato `YYYY-MM`. */
  value: string;
  onChange: (value: string) => void;
}

function formatMonthLabel(value: string): string {
  const label = formatMonthYear(parseIsoDate(`${value}-01`));
  return label.charAt(0).toUpperCase() + label.slice(1);
}

export function MonthPicker({ value, onChange }: MonthPickerProps) {
  const [open, setOpen] = useState(false);
  const [year, month] = value.split('-').map(Number);
  const [pickerYear, setPickerYear] = useState(year);

  const openPicker = () => {
    setPickerYear(year);
    setOpen(true);
  };

  const goToMonth = (offset: number) => {
    const date = new Date(year, month - 1 + offset, 1);
    const nextMonth = String(date.getMonth() + 1).padStart(2, '0');
    onChange(`${date.getFullYear()}-${nextMonth}`);
  };

  const selectMonth = (index: number) => {
    onChange(`${pickerYear}-${String(index + 1).padStart(2, '0')}`);
    setOpen(false);
  };

  return (
    <>
      <View className="flex-row items-center justify-center gap-3">
        <Button
          variant="outline"
          size="icon"
          accessibilityLabel="Mês anterior"
          onPress={() => goToMonth(-1)}
        >
          <ChevronLeft size={16} color="#18181b" />
        </Button>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel="Selecionar mês"
          onPress={openPicker}
          className="min-w-[180px] items-center rounded-md px-3 py-2 active:bg-zinc-100"
        >
          <Text className="text-lg font-semibold text-zinc-900">{formatMonthLabel(value)}</Text>
        </Pressable>
        <Button
          variant="outline"
          size="icon"
          accessibilityLabel="Próximo mês"
          onPress={() => goToMonth(1)}
        >
          <ChevronRight size={16} color="#18181b" />
        </Button>
      </View>

      <Sheet visible={open} onClose={() => setOpen(false)} title="Selecionar mês">
        <View className="px-4">
          <View className="mb-3 flex-row items-center justify-between">
            <Button
              variant="ghost"
              size="icon"
              accessibilityLabel="Ano anterior"
              onPress={() => setPickerYear((current) => current - 1)}
            >
              <ChevronLeft size={16} color="#18181b" />
            </Button>
            <Text className="text-base font-semibold text-zinc-900">{pickerYear}</Text>
            <Button
              variant="ghost"
              size="icon"
              accessibilityLabel="Próximo ano"
              onPress={() => setPickerYear((current) => current + 1)}
            >
              <ChevronRight size={16} color="#18181b" />
            </Button>
          </View>

          <View className="flex-row flex-wrap">
            {MONTHS.map((label, index) => {
              const selected = pickerYear === year && index + 1 === month;
              return (
                <Pressable
                  key={label}
                  accessibilityRole="button"
                  accessibilityLabel={`${label} ${pickerYear}`}
                  accessibilityState={{ selected }}
                  onPress={() => selectMonth(index)}
                  className={cn('w-1/3 items-center rounded-md py-3', selected ? 'bg-emerald-600' : 'active:bg-zinc-100')}
                >
                  <Text className={cn('text-sm', selected ? 'font-medium text-white' : 'text-zinc-700')}>
                    {label}
                  </Text>
                </Pressable>
              );
            })}
          </View>
        </View>
      </Sheet>
    </>
  );
}
