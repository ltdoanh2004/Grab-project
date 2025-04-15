import axios from 'axios';
import { CreateTodoDto, Todo, UpdateTodoDto } from '../types/todo';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

export const todoApi = {
  getAll: async (): Promise<Todo[]> => {
    const response = await api.get('/todos');
    return response.data.data;
  },

  getById: async (id: number): Promise<Todo> => {
    const response = await api.get(`/todos/${id}`);
    return response.data.data;
  },

  create: async (todo: CreateTodoDto): Promise<Todo> => {
    const response = await api.post('/todos', todo);
    return response.data.data;
  },

  update: async (id: number, todo: UpdateTodoDto): Promise<Todo> => {
    const response = await api.put(`/todos/${id}`, todo);
    return response.data.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/todos/${id}`);
  },
}; 