import express from "express";
import cors from "cors";
import helmet from "helmet";
import { taskRoutes } from "./routes/tasks";
import { authRoutes } from "./routes/auth";
import { errorHandler } from "./middleware/errorHandler";
import { requestLogger } from "./middleware/requestLogger";
import { rateLimiter } from "./middleware/rateLimiter";

const app = express();
const PORT = process.env.PORT || 3000;

app.use(helmet());
app.use(cors({ origin: process.env.ALLOWED_ORIGINS?.split(",") || "*" }));
app.use(express.json({ limit: "10kb" }));
app.use(requestLogger);
app.use(rateLimiter);

app.get("/health", (_req, res) => {
  res.json({ status: "ok", version: "1.0.0", uptime: process.uptime() });
});

app.use("/api/auth", authRoutes);
app.use("/api/tasks", taskRoutes);

app.use(errorHandler);

app.listen(PORT, () => {
  console.log(`TaskFlow API running on port ${PORT}`);
});

export default app;
