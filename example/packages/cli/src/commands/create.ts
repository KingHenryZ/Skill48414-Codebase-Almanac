import { validateTask, type Task, type CreateTaskInput, TaskPriority } from "@taskflow/shared";
import { type CliConfig } from "../config";
import { apiRequest } from "../http";

export async function createTask(config: CliConfig, flags: Record<string, string>) {
  if (!flags.title) {
    console.error("Usage: taskflow create --title 'Task title' [--priority high] [--tags 'a,b']");
    process.exit(1);
  }

  const input: CreateTaskInput = {
    title: flags.title,
    description: flags.description,
    priority: (flags.priority as TaskPriority) || TaskPriority.Medium,
    tags: flags.tags?.split(",").map((t) => t.trim()),
  };

  const validation = validateTask(input);
  if (!validation.valid) {
    console.error("Validation errors:");
    for (const [field, msgs] of Object.entries(validation.errors)) {
      console.error(`  ${field}: ${msgs.join(", ")}`);
    }
    process.exit(1);
  }

  const { data: task } = await apiRequest<Task>(config, "/tasks", {
    method: "POST",
    body: input,
  });

  console.log(`\n  Task created: ${task.title} (${task.id})\n`);
}
