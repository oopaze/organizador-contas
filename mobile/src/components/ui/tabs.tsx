import { createContext, useContext, type ReactNode } from 'react';
import {
  Pressable,
  Text,
  View,
  type PressableProps,
  type ViewProps,
} from 'react-native';
import { cn } from './utils';

interface TabsContextValue {
  value: string;
  onValueChange: (value: string) => void;
}

const TabsContext = createContext<TabsContextValue | null>(null);

function useTabsContext(component: string) {
  const context = useContext(TabsContext);
  if (!context) throw new Error(`${component} precisa estar dentro de Tabs`);
  return context;
}

export interface TabsProps extends ViewProps {
  value: string;
  onValueChange: (value: string) => void;
  children?: ReactNode;
}

export function Tabs({ value, onValueChange, className, children, ...props }: TabsProps) {
  return (
    <TabsContext.Provider value={{ value, onValueChange }}>
      <View className={cn('flex-col gap-2', className)} {...props}>
        {children}
      </View>
    </TabsContext.Provider>
  );
}

export function TabsList({ className, ...props }: ViewProps) {
  return (
    <View
      accessibilityRole="tablist"
      className={cn(
        'h-9 flex-row items-center justify-center self-start rounded-xl bg-zinc-100 p-[3px]',
        className
      )}
      {...props}
    />
  );
}

export interface TabsTriggerProps extends Omit<PressableProps, 'onPress'> {
  value: string;
  children?: ReactNode;
}

export function TabsTrigger({ value, className, children, disabled, ...props }: TabsTriggerProps) {
  const context = useTabsContext('TabsTrigger');
  const selected = context.value === value;

  return (
    <Pressable
      {...props}
      disabled={disabled}
      accessibilityRole="tab"
      accessibilityState={{ selected, disabled: disabled ?? undefined }}
      onPress={() => context.onValueChange(value)}
      className={cn(
        'flex-1 flex-row items-center justify-center gap-1.5 rounded-xl border border-transparent px-2 py-1',
        selected ? 'bg-white' : 'bg-transparent',
        disabled && 'opacity-50',
        className
      )}
    >
      {typeof children === 'string' ? (
        <Text
          className={cn('text-sm font-medium', selected ? 'text-zinc-900' : 'text-zinc-500')}
        >
          {children}
        </Text>
      ) : (
        children
      )}
    </Pressable>
  );
}

export interface TabsContentProps extends ViewProps {
  value: string;
  children?: ReactNode;
}

export function TabsContent({ value, className, children, ...props }: TabsContentProps) {
  const context = useTabsContext('TabsContent');
  if (context.value !== value) return null;
  return (
    <View className={cn('flex-1', className)} {...props}>
      {children}
    </View>
  );
}
