import React from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/app/components/ui/table';
import { Button } from '@/app/components/ui/button';
import { LoanPayment, deleteLoanPayment } from '@/services';
import { Trash2, FileText } from 'lucide-react';
import { toast } from 'sonner';

interface Props {
  payments: LoanPayment[];
  onChange: () => void;
}

export const LoanPaymentsTable: React.FC<Props> = ({ payments, onChange }) => {
  const handleDelete = async (id: number) => {
    if (!confirm('Remover este pagamento?')) return;
    try {
      await deleteLoanPayment(id);
      toast.success('Pagamento removido');
      onChange();
    } catch {
      toast.error('Falha ao remover');
    }
  };

  if (payments.length === 0) {
    return <p className="text-sm text-gray-500 py-2">Nenhum pagamento ainda.</p>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Data</TableHead>
          <TableHead>Valor</TableHead>
          <TableHead>Nota</TableHead>
          <TableHead>Comprovante</TableHead>
          <TableHead></TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {payments.map((p) => (
          <TableRow key={p.id}>
            <TableCell>{p.paid_at}</TableCell>
            <TableCell>R$ {p.amount}</TableCell>
            <TableCell>{p.note || '—'}</TableCell>
            <TableCell>
              {p.file_id ? (
                <FileText className="w-4 h-4 text-indigo-600" />
              ) : '—'}
            </TableCell>
            <TableCell>
              <Button variant="ghost" size="sm" onClick={() => handleDelete(p.id)}>
                <Trash2 className="w-4 h-4" />
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};
