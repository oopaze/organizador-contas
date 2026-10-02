import { Text, View } from 'react-native';
import Bot from 'lucide-react-native/icons/bot';
import User from 'lucide-react-native/icons/user';
import Markdown from 'react-native-markdown-display';
import type { AICall } from '../services';
import { cn } from './ui/utils';

export interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  aiCall?: AICall | null;
}

/** Estilo do markdown do assistente (o renderer não entende classes NativeWind). */
const markdownStyles = {
  body: { fontSize: 14, lineHeight: 20, color: '#18181b' },
  heading1: { fontSize: 18, lineHeight: 24, marginTop: 12, marginBottom: 4 },
  heading2: { fontSize: 16, lineHeight: 22, marginTop: 12, marginBottom: 4 },
  heading3: { fontSize: 14, lineHeight: 20, marginTop: 12, marginBottom: 4 },
  paragraph: { marginTop: 4, marginBottom: 4 },
  list_item: { marginTop: 2, marginBottom: 2 },
  bullet_list: { marginTop: 2, marginBottom: 2 },
  ordered_list: { marginTop: 2, marginBottom: 2 },
  code_inline: { backgroundColor: '#e4e4e7', borderRadius: 4, paddingHorizontal: 4, fontSize: 12 },
  code_block: { backgroundColor: '#e4e4e7', borderRadius: 6, padding: 8, fontSize: 12 },
  fence: { backgroundColor: '#e4e4e7', borderRadius: 6, padding: 8, fontSize: 12 },
  blockquote: {
    backgroundColor: '#fafafa',
    borderColor: '#d4d4d8',
    borderLeftWidth: 4,
    marginVertical: 4,
    paddingHorizontal: 8,
  },
  hr: { backgroundColor: '#d4d4d8', height: 1, marginVertical: 8 },
  link: { color: '#059669' },
};

export function ChatMessage({ role, content, aiCall }: ChatMessageProps) {
  const isUser = role === 'user';

  return (
    <View className={cn('flex-row gap-2', isUser ? 'justify-end' : 'justify-start')}>
      {!isUser ? (
        <View className="h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-emerald-100">
          <Bot size={16} color="#059669" />
        </View>
      ) : null}

      <View
        className={cn(
          'max-w-[85%] rounded-lg px-3 py-2',
          isUser ? 'bg-emerald-600' : 'bg-zinc-100'
        )}
      >
        {isUser ? (
          <Text className="text-sm text-white">{content}</Text>
        ) : (
          <>
            <Markdown style={markdownStyles}>{content.replace(/\\n/g, '\n')}</Markdown>
            {aiCall ? (
              <View className="mt-2 flex-row items-center gap-2 border-t border-zinc-200 pt-2">
                <Text className="text-[10px] text-zinc-400">{aiCall.model}</Text>
                <Text className="text-[10px] font-medium text-zinc-500">
                  {aiCall.total_tokens.toLocaleString()} tokens
                </Text>
                <Text className="text-[10px] text-zinc-400">
                  ({aiCall.input_used_tokens.toLocaleString()}↓{' '}
                  {aiCall.output_used_tokens.toLocaleString()}↑)
                </Text>
              </View>
            ) : null}
          </>
        )}
      </View>

      {isUser ? (
        <View className="h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-emerald-600">
          <User size={16} color="#ffffff" />
        </View>
      ) : null}
    </View>
  );
}
