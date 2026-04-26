import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import { randomUUID } from "crypto";
import { db } from "../database.js";
import { validateEmail } from "@spendwise/shared";

const JWT_SECRET = process.env.JWT_SECRET || "change-me-in-production";

export class AuthService {
  static async register(input: { email: string; password: string; name: string }) {
    if (!validateEmail(input.email)) {
      throw Object.assign(new Error("Invalid email format"), { status: 422 });
    }

    const name = (input.name || "").trim();
    if (!name) {
      throw Object.assign(new Error("Name is required"), { status: 422 });
    }

    if (!input.password || input.password.length < 8) {
      throw Object.assign(new Error("Password must be at least 8 characters"), { status: 422 });
    }

    const email = input.email.toLowerCase().trim();
    const existing = db.prepare("SELECT id FROM users WHERE email = ?").get(email);
    if (existing) {
      throw Object.assign(new Error("Email already registered"), { status: 409 });
    }

    const id = randomUUID();
    const hashed = await bcrypt.hash(input.password, 12);
    db.prepare("INSERT INTO users (id, email, password_hash, name) VALUES (?, ?, ?, ?)").run(id, email, hashed, name);

    const token = jwt.sign({ userId: id, role: "member" }, JWT_SECRET, { expiresIn: "7d" });
    return { user: { id, email, name }, token };
  }

  static async login(email: string, password: string) {
    const row = db.prepare("SELECT * FROM users WHERE email = ?").get(email.toLowerCase().trim()) as
      | { id: string; email: string; name: string; password_hash: string }
      | undefined;
    if (!row) {
      throw Object.assign(new Error("Invalid credentials"), { status: 401 });
    }

    const valid = await bcrypt.compare(password, row.password_hash);
    if (!valid) {
      throw Object.assign(new Error("Invalid credentials"), { status: 401 });
    }

    const token = jwt.sign({ userId: row.id, role: "member" }, JWT_SECRET, { expiresIn: "7d" });
    return { user: { id: row.id, email: row.email, name: row.name }, token };
  }

  static async getProfile(userId: string) {
    const user = db.prepare("SELECT id, email, name FROM users WHERE id = ?").get(userId) as
      | { id: string; email: string; name: string }
      | undefined;
    if (!user) {
      throw Object.assign(new Error("User not found"), { status: 404 });
    }
    return user;
  }
}
