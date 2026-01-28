import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage, sendChatMessage } from '@/services';
import { Button } from '@/app/components/ui/button';
import { Card } from '@/app/components/ui/card';
import { Textarea } from '@/app/components/ui/textarea';
import { ScrollArea } from '@/app/components/ui/scroll-area';
import { Send, Bot, User, MessageSquarePlus, Loader2, Sparkles } from 'lucide-react';
import { cn } from '@/app/components/ui/utils';

interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
}

const suggestedQuestions = [
  'Quanto gastei esse mês?',
  'Qual meu saldo atual?',
  'Quem são meus atores?',
  'Como posso economizar?',
];

export const ChatPage: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversation, setActiveConversation] = useState<Conversation | null>(null);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const lineHeight = 24; // approximate line height in pixels
      const maxHeight = lineHeight * 4; // 4 lines max
      textarea.style.height = `${Math.min(textarea.scrollHeight, maxHeight)}px`;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [activeConversation?.messages]);

  const createNewConversation = () => {
    const newConversation: Conversation = {
      id: crypto.randomUUID(),
      title: 'Nova conversa',
      messages: [],
    };
    setConversations(prev => [newConversation, ...prev]);
    setActiveConversation(newConversation);
  };

  const handleSendMessage = async (message?: string) => {
    const messageToSend = message || inputMessage.trim();
    if (!messageToSend || isLoading) return;

    let conversation = activeConversation;
    if (!conversation) {
      conversation = {
        id: crypto.randomUUID(),
        title: messageToSend.slice(0, 30) + (messageToSend.length > 30 ? '...' : ''),
        messages: [],
      };
      setConversations(prev => [conversation!, ...prev]);
    }

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: messageToSend,
      timestamp: new Date(),
    };

    const updatedConversation = {
      ...conversation,
      messages: [...conversation.messages, userMessage],
    };
    setActiveConversation(updatedConversation);
    setConversations(prev =>
      prev.map(c => (c.id === updatedConversation.id ? updatedConversation : c))
    );
    setInputMessage('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
    setIsLoading(true);

    try {
      const aiResponse = await sendChatMessage(messageToSend);
      const finalConversation = {
        ...updatedConversation,
        messages: [...updatedConversation.messages, aiResponse],
      };
      setActiveConversation(finalConversation);
      setConversations(prev =>
        prev.map(c => (c.id === finalConversation.id ? finalConversation : c))
      );
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
    <div className="flex h-[calc(100vh-120px)] gap-4 -mt-4">
      {/* Sidebar */}
      <div className="w-64 flex-shrink-0">
        <Card className="h-full flex flex-col">
          <div className="p-3 border-b">
            <Button onClick={createNewConversation} className="w-full" variant="outline">
              <MessageSquarePlus className="w-4 h-4 mr-2" />
              Nova Conversa
            </Button>
          </div>
          <ScrollArea className="flex-1 p-2">
            {conversations.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">
                Nenhuma conversa ainda
              </p>
            ) : (
              <div className="space-y-1">
                {conversations.map(conv => (
                  <button
                    key={conv.id}
                    onClick={() => setActiveConversation(conv)}
                    className={cn(
                      'w-full text-left px-3 py-2 rounded-md text-sm truncate transition-colors',
                      activeConversation?.id === conv.id
                        ? 'bg-primary text-primary-foreground'
                        : 'hover:bg-muted'
                    )}
                  >
                    {conv.title}
                  </button>
                ))}
              </div>
            )}
          </ScrollArea>
        </Card>
      </div>

      {/* Chat Area */}
      <Card className="flex-1 flex flex-col">
        {/* Messages */}
        <ScrollArea className="flex-1 p-4">
          {!activeConversation || activeConversation.messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                <Sparkles className="w-8 h-8 text-primary" />
              </div>
              <h2 className="text-xl font-semibold mb-2">Assistente Financeiro</h2>
              <p className="text-muted-foreground mb-6 max-w-md">
                Pergunte sobre suas finanças, gastos, receitas ou peça dicas de economia.
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
            // Messages will be added in the next edit
            <div className="space-y-4">
              {activeConversation.messages.map(msg => (
                <div
                  key={msg.id}
                  className={cn(
                    'flex gap-3',
                    msg.role === 'user' ? 'justify-end' : 'justify-start'
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
                      msg.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted'
                    )}
                  >
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  </div>
                  {msg.role === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                      <User className="w-4 h-4 text-primary-foreground" />
                    </div>
                  )}
                </div>
              ))}
              {isLoading && (
                <div className="flex gap-3 justify-start">
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <Bot className="w-4 h-4 text-primary" />
                  </div>
                  <div className="bg-muted rounded-lg px-4 py-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </ScrollArea>

        {/* Input */}
        <div className="p-4 border-t">
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

