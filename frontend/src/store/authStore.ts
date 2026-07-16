import {
  createUserWithEmailAndPassword,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  signOut,
  type User,
} from "firebase/auth";
import { create } from "zustand";

import { auth } from "@/lib/firebase";

interface AuthState {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  initAuthListener: () => void;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true,
  error: null,

  initAuthListener: () => {
    onAuthStateChanged(auth, (user) => {
      set({ user, isLoading: false });
    });
  },

  login: async (email, password) => {
    set({ error: null });
    try {
      await signInWithEmailAndPassword(auth, email, password);
    } catch (err) {
      set({ error: err instanceof Error ? err.message : "Failed to sign in." });
      throw err;
    }
  },

  signup: async (email, password) => {
    set({ error: null });
    try {
      await createUserWithEmailAndPassword(auth, email, password);
    } catch (err) {
      set({ error: err instanceof Error ? err.message : "Failed to sign up." });
      throw err;
    }
  },

  logout: async () => {
    await signOut(auth);
  },

  clearError: () => set({ error: null }),
}));
