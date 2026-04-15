import type { Request, Response, NextFunction } from "express";
import { validateTask, type Task, TaskStatus, TaskPriority } from "@taskflow/shared";
import { paginate } from "@taskflow/shared";
import { v4 as uuidv4 } from "uuid";

const tasks = new Map<string, Task>();

export class TaskController {
  static list(req: Request, res: Response) {
    const { status, priority, page = "1", limit = "20" } = req.query;
    let items = Array.from(tasks.values());

    if (status) items = items.filter((t) => t.status === status);
    if (priority) items = items.filter((t) => t.priority === priority);

    const result = paginate(items, {
      page: Number(page),
      limit: Math.min(Number(limit), 100),
    });

    res.json({ data: result.items, meta: result.meta });
  }

  static getById(req: Request, res: Response) {
    const task = tasks.get(req.params.id);
    if (!task) return res.status(404).json({ error: "Task not found", code: "NOT_FOUND" });
    res.json({ data: task });
  }

  static create(req: Request, res: Response, next: NextFunction) {
    const validation = validateTask(req.body);
    if (!validation.valid) {
      return res.status(422).json({ error: "Validation failed", code: "INVALID_INPUT", details: validation.errors });
    }

    const task: Task = {
      id: uuidv4(),
      title: req.body.title,
      description: req.body.description || "",
      status: TaskStatus.Pending,
      priority: req.body.priority || TaskPriority.Medium,
      assigneeId: req.body.assigneeId || null,
      tags: req.body.tags || [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      dueDate: req.body.dueDate || null,
    };

    tasks.set(task.id, task);
    res.status(201).json({ data: task });
  }

  static update(req: Request, res: Response) {
    const task = tasks.get(req.params.id);
    if (!task) return res.status(404).json({ error: "Task not found", code: "NOT_FOUND" });

    const allowed = ["title", "description", "status", "priority", "assigneeId", "tags", "dueDate"] as const;
    for (const key of allowed) {
      if (req.body[key] !== undefined) {
        (task as any)[key] = req.body[key];
      }
    }
    task.updatedAt = new Date().toISOString();
    tasks.set(task.id, task);
    res.json({ data: task });
  }

  static remove(req: Request, res: Response) {
    if (!tasks.delete(req.params.id)) {
      return res.status(404).json({ error: "Task not found", code: "NOT_FOUND" });
    }
    res.status(204).send();
  }

  static assign(req: Request, res: Response) {
    const task = tasks.get(req.params.id);
    if (!task) return res.status(404).json({ error: "Task not found", code: "NOT_FOUND" });

    task.assigneeId = req.body.assigneeId;
    task.updatedAt = new Date().toISOString();
    tasks.set(task.id, task);
    res.json({ data: task });
  }
}
