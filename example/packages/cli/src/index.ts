#!/usr/bin/env node
import { parseArgs } from "./args";
import { listTasks } from "./commands/list";
import { createTask } from "./commands/create";
import { loginCommand } from "./commands/login";
import { loadConfig } from "./config";

async function main() {
  const config = loadConfig();
  const { command, flags } = parseArgs(process.argv.slice(2));

  const commands: Record<string, () => Promise<void>> = {
    list: () => listTasks(config, flags),
    create: () => createTask(config, flags),
    login: () => loginCommand(config, flags),
  };

  const handler = commands[command];
  if (!handler) {
    console.error(`Unknown command: ${command}`);
    console.error("Available: list, create, login");
    process.exit(1);
  }

  await handler();
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
