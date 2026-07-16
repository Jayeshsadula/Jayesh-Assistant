import { KeyboardEvent, useEffect, useState } from "react";
import { ArrowUp, Square } from "lucide-react";

import ModelSelector from "@/components/chat/ModelSelector";
import { useChatStore } from "@/store/chatStore";
import { useSettingsStore } from "@/store/settingsStore";
import type { ModelName } from "@/types";

export default function ChatInput() {
  const [text, setText] = useState("");
  const { isStreaming, sendMessage, stopStreaming } = useChatStore();
  const { defaultModel, memoryEnabled, ragEnabled, isLoaded } = useSettingsStore();
  const [model, setModel] = useState<ModelName>(defaultModel);
  const [hasManualSelection, setHasManualSelection] = useState(false);

  // Once settings finish loading, adopt the user's saved default model —
  // unless they've already manually picked one in this session.
  useEffect(() => {
    if (isLoaded && !hasManualSelection) {
      setModel(defaultModel);
    }
  }, [isLoaded, defaultModel, hasManualSelection]);

  const handleModelChange = (next: ModelName) => {
    setHasManualSelection(true);
    setModel(next);
  };

  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed || isStreaming) return;
    setText("");
    sendMessage(trimmed, model, memoryEnabled, ragEnabled, []);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-border dark:border-border-dark bg-surface dark:bg-surface-dark p-4">
      <div className="mx-auto flex max-w-3xl flex-col gap-2 rounded-2xl border border-border dark:border-border-dark p-2.5">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          placeholder="Message JAYESH Assistant…"
          className="max-h-40 min-h-[24px] w-full resize-none bg-transparent px-1.5 py-1 text-sm outline-none placeholder:text-gray-400"
        />
        <div className="flex items-center justify-between">
          <ModelSelector value={model} onChange={handleModelChange} />

          {isStreaming ? (
            <button
              onClick={stopStreaming}
              className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-800 text-white transition hover:bg-gray-700"
              title="Stop generating"
            >
              <Square size={13} fill="currentColor" />
            </button>
          ) : (
            <button
              onClick={handleSend}
              disabled={!text.trim()}
              className="flex h-8 w-8 items-center justify-center rounded-full bg-accent text-white transition hover:bg-accent-hover disabled:opacity-40"
              title="Send"
            >
              <ArrowUp size={15} />
            </button>
          )}
        </div>
      </div>
      <p className="mt-2 text-center text-xs text-gray-400">
        JAYESH Assistant runs entirely on your local infrastructure.
      </p>
    </div>
  );
}
