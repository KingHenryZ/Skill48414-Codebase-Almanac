export function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export function validateCategory(input: { name?: string; color?: string; icon?: string }): string[] {
  const errors: string[] = [];
  if (!input.name || input.name.trim().length === 0) {
    errors.push("Category name is required");
  } else if (input.name.trim().length > 80) {
    errors.push("Category name must be 80 characters or less");
  }
  if (input.color != null && input.color !== "" && !/^#[0-9A-Fa-f]{6}$/.test(input.color)) {
    errors.push("Color must be a hex value like #6b7280");
  }
  if (input.icon != null && input.icon.length > 8) {
    errors.push("Icon must be 8 characters or less");
  }
  return errors;
}

export function validateExpense(input: {
  amount?: unknown;
  date?: unknown;
  description?: unknown;
}): string[] {
  const errors: string[] = [];
  const amount = input.amount;
  if (amount === undefined || amount === null || amount === "") {
    errors.push("Amount is required");
  } else if (typeof amount !== "number" || Number.isNaN(amount) || amount <= 0) {
    errors.push("Amount must be a positive number");
  }
  if (input.date === undefined || input.date === null || String(input.date).trim() === "") {
    errors.push("Date is required");
  } else {
    const d = new Date(String(input.date));
    if (Number.isNaN(d.getTime())) {
      errors.push("Date must be a valid ISO or YYYY-MM-DD value");
    }
  }
  if (input.description != null && typeof input.description === "string" && input.description.length > 500) {
    errors.push("Description must be 500 characters or less");
  }
  return errors;
}
