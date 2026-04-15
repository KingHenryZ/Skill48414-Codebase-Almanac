import { validateEmail } from "@taskflow/shared";
import { type CliConfig, saveConfig } from "../config";
import { apiRequest } from "../http";

export async function loginCommand(config: CliConfig, flags: Record<string, string>) {
  if (!flags.email || !flags.password) {
    console.error("Usage: taskflow login --email user@example.com --password secret");
    process.exit(1);
  }

  if (!validateEmail(flags.email)) {
    console.error("Invalid email format.");
    process.exit(1);
  }

  const { data } = await apiRequest<{ token: string; user: { username: string } }>(config, "/auth/login", {
    method: "POST",
    body: { email: flags.email, password: flags.password },
  });

  saveConfig({ ...config, token: data.token });
  console.log(`\n  Logged in as ${data.user.username}. Token saved to ~/.taskflow.json\n`);
}
