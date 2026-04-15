export function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

export interface PaginationParams {
  page: number;
  limit: number;
}

export interface PaginatedResult<T> {
  items: T[];
  meta: { page: number; limit: number; total: number; totalPages: number };
}

export function paginate<T>(
  items: T[],
  { page, limit }: PaginationParams,
): PaginatedResult<T> {
  const total = items.length;
  const totalPages = Math.ceil(total / limit);
  const start = (page - 1) * limit;
  const paged = items.slice(start, start + limit);

  return {
    items: paged,
    meta: { page, limit, total, totalPages },
  };
}
