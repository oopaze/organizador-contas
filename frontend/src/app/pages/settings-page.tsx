import React, { useEffect, useState } from 'react';
import { useUser } from '@/contexts/user-context';
import { updateProfile } from '@/services';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { Switch } from '@/app/components/ui/switch';
import { toast } from 'sonner';

export const SettingsPage: React.FC = () => {
  const { user, refetchUser } = useUser();
  const [savingMode, setSavingMode] = useState(false);
  const [savingSalary, setSavingSalary] = useState(false);
  const [salary, setSalary] = useState('');
  const [salaryDay, setSalaryDay] = useState('1');
  const modoOn = user?.profile?.modo_on === true;

  useEffect(() => {
    if (!user?.profile) return;
    setSalary(user.profile.salary ? String(user.profile.salary) : '');
    setSalaryDay(String(user.profile.salary_day ?? 1));
  }, [user?.profile?.salary, user?.profile?.salary_day]);

  const handleToggle = async (checked: boolean) => {
    setSavingMode(true);
    try {
      await updateProfile({ modo_on: checked });
      await refetchUser();
      toast.success(
        checked ? 'Modo lançamento rápido ativado!' : 'Modo lançamento rápido desativado.'
      );
    } catch {
      toast.error('Falha ao salvar a configuração');
    } finally {
      setSavingMode(false);
    }
  };

  const handleSaveSalary = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingSalary(true);
    try {
      const data: { salary?: number; salary_day?: number } = {
        salary_day: Math.min(31, Math.max(1, parseInt(salaryDay, 10) || 1)),
      };
      if (salary !== '') {
        data.salary = parseFloat(salary);
      }
      await updateProfile(data);
      await refetchUser();
      toast.success('Salário atualizado!');
    } catch {
      toast.error('Falha ao salvar o salário');
    } finally {
      setSavingSalary(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Configurações</h1>

      <Card>
        <CardHeader>
          <CardTitle>Salário</CardTitle>
          <CardDescription>
            O valor entra todo mês como receita garantida: meses passados e o atual como
            recebido, meses futuros como previsto.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSaveSalary} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="salary">Salário mensal</Label>
                <Input
                  id="salary"
                  type="number"
                  step="0.01"
                  inputMode="decimal"
                  placeholder="Ex: 5000"
                  value={salary}
                  onChange={(e) => setSalary(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="salary-day">Dia do recebimento</Label>
                <Input
                  id="salary-day"
                  type="number"
                  min="1"
                  max="31"
                  inputMode="numeric"
                  value={salaryDay}
                  onChange={(e) => setSalaryDay(e.target.value)}
                />
              </div>
            </div>
            <div className="flex justify-end">
              <Button type="submit" disabled={savingSalary}>
                {savingSalary ? 'Salvando...' : 'Salvar salário'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Modo lançamento rápido</CardTitle>
          <CardDescription>
            Lance no momento da transação, com extrato de saldo corrente e conciliação da fatura por IA.
            Desligado, o app mantém o fluxo de subir a fatura em lote.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between gap-4">
            <Label htmlFor="modo-on" className="cursor-pointer">
              Ativar modo lançamento rápido
            </Label>
            <Switch id="modo-on" checked={modoOn} disabled={savingMode} onCheckedChange={handleToggle} />
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
