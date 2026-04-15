import { readFileSync, writeFileSync, existsSync } from "fs";
import { join } from "path";
import { homedir } from "os";

export interface CliConfig {
  apiUrl: string;
  token: string | null;
}

const CONFIG_PATH = join(homedir(), ".taskflow.json");

export function loadConfig(): CliConfig {
  if (existsSync(CONFIG_PATH)) {
    const raw = readFileSync(CONFIG_PATH, "utf-8");
    return JSON.parse(raw);
  }
  return { apiUrl: "http://localhost:3000/api", token: null };
}

export function saveConfig(config: CliConfig): void {
  writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
}
