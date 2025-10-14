import { useContext } from "react";
import { AuthContext } from "../contexts/AuthContext.ts";
import type { AuthContextType } from "../types/feedback";

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
