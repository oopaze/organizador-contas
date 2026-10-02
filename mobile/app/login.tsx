import { useState } from 'react';
import {
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Text,
  View,
} from 'react-native';
import { router } from 'expo-router';
import Wallet from 'lucide-react-native/icons/wallet';
import { Button } from '../src/components/ui/button';
import { Input } from '../src/components/ui/input';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../src/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../src/components/ui/tabs';
import { useAuth } from '../src/contexts/auth-context';

export default function LoginScreen() {
  const { login, register } = useAuth();
  const [tab, setTab] = useState('login');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  const [registerEmail, setRegisterEmail] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');

  const handleTabChange = (value: string) => {
    setTab(value);
    setError(null);
    setNotice(null);
  };

  const handleLogin = async () => {
    setError(null);
    setNotice(null);
    setIsLoading(true);
    try {
      await login(loginEmail, loginPassword);
      router.replace('/');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Falha ao entrar');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async () => {
    setError(null);
    setNotice(null);
    setIsLoading(true);
    try {
      await register({
        email: registerEmail,
        password: registerPassword,
        first_name: firstName,
        last_name: lastName,
      });
      setNotice('Conta criada com sucesso! Por favor, contate suporter para ativar sua conta.');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Falha ao cadastrar');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      className="flex-1 bg-zinc-50"
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView
        contentContainerClassName="flex-grow justify-center p-6"
        keyboardShouldPersistTaps="handled"
      >
        <View className="w-full max-w-md self-center">
          <View className="mb-6 items-center">
            <View className="mb-3 h-14 w-14 items-center justify-center rounded-full bg-emerald-600">
              <Wallet size={28} color="#ffffff" />
            </View>
            <Text className="text-2xl font-bold text-zinc-900">Poupix</Text>
            <Text className="mt-1 text-sm text-zinc-600">Controle suas despesas e receitas</Text>
          </View>

          <Tabs value={tab} onValueChange={handleTabChange}>
            <TabsList className="w-full">
              <TabsTrigger value="login">Entrar</TabsTrigger>
              <TabsTrigger value="register">Cadastrar</TabsTrigger>
            </TabsList>

            <TabsContent value="login">
              <Card>
                <CardHeader>
                  <CardTitle>Entrar</CardTitle>
                  <CardDescription>Digite suas credenciais para acessar sua conta</CardDescription>
                </CardHeader>
                <CardContent className="gap-4">
                  <Input
                    label="Email"
                    placeholder="usuario@exemplo.com"
                    keyboardType="email-address"
                    autoCapitalize="none"
                    autoComplete="email"
                    value={loginEmail}
                    onChangeText={setLoginEmail}
                  />
                  <Input
                    label="Senha"
                    placeholder="••••••••"
                    secureTextEntry
                    value={loginPassword}
                    onChangeText={setLoginPassword}
                  />
                  {error ? <Text className="text-sm text-red-600">{error}</Text> : null}
                  <Button className="mt-4" onPress={handleLogin} disabled={isLoading}>
                    {isLoading ? 'Entrando...' : 'Entrar'}
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="register">
              <Card>
                <CardHeader>
                  <CardTitle>Cadastrar</CardTitle>
                  <CardDescription>Crie uma nova conta para começar</CardDescription>
                </CardHeader>
                <CardContent className="gap-4">
                  <Input
                    label="Nome"
                    placeholder="João"
                    value={firstName}
                    onChangeText={setFirstName}
                  />
                  <Input
                    label="Sobrenome"
                    placeholder="Silva"
                    value={lastName}
                    onChangeText={setLastName}
                  />
                  <Input
                    label="Email"
                    placeholder="usuario@exemplo.com"
                    keyboardType="email-address"
                    autoCapitalize="none"
                    autoComplete="email"
                    value={registerEmail}
                    onChangeText={setRegisterEmail}
                  />
                  <Input
                    label="Senha"
                    placeholder="••••••••"
                    secureTextEntry
                    value={registerPassword}
                    onChangeText={setRegisterPassword}
                  />
                  {error ? <Text className="text-sm text-red-600">{error}</Text> : null}
                  {notice ? <Text className="text-sm text-emerald-700">{notice}</Text> : null}
                  <Button className="mt-4" onPress={handleRegister} disabled={isLoading}>
                    {isLoading ? 'Criando conta...' : 'Criar Conta'}
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}