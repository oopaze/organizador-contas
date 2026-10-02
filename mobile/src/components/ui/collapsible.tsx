import type { ReactNode } from 'react';
import { Pressable, View, type ViewProps } from 'react-native';
import { cn } from './utils';

export interface CollapsibleProps extends Omit<ViewProps, 'children'> {
  open: boolean;
  onOpenChange?: (open: boolean) => void;
  trigger: ReactNode;
  children?: ReactNode;
}

export function Collapsible({
  open,
  onOpenChange,
  trigger,
  children,
  className,
  ...props
}: CollapsibleProps) {
  return (
    <View className={cn(className)} {...props}>
      <Pressable
        accessibilityRole="button"
        accessibilityState={{ expanded: open }}
        onPress={() => onOpenChange?.(!open)}
      >
        {trigger}
      </Pressable>
      {open ? <View>{children}</View> : null}
    </View>
  );
}
