import { useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  Text,
  View,
} from 'react-native';
import { Stack, router } from 'expo-router';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import ArrowLeft from 'lucide-react-native/icons/arrow-left';
import Bot from 'lucide-react-native/icons/bot';
import Menu from 'lucide-react-native/icons/menu';
import MessageCircle from 'lucide-react-native/icons/message-circle';
import MessageSquarePlus from 'lucide-react-native/icons/message-square-plus';
import Send from 'lucide-react-native/icons/send';
import { ChatMessage } from '../src/components/chat-message';
import { EmptyState } from '../src/components/empty-state';
import { InlineMessage } from '../src/components/inline-message';
import { Button } from '../src/components/ui/button';
import { Select } from '../src/components/ui/select';
import { Sheet } from '../src/components/ui/sheet';
import { Skeleton } from '../src/components/ui/skeleton';
import { Textarea } from '../src/components/ui/textarea';
import { cn } from '../src/components/ui/utils';
import { formatUploadError } from '../src/lib/transaction-form';
import {
  getConversationMessages,
  listConversations,
  sendMessageToConversation,
  startChat,
  type ChatConversation,
  type ChatMessage as ChatMessageData,
} from '../src/services';

/** Mesmos modelos do chat do PWA (`AI_MODELS` em `chat-page.tsx`). */
const CHAT_MODELS = {
  'gemini-2.5-flash-lite': { name: 'Gemini 2.5 Flash Lite', provider: 'Google' },
  'gemini-2.5-pro': { name: 'Gemini 2.5 Pro', provider: 'Google' },
  'gemini-3-flash-preview': { name: 'Gemini 3 Flash Preview', provider: 'Google' },
  'gemini-3-pro-preview': { name: 'Gemini 3 Pro Preview', provider: 'Google' },
  'deepseek-chat': { name: 'DeepSeek Chat', provider: 'DeepSeek' },
  'deepseek-reasoner': { name: 'DeepSeek Reasoner', provider: 'DeepSeek' },
  'gpt-5': { name: 'GPT-5', provider: 'OpenAI' },
  'gpt-5-mini': { name: 'GPT-5 Mini', provider: 'OpenAI' },
  'gpt-5-nano': { name: 'GPT-5 Nano', provider: 'OpenAI' },
} as const;

type ChatModelKey = keyof typeof CHAT_MODELS;

const DEFAULT_MODEL: ChatModelKey = 'deepseek-chat';

const MODEL_OPTIONS = Object.entries(CHAT_MODELS).map(([value, { name }]) => ({
  value,
  label: name,
}));

const SUGGESTED_QUESTIONS = [
  'Quanto gastei esse mês?',
  'Qual meu saldo atual?',
  'Quem são meus atores?',
  'Como posso economizar?',
];

function formatConversationDate(createdAt: string): string {
  return new Date(createdAt).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' });
}

function TypingBubble() {
  return (
    <View className="flex-row justify-start gap-2">
      <View className="h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-emerald-100">
        <Bot size={16} color="#059669" />
      </View>
      <View className="rounded-lg bg-zinc-100 px-4 py-2">
        <ActivityIndicator color="#059669" size="small" />
      </View>
    </View>
  );
}

