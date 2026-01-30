import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  ChatMessage,
  ChatConversation,
  startChat,
  listConversations,
  getConversationMessages,
  sendMessageToConversation,
} from '@/services';
import { Button } from '@/app/components/ui/button';
import { Card } from '@/app/components/ui/card';
import { Textarea } from '@/app/components/ui/textarea';
import { ScrollArea } from '@/app/components/ui/scroll-area';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/app/components/ui/select';
import { Send, Bot, User, MessageSquarePlus, Loader2, MessageCircle } from 'lucide-react';
import { cn } from '@/app/components/ui/utils';

// Provider Icons
const GoogleIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none">
    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
  </svg>
);

// DeepSeek official logo - whale symbol in brand blue (#4d6bfe)
const DeepSeekIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 56 42" fill="none">
    <path fill="#4d6bfe" d="M55.6128,3.4712c-.5953-.2917-.8517.2642-1.1998.5466-.1191.0911-.2198.2095-.3206.3188-.8701.9292-1.8867,1.5398-3.2148,1.4668-1.9417-.1094-3.5995.5012-5.065,1.9863-.3114-1.8313-1.3463-2.9248-2.9217-3.6262-.8242-.3645-1.6577-.729-2.2348-1.5217-.403-.5647-.5129-1.1934-.7144-1.813-.1283-.3735-.2565-.7563-.687-.8201-.4671-.0728-.6503.3188-.8335.647-.7327,1.3394-1.0166,2.8154-.9892,4.3096.0641,3.3621,1.4838,6.0406,4.3047,7.9449.3206.2187.403.4372.3023.7563-.1924.656-.4214,1.2937-.6228,1.9497-.1283.4192-.3207.5103-.7694.3279-1.5479-.6467-2.8852-1.6035-4.0667-2.7605-2.0058-1.9407-3.8193-4.0818-6.0815-5.7583-.5312-.3918-1.0625-.7561-1.6121-1.1025-2.3081-2.2412.3023-4.0818.9068-4.3003.6319-.2278.2198-1.0115-1.8227-1.0022-2.0425.009-3.9109.6924-6.2922,1.6035-.348.1367-.7145.2368-1.09.3188-2.1615-.4099-4.4055-.5012-6.7502-.2368-4.4147.4919-7.9408,2.5784-10.5328,6.1409C.1914,13.1289-.5413,17.9941.3563,23.0691c.9434,5.3481,3.6727,9.7761,7.8676,13.2385,4.3506,3.5896,9.3606,5.3481,15.0758,5.011,3.4713-.2004,7.3364-.665,11.6961-4.355,1.099.5467,2.2531.7652,4.1674.9292,1.4746.1367,2.8943-.0728,3.9933-.3005,1.7219-.3645,1.6029-1.959.9801-2.2505-5.0466-2.3506-3.9385-1.394-4.9459-2.1685,2.5645-3.0339,6.4297-6.1865,7.9409-16.4001.119-.8108.0183-1.3211,0-1.9771-.0092-.4008.0824-.5556.5404-.6013,1.2639-.1458,2.4912-.4919,3.6178-1.1115,3.2698-1.7857,4.5886-4.7195,4.9-8.2364.0459-.5376-.0091-1.0935-.577-1.3757ZM27.119,35.123c-4.8909-3.8447-7.263-5.1113-8.2431-5.0566-.9159.0547-.751,1.1025-.5496,1.7859.2107.6741.4855,1.1389.8701,1.731.2656.3918.4489.9748-.2655,1.4123-1.5754.9749-4.314-.3281-4.4423-.3918-3.1872-1.877-5.8525-4.3553-7.7302-7.7444-1.8135-3.262-2.8667-6.7605-3.0408-10.4961-.0458-.9019.2198-1.221,1.1174-1.3848,1.1815-.2187,2.3997-.2644,3.5812-.0913,4.9918.729,9.2415,2.9612,12.8043,6.4963,2.0333,2.0135,3.572,4.419,5.1566,6.7696,1.6852,2.4963,3.4987,4.8745,5.8068,6.8242.8151.6833,1.4654,1.2026,2.0882,1.5854-1.8775.2095-5.01.2552-7.1532-1.4397ZM29.4637,20.0442c0-.4009.3206-.7197.7237-.7197.0916,0,.174.018.2473.0453.1008.0366.1924.0913.2656.1731.1283.1277.2015.3098.2015.5012,0,.4009-.3205.7197-.7234.7197s-.7145-.3188-.7145-.7197ZM36.7452,23.7798c-.4671.1914-.9342.3552-1.383.3735-.6961.0364-1.4563-.2461-1.8684-.5923-.6411-.5376-1.0991-.8381-1.2914-1.7766-.0825-.4009-.0367-1.0205.0367-1.3757.1648-.7654-.0184-1.2573-.5587-1.7039-.4397-.3645-.9984-.4646-1.6121-.4646-.229,0-.4395-.1003-.5953-.1823-.2565-.1275-.467-.4464-.2656-.8382.0641-.1274.3756-.4373.4489-.4919.8335-.4739,1.7952-.3189,2.6836.0364.8244.3371,1.4472.9567,2.3447,1.8313.9159,1.0568,1.0807,1.3486,1.6028,2.1411.4123.6196.7878,1.2573,1.0442,1.9863.1557.4556-.0458.8291-.5862,1.0569Z"/>
  </svg>
);

