export interface ParsedArgs {
  command: string;
  flags: Record<string, string>;
}

export function parseArgs(argv: string[]): ParsedArgs {
  const command = argv[0] || "help";
  const flags: Record<string, string> = {};

  for (let i = 1; i < argv.length; i++) {
    const arg = argv[i];
    if (arg.startsWith("--")) {
      const key = arg.slice(2);
      const value = argv[i + 1] && !argv[i + 1].startsWith("--") ? argv[++i] : "true";
      flags[key] = value;
    }
  }

  return { command, flags };
}
