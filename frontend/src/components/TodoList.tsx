import { Button, Card, Empty, Modal, Typography } from 'antd';
import { PlusOutlined, InboxOutlined } from '@ant-design/icons';
import { useState } from 'react';
import { Todo } from '../types/todo';
import { useTodos } from '../hooks/useTodos';
import { TodoForm } from './TodoForm';
import { TodoTable } from './TodoTable';
import { TodoStatus } from '../constants/todoConstants';
import './TodoList.css';

const { Title, Text } = Typography;

interface TodoFormData {
  title: string;
  description?: string;
  status: TodoStatus;
}

export function TodoList() {
  const { 
    todos, 
    isLoading, 
    createTodo, 
    updateTodo, 
    deleteTodo, 
    isDeleting,
    isSubmitting,
    contextHolder 
  } = useTodos();
  
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingTodo, setEditingTodo] = useState<Todo | undefined>(undefined);

  const handleSubmit = async (data: TodoFormData) => {
    if (editingTodo) {
      await updateTodo({ id: editingTodo.id, ...data });
    } else {
      await createTodo(data);
    }
    handleCloseModal();
  };

  const handleCloseModal = () => {
    setIsModalVisible(false);
    setEditingTodo(undefined);
  };

  const handleAddNew = () => {
    setEditingTodo(undefined);
    setIsModalVisible(true);
  };

  const handleEdit = (todo: Todo) => {
    setEditingTodo(todo);
    setIsModalVisible(true);
  };

  return (
    <div className="todo-list-container">
      {contextHolder}
      <Card bordered={false} style={{ boxShadow: 'none' }}>
        <div className="todo-header">
          <div>
            <Title level={2}>Todo List</Title>
            <Text type="secondary">Manage your tasks efficiently</Text>
          </div>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleAddNew}
          >
            Add Todo
          </Button>
        </div>

        {todos.length === 0 ? (
          <Empty
            image={<InboxOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />}
            description="No todos yet. Add your first task!"
            style={{ margin: '2rem 0' }}
          >
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleAddNew}
            >
              Add Todo
            </Button>
          </Empty>
        ) : (
          <TodoTable
            todos={todos}
            isLoading={isLoading}
            onEdit={handleEdit}
            onDelete={deleteTodo}
            isDeleting={isDeleting}
          />
        )}
      </Card>

      <Modal
        title={editingTodo ? 'Edit Todo' : 'Add New Todo'}
        open={isModalVisible}
        onCancel={handleCloseModal}
        footer={null}
        width={600}
        destroyOnClose
      >
        <TodoForm
          key={editingTodo?.id || 'new'}
          initialData={editingTodo}
          onSubmit={handleSubmit}
          onCancel={handleCloseModal}
          isLoading={isSubmitting}
        />
      </Modal>
    </div>
  );
} 