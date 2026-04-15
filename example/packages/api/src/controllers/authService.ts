import { validateEmail, type User } from "@taskflow/shared";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import { v4 as uuidv4 } from "uuid";

const JWT_SECRET = process.env.JWT_SECRET || "change-me-in-production";
const users = new Map<string, User & { password: string }>();

export class AuthService {
  static async register(input: { email: string; username: string; password: string }) {
    if (!validateEmail(input.email)) {
      throw Object.assign(new Error("Invalid email format"), { status: 422 });
    }

    const existing = Array.from(users.values()).find((u) => u.email === input.email);
    if (existing) {
      throw Object.assign(new Error("Email already registered"), { status: 409 });
    }

    const hashed = await bcrypt.hash(input.password, 12);
    const user: User & { password: string } = {
      id: uuidv4(),
      email: input.email,
      username: input.username,
      role: "member",
      password: hashed,
      createdAt: new Date().toISOString(),
    };

    users.set(user.id, user);
    const token = jwt.sign({ userId: user.id, role: user.role }, JWT_SECRET, { expiresIn: "7d" });

    return { user: { id: user.id, email: user.email, username: user.username, role: user.role }, token };
  }

  static async login(email: string, password: string) {
    const user = Array.from(users.values()).find((u) => u.email === email);
    if (!user) throw Object.assign(new Error("Invalid credentials"), { status: 401 });

    const valid = await bcrypt.compare(password, user.password);
    if (!valid) throw Object.assign(new Error("Invalid credentials"), { status: 401 });

    const token = jwt.sign({ userId: user.id, role: user.role }, JWT_SECRET, { expiresIn: "7d" });

    return { user: { id: user.id, email: user.email, username: user.username, role: user.role }, token };
  }

  static async getProfile(userId: string) {
    const user = users.get(userId);
    if (!user) throw Object.assign(new Error("User not found"), { status: 404 });
    return { id: user.id, email: user.email, username: user.username, role: user.role };
  }
}