const ProviderIcon = ({ provider, className }: { provider: string; className?: string }) => {
  switch (provider) {
    case 'Google':
      return <GoogleIcon className={className} />;
    case 'DeepSeek':
      return <DeepSeekIcon className={className} />;
    default:
      return null;
  }
};

const AI_MODELS = {
  // DeepSeek Models
  'deepseek-chat': { name: 'DeepSeek Chat', provider: 'DeepSeek' },
  'deepseek-reasoner': { name: 'DeepSeek Reasoner', provider: 'DeepSeek' },
  'deepseek-v3.2': { name: 'DeepSeek v3.2', provider: 'DeepSeek' },
  // Google Models
  'gemini-2.5-flash-lite': { name: 'Gemini 2.5 Flash Lite', provider: 'Google' },
  'gemini-2.5-pro': { name: 'Gemini 2.5 Pro', provider: 'Google' },
  'gemini-3-flash-preview': { name: 'Gemini 3 Flash Preview', provider: 'Google' },
  'gemini-3-pro-preview': { name: 'Gemini 3 Pro Preview', provider: 'Google' },
} as const;

type AIModelKey = keyof typeof AI_MODELS;

const DEFAULT_MODEL: AIModelKey = 'gemini-2.5-flash-lite';

const suggestedQuestions = [
  'Quanto gastei esse mês?',
  'Qual meu saldo atual?',
  'Quem são meus atores?',
  'Como posso economizar?',
];

