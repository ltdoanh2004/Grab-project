export interface Todo {
  id: number;
  title: string;
  description: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface CreateTodoDto {
  title: string;
  description?: string;
  status?: string;
}

export interface UpdateTodoDto {
  title?: string;
  description?: string;
  status?: string;
} 