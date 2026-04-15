import type { CliConfig } from "./config";

export async function apiRequest<T>(
  config: CliConfig,
  path: string,
  options?: { method?: string; body?: unknown },
): Promise<{ data: T }> {
  const url = `${config.apiUrl}${path}`;
  const headers: Record<string, string> = { "Content-Type": "application/json" };

  if (config.token) {
    headers["Authorization"] = `Bearer ${config.token}`;
  }

  const res = await fetch(url, {
    method: options?.method || "GET",
    headers,
    body: options?.body ? JSON.stringify(options.body) : undefined,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `API error: ${res.status}`);
  }

  return res.json();
}
