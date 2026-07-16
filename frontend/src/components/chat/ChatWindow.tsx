import { useEffect, useRef } from "react";
import { RotateCcw, Sparkles } from "lucide-react";

import ChatMessage from "@/components/chat/ChatMessage";
import { useChatStore } from "@/store/chatStore";
import { useSettingsStore } from "@/store/settingsStore";

export default function ChatWindow() {
  const { messages, isStreaming, streamingText, regenerateLast } = useChatStore();
  const { defaultModel, memoryEnabled, ragEnabled } = useSettingsStore();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingText]);

  const canRegenerate =
    !isStreaming && messages.length > 0 && messages[messages.length - 1].role === "assistant";

  if (messages.length === 0 && !isStreaming) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 text-center px-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-accent text-white">
          <Sparkles size={22} />
        </div>
        <h2 className="text-lg font-semibold">How can I help you today?</h2>
        <p className="max-w-sm text-sm text-gray-400">
          Ask anything — I run entirely on local models via Ollama, with memory and document
          search built in.
        </p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="mx-auto max-w-3xl">
        {messages.map((message) => (
          <ChatMessage key={message.message_id} message={message} />
        ))}

        {isStreaming && (
          <ChatMessage
            message={{
              message_id: "streaming",
              role: "assistant",
              content: streamingText || "▋",
              created_at: new Date().toISOString(),
            }}
          />
        )}

        {canRegenerate && (
          <div className="px-4 pb-4">
            <button
              onClick={() => regenerateLast(defaultModel, memoryEnabled, ragEnabled, [])}
              className="flex items-center gap-1.5 rounded-lg border border-border dark:border-border-dark px-2.5 py-1.5 text-xs text-gray-500 transition hover:bg-panel dark:hover:bg-panel-dark"
            >
              <RotateCcw size={13} />
              Regenerate response
            </button>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}