export const ChatPage: React.FC = () => {
  const [conversations, setConversations] = useState<ChatConversation[]>([]);
  const [activeConversation, setActiveConversation] = useState<ChatConversation | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [selectedModel, setSelectedModel] = useState<AIModelKey>(DEFAULT_MODEL);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingConversations, setIsLoadingConversations] = useState(true);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const conversationsEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const lineHeight = 24;
      const maxHeight = lineHeight * 4;
      textarea.style.height = `${Math.min(textarea.scrollHeight, maxHeight)}px`;
    }
  };

  // Load conversations on mount
  useEffect(() => {
    const loadConversations = async () => {
      try {
        const data = await listConversations();
        // Sort by created_at descending (newest first)
        const sorted = [...data].sort((a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
        setConversations(sorted);
      } catch (error) {
        console.error('Error loading conversations:', error);
      } finally {
        setIsLoadingConversations(false);
      }
    };
    loadConversations();
  }, []);

  // Scroll conversations list to bottom on load
  useEffect(() => {
    if (!isLoadingConversations && conversations.length > 0) {
      conversationsEndRef.current?.scrollIntoView({ behavior: 'auto' });
    }
  }, [isLoadingConversations, conversations.length]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load messages when active conversation changes
  useEffect(() => {
    const loadMessages = async () => {
      if (!activeConversation) {
        setMessages([]);
        setIsLoadingMessages(false);
        return;
      }
      // Clear messages and show loading state immediately
      setMessages([]);
      setIsLoadingMessages(true);
      try {
        const data = await getConversationMessages(activeConversation.id);
        setMessages(data);
      } catch (error) {
        console.error('Error loading messages:', error);
      } finally {
        setIsLoadingMessages(false);
      }
    };
    loadMessages();
  }, [activeConversation?.id]);

  const createNewConversation = () => {
    setActiveConversation(null);
    setMessages([]);
  };

  const handleSendMessage = async (message?: string) => {
    const messageToSend = message || inputMessage.trim();
    if (!messageToSend || isLoading) return;

    setInputMessage('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
    setIsLoading(true);

    try {
      if (!activeConversation) {
        // Start a new conversation
        const response = await startChat(messageToSend, selectedModel);
        const newConversation = {
          ...response.conversation,
          title: response.conversation.title,
        };
        setConversations(prev => [newConversation, ...prev]);
        setActiveConversation(newConversation);
        setMessages([response.user_message, response.ai_message]);
      } else {
        // Send message to existing conversation
        // Optimistically add user message
        const tempUserMessage: ChatMessage = {
          id: Date.now(),
          role: 'human',
          content: messageToSend,
          ai_call: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
        setMessages(prev => [...prev, tempUserMessage]);

        const response = await sendMessageToConversation(activeConversation.id, messageToSend, selectedModel);
        // Replace temp message with real ones
        setMessages(prev => [
          ...prev.filter(m => m.id !== tempUserMessage.id),
          response.user_message,
          response.ai_message,
        ]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputMessage(e.target.value);
    adjustTextareaHeight();
  };

  return (
    <div className="flex h-[calc(100vh-120px)] gap-2 -mt-3">
      {/* Sidebar */}
      <div className="w-80 flex-shrink-0">
        <Card className="h-full flex flex-col overflow-hidden gap-0">
          <div className="p-3 border-b">
            <Button onClick={createNewConversation} className="w-full" variant="outline">
              <MessageSquarePlus className="w-4 h-4 mr-2" />
              Nova Conversa
            </Button>
          </div>
          <ScrollArea className="flex-1 min-h-0 p-2">
            {isLoadingConversations ? (
              <div className="flex justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
              </div>
            ) : conversations.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 px-4">
                <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center mb-3">
                  <MessageCircle className="w-6 h-6 text-muted-foreground" />
                </div>
                <p className="text-sm text-muted-foreground text-center">
                  Nenhuma conversa ainda
                </p>
                <p className="text-xs text-muted-foreground/70 text-center mt-1">
                  Comece uma nova conversa!
                </p>
              </div>
            ) : (
              <div className="flex flex-col-reverse">
                <div ref={conversationsEndRef} />
                {[...conversations].reverse().map((conv, index, arr) => {
                  const isActive = activeConversation?.id === conv.id;
                  const date = new Date(conv.created_at);
                  const formattedDate = date.toLocaleDateString('pt-BR', {
                    day: '2-digit',
                    month: 'short',
                  });
                  const isLast = index === arr.length - 1;

                  return (
                    <div key={conv.id}>
                      {!isLast && (
                        <div className="mx-3 my-1 border-t border-border/50" />
                      )}
                      <button
                        onClick={() => setActiveConversation(conv)}
                        className={cn(
                          'w-full text-left px-3 py-2.5 rounded-lg transition-all duration-200 group',
                          isActive
                            ? 'bg-primary text-primary-foreground shadow-sm'
                            : 'hover:bg-muted/80'
                        )}
                      >
                        <div className="flex items-start gap-2">
                          <MessageCircle className={cn(
                            'w-4 h-4 mt-0.5 flex-shrink-0 mr-1',
                            isActive ? 'text-primary-foreground' : 'text-muted-foreground'
                          )} />
                          <div className="flex-1 min-w-0">
                            <p className="text-[0.8rem] font-medium line-clamp-2" title={conv.title}>
                              {conv.title}
                            </p>
                            <p className={cn(
                              'text-[0.7rem] mt-0.5',
                              isActive ? 'text-primary-foreground/70' : 'text-muted-foreground'
                            )}>
                              {formattedDate}
                            </p>
                          </div>
                        </div>
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </ScrollArea>
        </Card>
      </div>

      {/* Chat Area */}
      <Card className="flex-1 flex flex-col gap-0 overflow-hidden">
        {/* Messages */}
        <ScrollArea className="flex-1 min-h-0 p-4">
          {isLoadingMessages ? (
            <div className="h-full flex flex-col items-center justify-center">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
              <p className="text-sm text-muted-foreground mt-3">Carregando mensagens...</p>
            </div>
          ) : messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-pink-100 to-purple-100 dark:from-pink-900/30 dark:to-purple-900/30 rounded-full flex items-center justify-center mb-4 shadow-lg">
                <span className="text-4xl">🐰</span>
              </div>
              <h2 className="text-2xl font-bold mb-1 bg-gradient-to-r from-pink-500 to-purple-500 bg-clip-text text-transparent">
                Bunny Money
              </h2>
              <p className="text-sm text-muted-foreground mb-1">Seu assistente financeiro fofo 💰</p>
              <p className="text-muted-foreground mb-6 max-w-md">
                Oi! Sou o Bunny Money! 🥕 Posso te ajudar com suas finanças, gastos, receitas ou dar dicas de economia. Vamos conversar?
              </p>
              <div className="grid grid-cols-2 gap-2 max-w-md">
                {suggestedQuestions.map((question, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    className="text-sm h-auto py-2 px-3"
                    onClick={() => handleSendMessage(question)}
                  >
                    {question}
                  </Button>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex flex-col-reverse gap-3">
              <div ref={messagesEndRef} />
              {isLoading && (
                <div className="flex gap-3 justify-start mb-4">
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <Bot className="w-4 h-4 text-primary" />
                  </div>
                  <div className="bg-muted rounded-lg px-4 py-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                  </div>
                </div>
              )}
              {[...messages].reverse().map((msg, index) => (
                <div
                  key={msg.id}
                  className={cn(
                    'flex gap-3',
                    msg.role === 'human' ? 'justify-end' : 'justify-start',
                    index !== messages.length - 1 && 'mb-4'
                  )}
                >
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <Bot className="w-4 h-4 text-primary" />
                    </div>
                  )}
                  <div
                    className={cn(
                      'max-w-[70%] rounded-lg px-4 py-2',
                      msg.role === 'human'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted'
                    )}
                  >
                    {msg.role === 'assistant' ? (
                      <>
                        <div className={cn(
                          "text-sm prose prose-sm dark:prose-invert max-w-none",
                          // Paragraphs
                          "prose-p:my-2 prose-p:leading-relaxed",
                          // Lists
                          "prose-ul:my-2 prose-ul:list-disc prose-ul:pl-5 prose-ul:space-y-1",
                          "prose-ol:my-2 prose-ol:list-decimal prose-ol:pl-5 prose-ol:space-y-1",
                          "prose-li:my-0.5 prose-li:pl-1",
                          // Headings
                          "prose-headings:font-semibold prose-headings:my-2 prose-headings:mt-4",
                          "prose-h1:text-lg prose-h2:text-base prose-h3:text-sm",
                          // Code
                          "prose-pre:my-2 prose-pre:bg-muted prose-pre:p-3 prose-pre:rounded-md prose-pre:overflow-x-auto",
                          "prose-code:bg-muted prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-xs prose-code:before:content-none prose-code:after:content-none",
                          // Links
                          "prose-a:text-primary prose-a:underline prose-a:underline-offset-2 hover:prose-a:text-primary/80",
                          // Blockquotes
                          "prose-blockquote:border-l-4 prose-blockquote:border-primary/30 prose-blockquote:pl-4 prose-blockquote:italic prose-blockquote:my-2",
                          // Tables
                          "prose-table:my-2 prose-table:w-full prose-table:text-xs",
                          "prose-th:border prose-th:border-border prose-th:px-2 prose-th:py-1 prose-th:bg-muted prose-th:font-semibold prose-th:text-left",
                          "prose-td:border prose-td:border-border prose-td:px-2 prose-td:py-1",
                          // Horizontal rule
                          "prose-hr:my-4 prose-hr:border-border",
                          // Strong & Emphasis
                          "prose-strong:font-semibold prose-em:italic"
                        )}>
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                          >
                            {msg.content.replace(/\\n/g, '\n')}
                          </ReactMarkdown>
                        </div>
                        {msg.ai_call && (
                          <div className="flex items-center gap-1 mt-2 pt-2 border-t border-border/50">
                            <span className="text-[10px] text-muted-foreground/70 font-medium">
                              {msg.ai_call.total_tokens.toLocaleString()} tokens
                            </span>
                            <span className="text-[10px] text-muted-foreground/50">
                              ({msg.ai_call.input_used_tokens.toLocaleString()}↓ {msg.ai_call.output_used_tokens.toLocaleString()}↑)
                            </span>
                          </div>
                        )}
                      </>
                    ) : (
                      <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                    )}
                  </div>
                  {msg.role === 'human' && (
                    <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                      <User className="w-4 h-4 text-primary-foreground" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </ScrollArea>

        {/* Input */}
        <div className="p-4 border-t">
          <div className="flex gap-2 items-end">
            <Select value={selectedModel} onValueChange={(value) => setSelectedModel(value as AIModelKey)}>
              <SelectTrigger className="w-[220px] h-10">
                <SelectValue placeholder="Selecione o modelo">
                  <span className="flex items-center gap-2">
                    <ProviderIcon provider={AI_MODELS[selectedModel].provider} className="w-4 h-4" />
                    <span className="truncate">{AI_MODELS[selectedModel].name}</span>
                  </span>
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                {Object.entries(AI_MODELS).map(([key, { name, provider }]) => (
                  <SelectItem key={key} value={key}>
                    <span className="flex items-center gap-2">
                      <ProviderIcon provider={provider} className="w-4 h-4" />
                      <span>{name}</span>
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Textarea
              ref={textareaRef}
              value={inputMessage}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Digite sua pergunta..."
              disabled={isLoading}
              className="flex-1 min-h-[40px] max-h-[96px] resize-none"
              rows={1}
            />
            <Button
              onClick={() => handleSendMessage()}
              disabled={isLoading || !inputMessage.trim()}
              className="h-10"
            >
              {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

