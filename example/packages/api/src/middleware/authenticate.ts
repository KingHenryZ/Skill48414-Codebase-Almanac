import type { Request, Response, NextFunction } from "express";
import jwt from "jsonwebtoken";

const JWT_SECRET = process.env.JWT_SECRET || "change-me-in-production";

declare global {
  namespace Express {
    interface Request {
      userId?: string;
      userRole?: string;
    }
  }
}

export function authenticate(req: Request, res: Response, next: NextFunction) {
  const header = req.headers.authorization;
  if (!header?.startsWith("Bearer ")) {
    return res.status(401).json({ error: "Missing authorization token", code: "UNAUTHORIZED" });
  }

  try {
    const payload = jwt.verify(header.slice(7), JWT_SECRET) as { userId: string; role: string };
    req.userId = payload.userId;
    req.userRole = payload.role;
    next();
  } catch {
    res.status(401).json({ error: "Invalid or expired token", code: "UNAUTHORIZED" });
  }
}
