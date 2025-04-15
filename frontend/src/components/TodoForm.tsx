import { Form, Input, Select, Space, Button } from 'antd';
import { Todo } from '../types/todo';
import { STATUS_ICONS, STATUS_LABELS, TodoStatus } from '../constants/todoConstants';
import { useEffect } from 'react';

const { TextArea } = Input;

interface TodoFormProps {
  initialData?: Todo;
  onSubmit: (values: { title: string; description?: string; status: TodoStatus }) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

export function TodoForm({ initialData, onSubmit, onCancel, isLoading }: TodoFormProps) {
  const [form] = Form.useForm();

  useEffect(() => {
    form.setFieldsValue({
      title: initialData?.title || '',
      description: initialData?.description || '',
      status: initialData?.status || 'pending',
    });
  }, [form, initialData]);

  return (
    <Form 
      form={form}
      onFinish={onSubmit}
      layout="vertical"
      preserve={false}
    >
      <Form.Item
        name="title"
        label="Title"
        rules={[{ required: true, message: 'Please input the title!' }]}
      >
        <Input placeholder="Enter task title" disabled={isLoading} />
      </Form.Item>
      
      <Form.Item
        name="description"
        label="Description"
      >
        <TextArea 
          rows={4} 
          placeholder="Enter task description"
          showCount
          maxLength={500}
          disabled={isLoading}
        />
      </Form.Item>
      
      <Form.Item
        name="status"
        label="Status"
        initialValue="pending"
      >
        <Select disabled={isLoading}>
          {Object.entries(STATUS_LABELS).map(([value, label]) => (
            <Select.Option 
              key={value} 
              value={value}
              icon={STATUS_ICONS[value as TodoStatus]}
            >
              {label}
            </Select.Option>
          ))}
        </Select>
      </Form.Item>
      
      <Form.Item>
        <Space>
          <Button 
            type="primary" 
            htmlType="submit"
            loading={isLoading}
          >
            {initialData ? 'Update' : 'Create'}
          </Button>
          <Button 
            onClick={onCancel}
            disabled={isLoading}
          >
            Cancel
          </Button>
        </Space>
      </Form.Item>
    </Form>
  );
} 