import { create } from "zustand";

import { api } from "@/lib/api";
import type { ModelName, ThemePreference, UserSettingsPublic } from "@/types";

interface SettingsState {
  theme: ThemePreference;
  defaultModel: ModelName;
  memoryEnabled: boolean;
  ragEnabled: boolean;
  isLoaded: boolean;
  loadSettings: () => Promise<void>;
  setTheme: (theme: ThemePreference) => Promise<void>;
  setDefaultModel: (model: ModelName) => Promise<void>;
  setMemoryEnabled: (enabled: boolean) => Promise<void>;
  setRagEnabled: (enabled: boolean) => Promise<void>;
}

function applyThemeToDocument(theme: ThemePreference) {
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const shouldUseDark = theme === "dark" || (theme === "system" && prefersDark);
  document.documentElement.classList.toggle("dark", shouldUseDark);
}

export const useSettingsStore = create<SettingsState>((set, get) => ({
  theme: "system",
  defaultModel: "qwen2.5:7b",
  memoryEnabled: true,
  ragEnabled: true,
  isLoaded: false,

  loadSettings: async () => {
    try {
      const settings = await api.get<UserSettingsPublic>("/settings");
      set({
        theme: settings.theme,
        defaultModel: settings.default_model,
        memoryEnabled: settings.memory_enabled,
        ragEnabled: settings.rag_enabled,
        isLoaded: true,
      });
      applyThemeToDocument(settings.theme);
    } catch {
      set({ isLoaded: true });
      applyThemeToDocument(get().theme);
    }
  },

  setTheme: async (theme) => {
    set({ theme });
    applyThemeToDocument(theme);
    await api.put("/settings", { theme });
  },

  setDefaultModel: async (model) => {
    set({ defaultModel: model });
    await api.put("/settings", { default_model: model });
  },

  setMemoryEnabled: async (enabled) => {
    set({ memoryEnabled: enabled });
    await api.put("/settings", { memory_enabled: enabled });
  },

  setRagEnabled: async (enabled) => {
    set({ ragEnabled: enabled });
    await api.put("/settings", { rag_enabled: enabled });
  },
}));
