import { ChevronDown } from "lucide-react";
import { useState } from "react";

import { cn } from "@/lib/cn";
import type { ModelName } from "@/types";

const MODEL_LABELS: Record<ModelName, string> = {
  "qwen2.5:7b": "Qwen 2.5",
  "llama3.1:8b": "Llama 3.1",
  "mistral:7b": "Mistral",
  "gemma2:9b": "Gemma 2",
  "deepseek-r1:7b": "DeepSeek R1",
};

const MODELS = Object.keys(MODEL_LABELS) as ModelName[];

export default function ModelSelector({
  value,
  onChange,
}: {
  value: ModelName;
  onChange: (model: ModelName) => void;
}) {
  const [open, setOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1.5 rounded-lg border border-border dark:border-border-dark px-2.5 py-1.5 text-xs font-medium transition hover:bg-panel dark:hover:bg-panel-dark"
      >
        {MODEL_LABELS[value]}
        <ChevronDown size={13} />
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
          <div className="absolute bottom-full z-20 mb-1 w-40 rounded-lg border border-border dark:border-border-dark bg-surface dark:bg-surface-dark p-1 shadow-lg">
            {MODELS.map((model) => (
              <button
                key={model}
                onClick={() => {
                  onChange(model);
                  setOpen(false);
                }}
                className={cn(
                  "block w-full rounded-md px-2.5 py-1.5 text-left text-xs transition hover:bg-panel dark:hover:bg-panel-dark",
                  value === model && "font-semibold text-accent"
                )}
              >
                {MODEL_LABELS[model]}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
