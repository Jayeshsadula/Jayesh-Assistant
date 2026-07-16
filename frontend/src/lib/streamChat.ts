import { api } from "@/lib/api";
import type { ChatRequestPayload } from "@/types";

export interface StreamCallbacks {
  onToken: (token: string) => void;
  onDone: (conversationId: string, fullText: string) => void;
  onError: (message: string) => void;
}

/**
 * Streams a chat completion from POST /chat/stream.
 *
 * Native EventSource doesn't support POST bodies or custom headers, so we
 * use fetch() with a ReadableStream reader and parse the `data: {...}\n\n`
 * SSE frames manually.
 */
export async function streamChat(
  payload: ChatRequestPayload,
  callbacks: StreamCallbacks,
  signal?: AbortSignal
): Promise<void> {
  const { url, headers } = await api.getStreamConfig("/chat/stream");

  const response = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
    signal,
  });

  if (!response.ok || !response.body) {
    callbacks.onError(`Request failed with status ${response.status}`);
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const frames = buffer.split("\n\n");
    buffer = frames.pop() ?? "";

    for (const frame of frames) {
      const line = frame.trim();
      if (!line.startsWith("data:")) continue;

      const jsonStr = line.slice(5).trim();
      try {
        const event = JSON.parse(jsonStr);
        if (event.type === "token") {
          callbacks.onToken(event.content);
        } else if (event.type === "done") {
          callbacks.onDone(event.conversation_id, event.full_text);
        } else if (event.type === "error") {
          callbacks.onError(event.message);
        }
      } catch {
        // Ignore malformed frames rather than crashing the stream.
      }
    }
  }
}
