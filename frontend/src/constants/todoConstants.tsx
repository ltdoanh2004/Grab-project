import { ClockCircleOutlined, SyncOutlined, CheckCircleOutlined } from '@ant-design/icons';

export const STATUS_COLORS = {
  pending: 'gold',
  in_progress: 'blue',
  completed: 'green',
} as const;

export const STATUS_LABELS = {
  pending: 'Pending',
  in_progress: 'In Progress',
  completed: 'Completed',
} as const;

export const STATUS_ICONS = {
  pending: <ClockCircleOutlined />,
  in_progress: <SyncOutlined />,
  completed: <CheckCircleOutlined />,
} as const;

export type TodoStatus = keyof typeof STATUS_LABELS; 