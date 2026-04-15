import { Router, type Request, type Response, type NextFunction } from "express";
import { AuthService } from "../controllers/authService";
import { authenticate } from "../middleware/authenticate";

export const authRoutes = Router();

authRoutes.post("/register", async (req: Request, res: Response, next: NextFunction) => {
  try {
    const result = await AuthService.register(req.body);
    res.status(201).json({ data: result });
  } catch (err) {
    next(err);
  }
});

authRoutes.post("/login", async (req: Request, res: Response, next: NextFunction) => {
  try {
    const result = await AuthService.login(req.body.email, req.body.password);
    res.json({ data: result });
  } catch (err) {
    next(err);
  }
});

authRoutes.get("/me", authenticate, async (req: Request, res: Response, next: NextFunction) => {
  try {
    const user = await AuthService.getProfile(req.userId!);
    res.json({ data: user });
  } catch (err) {
    next(err);
  }
});
