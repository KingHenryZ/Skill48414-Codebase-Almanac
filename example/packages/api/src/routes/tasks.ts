import { Router } from "express";
import { TaskController } from "../controllers/taskController";
import { authenticate } from "../middleware/authenticate";
import { validateBody } from "../middleware/validateBody";

export const taskRoutes = Router();

taskRoutes.get("/", authenticate, TaskController.list);
taskRoutes.get("/:id", authenticate, TaskController.getById);
taskRoutes.post("/", authenticate, validateBody, TaskController.create);
taskRoutes.put("/:id", authenticate, validateBody, TaskController.update);
taskRoutes.delete("/:id", authenticate, TaskController.remove);
taskRoutes.post("/:id/assign", authenticate, TaskController.assign);
