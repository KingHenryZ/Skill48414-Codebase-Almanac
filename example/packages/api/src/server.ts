import "./database.js";
import express from "express";
import cors from "cors";
import helmet from "helmet";
import path from "path";
import { fileURLToPath } from "url";
import { authRoutes } from "./routes/auth.js";
import expenseRoutes from "./routes/expenses.js";
import categoryRoutes from "./routes/categories.js";
import summaryRoutes from "./routes/summary.js";
import { errorHandler } from "./middleware/errorHandler.js";
import { requestLogger } from "./middleware/requestLogger.js";
import { rateLimiter } from "./middleware/rateLimiter.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const publicDir = path.join(__dirname, "../../frontend/public");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(
  helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'", "https://cdn.jsdelivr.net"],
        styleSrc: ["'self'", "https://fonts.googleapis.com"],
        fontSrc: ["'self'", "https://fonts.gstatic.com"],
        connectSrc: ["'self'"],
        imgSrc: ["'self'", "data:"],
      },
    },
  }),
);
app.use(cors({ origin: process.env.ALLOWED_ORIGINS?.split(",") || "*" }));
app.use(express.json({ limit: "10kb" }));
app.use(requestLogger);
app.use(rateLimiter);

app.get("/health", (_req, res) => {
  res.json({ status: "ok", version: "1.0.0", uptime: process.uptime() });
});

app.use("/api/auth", authRoutes);
app.use("/api/categories", categoryRoutes);
app.use("/api/expenses", expenseRoutes);
app.use("/api/summary", summaryRoutes);

app.use(express.static(publicDir));

app.use((_req, res) => {
  res.status(404).json({ error: "Not found", code: "NOT_FOUND" });
});

app.use(errorHandler);

app.listen(PORT, () => {
  console.log(`SpendWise API + UI on http://localhost:${PORT}`);
});

export default app;
