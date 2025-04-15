import { Button, Space, Table, Tag, Typography, Popconfirm } from 'antd';
import { DeleteOutlined, EditOutlined } from '@ant-design/icons';
import { Todo } from '../types/todo';
import { STATUS_COLORS, STATUS_ICONS, STATUS_LABELS, TodoStatus } from '../constants/todoConstants';

const { Text } = Typography;

interface TodoTableProps {
  todos: Todo[];
  isLoading: boolean;
  onEdit: (todo: Todo) => void;
  onDelete: (id: number) => void;
  isDeleting: boolean;
}

export function TodoTable({ todos, isLoading, onEdit, onDelete, isDeleting }: TodoTableProps) {
  const columns = [
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      width: '30%',
      render: (text: string) => (
        <Text strong style={{ fontSize: '15px' }}>{text}</Text>
      ),
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      width: '40%',
      render: (text: string) => (
        <Text type="secondary" style={{ fontSize: '14px' }}>{text || '-'}</Text>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: '15%',
      render: (status: TodoStatus) => (
        <Tag 
          color={STATUS_COLORS[status]}
          icon={STATUS_ICONS[status]}
        >
          {STATUS_LABELS[status]}
        </Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: '15%',
      render: (_: unknown, record: Todo) => (
        <Space>
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => onEdit(record)}
          >
            Edit
          </Button>
          <Popconfirm
            title="Delete Todo"
            description={`Are you sure to delete "${record.title}"?`}
            onConfirm={() => onDelete(record.id)}
            okText="Yes"
            cancelText="No"
            okType="danger"
          >
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              loading={isDeleting}
            >
              Delete
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={todos}
      loading={isLoading}
      rowKey="id"
      pagination={{ 
        pageSize: 10,
        showSizeChanger: true,
        showQuickJumper: true,
        showTotal: (total) => `Total ${total} items`,
      }}
    />
  );
} 