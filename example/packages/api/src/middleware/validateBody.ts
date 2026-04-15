import type { Request, Response, NextFunction } from "express";
import { sanitize } from "@taskflow/shared";

export function validateBody(req: Request, res: Response, next: NextFunction) {
  if (!req.body || typeof req.body !== "object") {
    return res.status(400).json({ error: "Request body must be a JSON object", code: "INVALID_BODY" });
  }

  if (req.body.title) req.body.title = sanitize(req.body.title);
  if (req.body.description) req.body.description = sanitize(req.body.description);

  next();
}
