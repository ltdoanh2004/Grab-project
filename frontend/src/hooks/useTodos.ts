import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { todoApi } from '../services/todoApi';
import { UpdateTodoDto } from '../types/todo';
import { notification } from 'antd';
import { TodoStatus } from '../constants/todoConstants';

interface TodoFormData {
  title: string;
  description?: string;
  status: TodoStatus;
}

export const useTodos = () => {
  const queryClient = useQueryClient();
  const [api, contextHolder] = notification.useNotification();

  const { data: todos = [], isPending } = useQuery({
    queryKey: ['todos'],
    queryFn: todoApi.getAll,
  });

  const createMutation = useMutation({
    mutationFn: (data: TodoFormData) => todoApi.create({ ...data, status: data.status || 'pending' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
      api.success({
        message: 'Success',
        description: 'Todo created successfully',
        placement: 'topRight',
        duration: 3,
      });
    },
    onError: () => {
      api.error({
        message: 'Error',
        description: 'Failed to create todo',
        placement: 'topRight',
        duration: 3,
      });
    },
  });

  const updateMutation = useMutation({
    mutationFn: (params: { id: number } & UpdateTodoDto) => 
      todoApi.update(params.id, { title: params.title, description: params.description, status: params.status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
      api.success({
        message: 'Success',
        description: 'Todo updated successfully',
        placement: 'topRight',
        duration: 3,
      });
    },
    onError: () => {
      api.error({
        message: 'Error',
        description: 'Failed to update todo',
        placement: 'topRight',
        duration: 3,
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: todoApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
      api.success({
        message: 'Success',
        description: 'Todo deleted successfully',
        placement: 'topRight',
        duration: 3,
      });
    },
    onError: () => {
      api.error({
        message: 'Error',
        description: 'Failed to delete todo',
        placement: 'topRight',
        duration: 3,
      });
    },
  });

  return {
    todos,
    isLoading: isPending,
    createTodo: createMutation.mutateAsync,
    updateTodo: updateMutation.mutateAsync,
    deleteTodo: deleteMutation.mutate,
    isDeleting: deleteMutation.isPending,
    isSubmitting: createMutation.isPending || updateMutation.isPending,
    contextHolder,
  };
}; 