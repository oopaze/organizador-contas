import React, { useState } from 'react';
import { useUser } from '@/contexts/user-context';
import { updateProfile } from '@/services';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Label } from '@/app/components/ui/label';
import { Switch } from '@/app/components/ui/switch';
import { toast } from 'sonner';

export const SettingsPage: React.FC = () => {
  const { user, refetchUser } = useUser();
  const [saving, setSaving] = useState(false);
  const modoOn = user?.profile?.modo_on === true;

  const handleToggle = async (checked: boolean) => {
    setSaving(true);
    try {
      await updateProfile({ modo_on: checked });
      await refetchUser();
      toast.success(
        checked ? 'Modo lançamento rápido ativado!' : 'Modo lançamento rápido desativado.'
      );
    } catch {
      toast.error('Falha ao salvar a configuração');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Configurações</h1>

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
            <Switch id="modo-on" checked={modoOn} disabled={saving} onCheckedChange={handleToggle} />
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
