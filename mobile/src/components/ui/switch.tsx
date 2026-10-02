import { Switch as NativeSwitch, type SwitchProps } from 'react-native';
import { cn } from './utils';

export function Switch({ className, ...props }: SwitchProps) {
  return (
    <NativeSwitch
      accessibilityRole="switch"
      trackColor={{ false: '#e4e4e7', true: '#a7f3d0' }}
      thumbColor={props.value ? '#059669' : '#f4f4f5'}
      className={cn('shrink-0', className)}
      {...props}
    />
  );
}
