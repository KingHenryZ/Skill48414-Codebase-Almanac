import type { Request, Response, NextFunction } from "express";

const windowMs = 15 * 60 * 1000;
const maxRequests = 100;
const hits = new Map<string, { count: number; resetAt: number }>();

export function rateLimiter(req: Request, res: Response, next: NextFunction) {
  const ip = req.ip || req.socket.remoteAddress || "unknown";
  const now = Date.now();

  let record = hits.get(ip);
  if (!record || now > record.resetAt) {
    record = { count: 0, resetAt: now + windowMs };
    hits.set(ip, record);
  }

  record.count++;
  res.setHeader("X-RateLimit-Limit", String(maxRequests));
  res.setHeader("X-RateLimit-Remaining", String(Math.max(0, maxRequests - record.count)));

  if (record.count > maxRequests) {
    return res.status(429).json({ error: "Too many requests", code: "RATE_LIMITED" });
  }

  next();
}
