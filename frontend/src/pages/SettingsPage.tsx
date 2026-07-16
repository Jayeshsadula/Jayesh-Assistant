import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Brain, FileSearch, Monitor, Moon, Sun } from "lucide-react";

import { cn } from "@/lib/cn";
import { useSettingsStore } from "@/store/settingsStore";
import type { ModelName, ThemePreference } from "@/types";

const MODEL_OPTIONS: { value: ModelName; label: string; description: string }[] = [
  { value: "qwen2.5:7b", label: "Qwen 2.5", description: "Strong general-purpose reasoning" },
  { value: "llama3.1:8b", label: "Llama 3.1", description: "Meta's well-rounded open model" },
  { value: "mistral:7b", label: "Mistral", description: "Fast, efficient, lightweight" },
  { value: "gemma2:9b", label: "Gemma 2", description: "Google's open weight model" },
  { value: "deepseek-r1:7b", label: "DeepSeek R1", description: "Reasoning-focused model" },
];

const THEME_OPTIONS: { value: ThemePreference; label: string; icon: typeof Sun }[] = [
  { value: "light", label: "Light", icon: Sun },
  { value: "dark", label: "Dark", icon: Moon },
  { value: "system", label: "System", icon: Monitor },
];

function SettingsSection({ title, description, children }: { title: string; description: string; children: React.ReactNode }) {
  return (
    <section className="border-b border-border py-6 last:border-none dark:border-border-dark">
      <h2 className="text-sm font-semibold">{title}</h2>
      <p className="mt-0.5 text-sm text-gray-500 dark:text-gray-400">{description}</p>
      <div className="mt-4">{children}</div>
    </section>
  );
}

export default function SettingsPage() {
  const navigate = useNavigate();
  const {
    theme,
    defaultModel,
    memoryEnabled,
    ragEnabled,
    isLoaded,
    loadSettings,
    setTheme,
    setDefaultModel,
    setMemoryEnabled,
    setRagEnabled,
  } = useSettingsStore();

  useEffect(() => {
    if (!isLoaded) loadSettings();
  }, [isLoaded, loadSettings]);

  return (
    <div className="mx-auto h-screen max-w-2xl overflow-y-auto px-6 py-8">
      <button
        onClick={() => navigate("/")}
        className="mb-6 flex items-center gap-1.5 text-sm text-gray-500 transition hover:text-gray-800 dark:hover:text-gray-200"
      >
        <ArrowLeft size={15} />
        Back to chat
      </button>

      <h1 className="text-xl font-semibold">Settings</h1>
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Configure JAYESH Assistant's appearance, model, and memory behavior.
      </p>

      <SettingsSection title="Theme" description="Choose how JAYESH Assistant looks on this device.">
        <div className="grid grid-cols-3 gap-2">
          {THEME_OPTIONS.map(({ value, label, icon: Icon }) => (
            <button
              key={value}
              onClick={() => setTheme(value)}
              className={cn(
                "flex flex-col items-center gap-2 rounded-lg border px-3 py-3 text-sm transition",
                theme === value
                  ? "border-accent bg-accent/5 text-accent"
                  : "border-border hover:bg-panel dark:border-border-dark dark:hover:bg-panel-dark"
              )}
            >
              <Icon size={18} />
              {label}
            </button>
          ))}
        </div>
      </SettingsSection>

      <SettingsSection title="Default model" description="The model used for new conversations by default.">
        <div className="flex flex-col gap-2">
          {MODEL_OPTIONS.map(({ value, label, description }) => (
            <button
              key={value}
              onClick={() => setDefaultModel(value)}
              className={cn(
                "flex items-center justify-between rounded-lg border px-3 py-2.5 text-left text-sm transition",
                defaultModel === value
                  ? "border-accent bg-accent/5"
                  : "border-border hover:bg-panel dark:border-border-dark dark:hover:bg-panel-dark"
              )}
            >
              <span>
                <span className="font-medium">{label}</span>
                <span className="ml-2 text-xs text-gray-400">{description}</span>
              </span>
              {defaultModel === value && <span className="h-2 w-2 rounded-full bg-accent" />}
            </button>
          ))}
        </div>
      </SettingsSection>

      <SettingsSection title="Memory & retrieval" description="Control what context the assistant draws on when replying.">
        <div className="flex flex-col gap-3">
          <label className="flex items-center justify-between rounded-lg border border-border px-3 py-2.5 dark:border-border-dark">
            <span className="flex items-center gap-2 text-sm">
              <Brain size={16} className="text-gray-400" />
              Long-term memory
            </span>
            <input
              type="checkbox"
              checked={memoryEnabled}
              onChange={(e) => setMemoryEnabled(e.target.checked)}
              className="h-4 w-4 accent-accent"
            />
          </label>
          <label className="flex items-center justify-between rounded-lg border border-border px-3 py-2.5 dark:border-border-dark">
            <span className="flex items-center gap-2 text-sm">
              <FileSearch size={16} className="text-gray-400" />
              Document search (RAG)
            </span>
            <input
              type="checkbox"
              checked={ragEnabled}
              onChange={(e) => setRagEnabled(e.target.checked)}
              className="h-4 w-4 accent-accent"
            />
          </label>
        </div>
      </SettingsSection>
    </div>
  );
}
