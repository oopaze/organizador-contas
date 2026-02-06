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
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from '@/app/components/ui/sheet';
import { Send, Bot, User, MessageSquarePlus, Loader2, MessageCircle, Menu } from 'lucide-react';
import { cn } from '@/app/components/ui/utils';
import { ProviderIcon } from '@/app/components/icons/provider-icons';

const AI_MODELS = {
  // Google Models
  'gemini-2.5-flash-lite': { name: 'Gemini 2.5 Flash Lite', provider: 'Google' },
  'gemini-2.5-pro': { name: 'Gemini 2.5 Pro', provider: 'Google' },
  'gemini-3-flash-preview': { name: 'Gemini 3 Flash Preview', provider: 'Google' },
  'gemini-3-pro-preview': { name: 'Gemini 3 Pro Preview', provider: 'Google' },
  // DeepSeek Models
  'deepseek-chat': { name: 'DeepSeek Chat', provider: 'DeepSeek' },
  'deepseek-reasoner': { name: 'DeepSeek Reasoner', provider: 'DeepSeek' },
  // OpenAI Models
  "gpt-5": { name: "GPT-5", provider: "OpenAI" },
  "gpt-5-mini": { name: "GPT-5 Mini", provider: "OpenAI" },
  "gpt-5-nano": { name: "GPT-5 Nano", provider: "OpenAI" },
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
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
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

  // Scroll conversations list to bottom on initial load only
  const hasScrolledConversations = useRef(false);
  const conversationsScrollRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!isLoadingConversations && conversations.length > 0 && !hasScrolledConversations.current) {
      // Use setTimeout to ensure DOM is fully rendered
      setTimeout(() => {
        const scrollContainer = conversationsScrollRef.current?.querySelector('[data-radix-scroll-area-viewport]');
        if (scrollContainer) {
          scrollContainer.scrollTop = scrollContainer.scrollHeight;
        }
      }, 0);
      hasScrolledConversations.current = true;
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
    setIsSidebarOpen(false);
  };

  const handleSelectConversation = (conv: ChatConversation) => {
    setActiveConversation(conv);
    setIsSidebarOpen(false);
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

  // Sidebar content - reused in desktop and mobile drawer
  const sidebarContent = (
    <>
      <div className="p-3 border-b">
        <Button onClick={createNewConversation} className="w-full" variant="outline">
          <MessageSquarePlus className="w-4 h-4 mr-2" />
          Nova Conversa
        </Button>
      </div>
      <ScrollArea ref={conversationsScrollRef} className="flex-1 min-h-0 p-2">
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
                    onClick={() => handleSelectConversation(conv)}
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
    </>
  );

  return (
    <div className="flex h-[calc(100vh-120px)] gap-2 -mt-3 overflow-hidden">
      {/* Mobile Sidebar Drawer */}
      <Sheet open={isSidebarOpen} onOpenChange={setIsSidebarOpen}>
        <SheetContent side="left" className="w-80 p-0 flex flex-col">
          <SheetHeader className="p-4 border-b">
            <SheetTitle>Conversas</SheetTitle>
          </SheetHeader>
          <div className="flex-1 flex flex-col overflow-hidden">
            {sidebarContent}
          </div>
        </SheetContent>
      </Sheet>

      {/* Desktop Sidebar */}
      <div className="w-80 flex-shrink-0 hidden md:block">
        <Card className="h-full flex flex-col overflow-hidden gap-0">
          {sidebarContent}
        </Card>
      </div>

      {/* Chat Area */}
      <Card className="flex-1 min-w-0 flex flex-col gap-0 overflow-hidden">
        {/* Header with model selector */}
        <div className="flex items-center justify-between gap-3 p-3 border-b">
          {/* Mobile: menu button + title */}
          <div className="flex items-center gap-3 min-w-0 md:hidden">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 flex-shrink-0"
              onClick={() => setIsSidebarOpen(true)}
            >
              <Menu className="w-4 h-4" />
            </Button>
            <span className="text-sm font-medium text-muted-foreground truncate">
              {activeConversation?.title || 'Nova conversa'}
            </span>
          </div>

          {/* Desktop: just a label */}
          <div className="hidden md:flex items-center gap-2">
            <Bot className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-medium text-muted-foreground">
              {activeConversation?.title || 'Nova conversa'}
            </span>
          </div>

          {/* Model selector - always visible */}
          <Select value={selectedModel} onValueChange={(value) => setSelectedModel(value as AIModelKey)}>
            <SelectTrigger className="w-auto h-8 gap-2 flex-shrink-0">
              <SelectValue placeholder="Modelo">
                <span className="flex items-center gap-2">
                  <ProviderIcon provider={AI_MODELS[selectedModel].provider} className="w-4 h-4" />
                  <span className="text-sm">{AI_MODELS[selectedModel].name}</span>
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
        </div>

        {/* Messages */}
        <ScrollArea className="flex-1 min-h-0 p-4">
          {isLoadingMessages ? (
            <div className="h-full flex flex-col items-center justify-center">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
              <p className="text-sm text-muted-foreground mt-3">Carregando mensagens...</p>
            </div>
          ) : messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-emerald-100 to-teal-100 dark:from-emerald-900/30 dark:to-teal-900/30 rounded-full flex items-center justify-center mb-4 shadow-lg">
                <span className="text-4xl">🐰</span>
              </div>
              <h2 className="text-2xl font-bold mb-1 bg-gradient-to-r from-emerald-500 to-teal-500 bg-clip-text text-transparent">
                Bunny Pix
              </h2>
              <p className="text-sm text-muted-foreground mb-1">Seu assistente financeiro fofo 💰</p>
              <p className="text-muted-foreground mb-6 max-w-md">
                Oi! Sou o Bunny Pix! 🥕 Posso te ajudar com suas finanças, gastos, receitas ou dar dicas de economia. Vamos conversar?
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-w-md w-full px-4 sm:px-0">
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
                      'max-w-[85%] sm:max-w-[70%] rounded-lg px-3 sm:px-4 py-2',
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
                          <div className="flex items-center gap-2 mt-2 pt-2 border-t border-border/50">
                            <span className="text-[10px] text-muted-foreground/50">
                              {msg.ai_call.model}
                            </span>
                            <span className="text-[10px] text-muted-foreground/70 font-medium">
                              {msg.ai_call.total_tokens.toLocaleString()} tokens
                            </span>
                            <span className="text-[10px] text-muted-foreground/50" title={`Input: ${msg.ai_call.input_used_tokens.toLocaleString()} tokens - Output: ${msg.ai_call.output_used_tokens.toLocaleString()} tokens`}>
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
        <div className="p-2 sm:p-4 border-t">
          <div className="flex gap-2 items-end">
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
              className="h-10 flex-shrink-0"
            >
              {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

