import type { Request, Response, NextFunction } from "express";

export function errorHandler(err: Error & { status?: number }, _req: Request, res: Response, _next: NextFunction) {
  const status = err.status || 500;

  if (status >= 500) {
    console.error(`[ERROR] ${err.message}`, { stack: err.stack });
  }

  res.status(status).json({
    error: status >= 500 && process.env.NODE_ENV === "production" ? "Internal server error" : err.message,
    code: status >= 500 ? "INTERNAL_ERROR" : "REQUEST_ERROR",
  });
}
