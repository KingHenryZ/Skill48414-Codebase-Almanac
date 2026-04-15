import type { Task } from "@taskflow/shared";
import { formatDate } from "@taskflow/shared";
import { type CliConfig } from "../config";
import { apiRequest } from "../http";

export async function listTasks(config: CliConfig, flags: Record<string, string>) {
  const params = new URLSearchParams();
  if (flags.status) params.set("status", flags.status);
  if (flags.priority) params.set("priority", flags.priority);

  const { data } = await apiRequest<Task[]>(config, `/tasks?${params}`);

  if (data.length === 0) {
    console.log("No tasks found.");
    return;
  }

  console.log(`\n  Tasks (${data.length}):\n`);
  for (const task of data) {
    const status = statusIcon(task.status);
    const due = task.dueDate ? ` (due ${formatDate(task.dueDate)})` : "";
    console.log(`  ${status} [${task.priority}] ${task.title}${due}`);
  }
  console.log();
}

function statusIcon(status: string): string {
  const icons: Record<string, string> = {
    pending: "○",
    in_progress: "◐",
    done: "●",
    archived: "◌",
  };
  return icons[status] || "?";
}
