import { ChatMessage } from '../types';
import { delay } from '../mockData';

// Mock AI responses based on keywords
const mockResponses: Record<string, string> = {
  'gasto': 'Analisando seus gastos do mês atual, você tem um total de R$ 2.500,00 em despesas. Os maiores gastos são: Alimentação (R$ 800), Transporte (R$ 400) e Lazer (R$ 350).',
  'receita': 'Suas receitas do mês totalizam R$ 5.000,00. A principal fonte é seu salário.',
  'saldo': 'Seu saldo atual é de R$ 2.500,00. Considerando os gastos de terceiros no seu cartão (R$ 500,00), seu saldo real é de R$ 3.000,00.',
  'ator': 'Você tem 3 atores cadastrados que usam seu cartão. O maior gastador é João com R$ 300,00 este mês.',
  'economia': 'Para economizar, sugiro revisar seus gastos com Lazer e Alimentação fora de casa. Você poderia economizar até R$ 200,00 por mês.',
  'fatura': 'Sua próxima fatura vence dia 15. O valor estimado é de R$ 2.800,00.',
};

function generateMockResponse(userMessage: string): string {
  const lowerMessage = userMessage.toLowerCase();
  
  for (const [keyword, response] of Object.entries(mockResponses)) {
    if (lowerMessage.includes(keyword)) {
      return response;
    }
  }
  
  return 'Entendi sua pergunta! No momento estou em modo de demonstração. Quando o backend estiver pronto, poderei analisar suas transações reais e fornecer insights personalizados sobre suas finanças. Tente perguntar sobre: gastos, receitas, saldo, atores, economia ou fatura.';
}

export async function sendChatMessage(message: string): Promise<ChatMessage> {
  await delay(1000); // Simulate AI thinking time
  
  const response: ChatMessage = {
    id: crypto.randomUUID(),
    role: 'assistant',
    content: generateMockResponse(message),
    timestamp: new Date(),
  };
  
  return response;
}

