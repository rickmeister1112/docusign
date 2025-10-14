import { createContext } from "react";
import type { AuthContextType } from "../types/feedback";

export const AuthContext = createContext<AuthContextType | undefined>(
  undefined
);
