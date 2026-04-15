import { TaskPriority, TaskStatus, type CreateTaskInput, type UpdateTaskInput } from "./types";

export interface ValidationResult {
  valid: boolean;
  errors: Record<string, string[]>;
}

export function validateTask(input: CreateTaskInput): ValidationResult {
  const errors: Record<string, string[]> = {};

  if (!input.title || input.title.trim().length === 0) {
    errors.title = ["Title is required"];
  } else if (input.title.length > 200) {
    errors.title = ["Title must be under 200 characters"];
  }

  if (input.priority && !Object.values(TaskPriority).includes(input.priority)) {
    errors.priority = [`Must be one of: ${Object.values(TaskPriority).join(", ")}`];
  }

  if (input.tags && input.tags.length > 10) {
    errors.tags = ["Maximum 10 tags per task"];
  }

  if (input.dueDate) {
    const date = new Date(input.dueDate);
    if (isNaN(date.getTime())) {
      errors.dueDate = ["Invalid date format"];
    }
  }

  return { valid: Object.keys(errors).length === 0, errors };
}

export function validateTaskUpdate(input: UpdateTaskInput): ValidationResult {
  const errors: Record<string, string[]> = {};

  if (input.title !== undefined) {
    if (input.title.trim().length === 0) {
      errors.title = ["Title cannot be empty"];
    } else if (input.title.length > 200) {
      errors.title = ["Title must be under 200 characters"];
    }
  }

  if (input.status && !Object.values(TaskStatus).includes(input.status)) {
    errors.status = [`Must be one of: ${Object.values(TaskStatus).join(", ")}`];
  }

  if (input.priority && !Object.values(TaskPriority).includes(input.priority)) {
    errors.priority = [`Must be one of: ${Object.values(TaskPriority).join(", ")}`];
  }

  return { valid: Object.keys(errors).length === 0, errors };
}

export function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export function sanitize(input: string): string {
  return input.replace(/<[^>]*>/g, "").trim();
}
