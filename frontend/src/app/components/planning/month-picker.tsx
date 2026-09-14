import React, { useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/app/components/ui/button';
import { Popover, PopoverContent, PopoverTrigger } from '@/app/components/ui/popover';

const MONTHS = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];

const monthLabel = (value: string) => {
  const [year, month] = value.split('-').map(Number);
  return `${MONTHS[month - 1]}/${String(year).slice(2)}`;
};

export const MonthPicker: React.FC<{
  value: string;
  onChange: (value: string) => void;
  ariaLabel: string;
}> = ({ value, onChange, ariaLabel }) => {
  const [open, setOpen] = useState(false);
  const [year, month] = value.split('-').map(Number);
  const [viewYear, setViewYear] = useState(year);

  const pick = (monthIndex: number) => {
    onChange(`${viewYear}-${String(monthIndex + 1).padStart(2, '0')}`);
    setOpen(false);
  };

  return (
    <Popover
      open={open}
      onOpenChange={(next) => {
        setOpen(next);
        if (next) setViewYear(year);
      }}
    >
      <PopoverTrigger asChild>
        <Button variant="outline" aria-label={ariaLabel} className="w-[104px] justify-center font-normal">
          {monthLabel(value)}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[232px] p-3" align="center">
        <div className="flex items-center justify-between pb-2">
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7"
            onClick={() => setViewYear(viewYear - 1)}
            aria-label="Ano anterior"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-sm font-medium">{viewYear}</span>
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7"
            onClick={() => setViewYear(viewYear + 1)}
            aria-label="Próximo ano"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
        <div className="grid grid-cols-3 gap-1">
          {MONTHS.map((label, index) => (
            <Button
              key={label}
              variant={viewYear === year && index + 1 === month ? 'default' : 'ghost'}
              size="sm"
              className="h-8 text-xs"
              onClick={() => pick(index)}
            >
              {label}
            </Button>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  );
};