export default function ChatScreen() {
  const insets = useSafeAreaInsets();
  const [conversations, setConversations] = useState<ChatConversation[]>([]);
  const [activeConversation, setActiveConversation] = useState<ChatConversation | null>(null);
  const [messages, setMessages] = useState<ChatMessageData[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [selectedModel, setSelectedModel] = useState<ChatModelKey>(DEFAULT_MODEL);
  const [isSending, setIsSending] = useState(false);
  const [isLoadingConversations, setIsLoadingConversations] = useState(true);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [conversationsError, setConversationsError] = useState<string | null>(null);
  const [messagesError, setMessagesError] = useState<string | null>(null);
  const [sendError, setSendError] = useState<string | null>(null);
  const scrollRef = useRef<ScrollView>(null);

  useEffect(() => {
    let cancelled = false;
    setConversationsError(null);

    listConversations()
      .then((data) => {
        if (cancelled) return;
        setConversations(
          [...data].sort(
            (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          )
        );
      })
      .catch((error) => {
        if (!cancelled) {
          setConversationsError(formatUploadError(error, 'Falha ao carregar as conversas'));
        }
      })
      .finally(() => {
        if (!cancelled) setIsLoadingConversations(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!activeConversation) {
      setMessages([]);
      setMessagesError(null);
      setIsLoadingMessages(false);
      return;
    }

    let cancelled = false;
    const conversationId = activeConversation.id;
    setMessages([]);
    setMessagesError(null);
    setIsLoadingMessages(true);

    getConversationMessages(conversationId)
      .then((data) => {
        if (!cancelled) setMessages(data);
      })
      .catch((error) => {
        if (!cancelled) {
          setMessagesError(formatUploadError(error, 'Falha ao carregar as mensagens'));
        }
      })
      .finally(() => {
        if (!cancelled) setIsLoadingMessages(false);
      });

    return () => {
      cancelled = true;
    };
  }, [activeConversation?.id]);

  const createNewConversation = () => {
    setActiveConversation(null);
    setMessages([]);
    setSendError(null);
    setSidebarOpen(false);
  };

  const handleSelectConversation = (conversation: ChatConversation) => {
    setActiveConversation(conversation);
    setSendError(null);
    setSidebarOpen(false);
  };

  const handleSendMessage = async (message?: string) => {
    const messageToSend = (message ?? inputMessage).trim();
    if (!messageToSend || isSending) return;

    setInputMessage('');
    setSendError(null);
    setIsSending(true);

    try {
      if (!activeConversation) {
        const response = await startChat(messageToSend, selectedModel);
        setConversations((prev) => [response.conversation, ...prev]);
        setActiveConversation(response.conversation);
        setMessages([response.user_message, response.ai_message]);
      } else {
        // Envio otimista: a bolha do usuário aparece antes da resposta (como no web).
        const tempUserMessage: ChatMessageData = {
          id: Date.now(),
          role: 'human',
          content: messageToSend,
          ai_call: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, tempUserMessage]);

        const response = await sendMessageToConversation(
          activeConversation.id,
          messageToSend,
          selectedModel
        );
        setMessages((prev) => [
          ...prev.filter((m) => m.id !== tempUserMessage.id),
          response.user_message,
          response.ai_message,
        ]);
      }
    } catch (error) {
      setSendError(formatUploadError(error, 'Falha ao enviar a mensagem'));
    } finally {
      setIsSending(false);
    }
  };

  const handleBack = () => {
    if (router.canGoBack()) {
      router.back();
    } else {
      router.replace('/more');
    }
  };

  const selectedModelInfo = CHAT_MODELS[selectedModel];

  return (
    <KeyboardAvoidingView
      className="flex-1 bg-zinc-50"
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      style={{ paddingTop: insets.top, paddingBottom: insets.bottom }}
    >
      <Stack.Screen options={{ headerShown: false }} />

      <View className="flex-row items-center gap-1 border-b border-zinc-200 bg-white px-2 py-2">
        <Pressable
          accessibilityRole="button"
          accessibilityLabel="Voltar"
          onPress={handleBack}
          className="h-11 w-11 items-center justify-center rounded-md active:bg-zinc-100"
        >
          <ArrowLeft size={18} color="#3f3f46" />
        </Pressable>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel="Conversas"
          onPress={() => setSidebarOpen(true)}
          className="h-11 w-11 items-center justify-center rounded-md active:bg-zinc-100"
        >
          <Menu size={18} color="#3f3f46" />
        </Pressable>
        <Text numberOfLines={1} className="min-w-0 flex-1 text-sm font-medium text-zinc-600">
          {activeConversation?.title || 'Nova conversa'}
        </Text>
        <View className="flex-row items-center gap-2">
          <Text className="text-[10px] uppercase tracking-wide text-zinc-400">
            {selectedModelInfo.provider}
          </Text>
          <Select
            value={selectedModel}
            onValueChange={(value) => setSelectedModel(value as ChatModelKey)}
            options={MODEL_OPTIONS}
            className="h-9 w-auto"
          />
        </View>
      </View>

      <ScrollView
        ref={scrollRef}
        className="flex-1"
        contentContainerClassName="gap-3 p-4"
        keyboardShouldPersistTaps="handled"
        onContentSizeChange={() => scrollRef.current?.scrollToEnd({ animated: true })}
      >
        {isLoadingMessages ? (
          <View className="items-center gap-3 py-12">
            <ActivityIndicator color="#059669" />
            <Text className="text-sm text-zinc-500">Carregando mensagens...</Text>
          </View>
        ) : messagesError ? (
          <InlineMessage>{messagesError}</InlineMessage>
        ) : messages.length === 0 ? (
          <View className="items-center gap-2 px-4 py-8">
            <Text className="text-4xl">🐰</Text>
            <Text className="text-2xl font-bold text-emerald-600">Bunny Pix</Text>
            <Text className="text-sm text-zinc-500">Seu assistente financeiro fofo 💰</Text>
            <Text className="mt-1 text-center text-zinc-600">
              Oi! Sou o Bunny Pix! 🥕 Posso te ajudar com suas finanças, gastos, receitas ou dar
              dicas de economia. Vamos conversar?
            </Text>
            <View className="mt-2 w-full gap-2">
              {SUGGESTED_QUESTIONS.map((question) => (
                <Button
                  key={question}
                  variant="outline"
                  className="h-auto py-2"
                  disabled={isSending}
                  onPress={() => void handleSendMessage(question)}
                >
                  <Text className="text-sm text-zinc-900">{question}</Text>
                </Button>
              ))}
            </View>
          </View>
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                role={message.role === 'human' ? 'user' : 'assistant'}
                content={message.content}
                aiCall={message.ai_call}
              />
            ))}
            {isSending ? <TypingBubble /> : null}
          </>
        )}
      </ScrollView>

      <View className="border-t border-zinc-200 bg-white p-3">
        {sendError ? (
          <View className="mb-2">
            <InlineMessage>{sendError}</InlineMessage>
          </View>
        ) : null}
        <View className="flex-row items-end gap-2">
          <Textarea
            value={inputMessage}
            onChangeText={setInputMessage}
            placeholder="Digite sua pergunta..."
            editable={!isSending}
            accessibilityLabel="Mensagem"
            className="max-h-24 min-h-11 flex-1"
          />
          <Button
            size="icon"
            disabled={isSending || !inputMessage.trim()}
            onPress={() => void handleSendMessage()}
            accessibilityLabel="Enviar mensagem"
          >
            {isSending ? (
              <ActivityIndicator color="#ffffff" size="small" />
            ) : (
              <Send size={18} color="#ffffff" />
            )}
          </Button>
        </View>
      </View>

      <Sheet
        visible={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        title="Conversas"
        scrollable
      >
        <View className="gap-3 px-4 pb-2">
          <Button variant="outline" onPress={createNewConversation}>
            <MessageSquarePlus size={16} color="#3f3f46" />
            <Text className="text-sm font-medium text-zinc-900">Nova Conversa</Text>
          </Button>
        </View>

        {isLoadingConversations ? (
          <View className="gap-2 px-4 py-2">
            <Skeleton className="h-14 w-full" />
            <Skeleton className="h-14 w-full" />
          </View>
        ) : conversationsError ? (
          <View className="px-4">
            <InlineMessage>{conversationsError}</InlineMessage>
          </View>
        ) : conversations.length === 0 ? (
          <EmptyState title="Nenhuma conversa ainda" description="Comece uma nova conversa!" />
        ) : (
          <View className="px-2">
            {conversations.map((conversation) => {
              const isActive = activeConversation?.id === conversation.id;

              return (
                <Pressable
                  key={conversation.id}
                  accessibilityRole="button"
                  onPress={() => handleSelectConversation(conversation)}
                  className={cn(
                    'flex-row items-start gap-2 rounded-lg px-3 py-2.5 active:bg-zinc-100',
                    isActive && 'bg-emerald-600'
                  )}
                >
                  <MessageCircle size={16} color={isActive ? '#ffffff' : '#71717a'} />
                  <View className="min-w-0 flex-1">
                    <Text
                      numberOfLines={2}
                      className={cn(
                        'text-sm font-medium',
                        isActive ? 'text-white' : 'text-zinc-900'
                      )}
                    >
                      {conversation.title}
                    </Text>
                    <Text
                      className={cn('mt-0.5 text-xs', isActive ? 'text-emerald-100' : 'text-zinc-500')}
                    >
                      {formatConversationDate(conversation.created_at)}
                    </Text>
                  </View>
                </Pressable>
              );
            })}
          </View>
        )}
      </Sheet>
    </KeyboardAvoidingView>
  );
}
