export enum TaskStatus {
  Pending = "pending",
  InProgress = "in_progress",
  Done = "done",
  Archived = "archived",
}

export enum TaskPriority {
  Low = "low",
  Medium = "medium",
  High = "high",
  Critical = "critical",
}

export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  assigneeId: string | null;
  tags: string[];
  createdAt: string;
  updatedAt: string;
  dueDate: string | null;
}

export interface User {
  id: string;
  email: string;
  username: string;
  role: "admin" | "member" | "viewer";
  createdAt: string;
}

export interface ApiResponse<T> {
  data: T;
  meta?: {
    page: number;
    limit: number;
    total: number;
  };
}

export interface ApiError {
  error: string;
  code: string;
  details?: Record<string, string[]>;
}

export interface CreateTaskInput {
  title: string;
  description?: string;
  priority?: TaskPriority;
  assigneeId?: string;
  tags?: string[];
  dueDate?: string;
}

export interface UpdateTaskInput {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  assigneeId?: string | null;
  tags?: string[];
  dueDate?: string | null;
}
