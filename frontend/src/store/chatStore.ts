import { create } from "zustand";

import { api } from "@/lib/api";
import { streamChat } from "@/lib/streamChat";
import type { ConversationPublic, MessagePublic, ModelName } from "@/types";

interface ChatState {
  conversations: ConversationPublic[];
  activeConversationId: string | null;
  messages: MessagePublic[];
  isStreaming: boolean;
  streamingText: string;
  searchQuery: string;
  abortController: AbortController | null;

  loadConversations: () => Promise<void>;
  selectConversation: (conversationId: string) => Promise<void>;
  startNewChat: () => void;
  renameConversation: (conversationId: string, title: string) => Promise<void>;
  deleteConversation: (conversationId: string) => Promise<void>;
  setSearchQuery: (query: string) => void;

  sendMessage: (
    content: string,
    model: ModelName,
    useMemory: boolean,
    useRag: boolean,
    documentIds: string[]
  ) => Promise<void>;
  stopStreaming: () => void;
  regenerateLast: (model: ModelName, useMemory: boolean, useRag: boolean, documentIds: string[]) => Promise<void>;
}

function tempMessage(role: "user" | "assistant", content: string): MessagePublic {
  return {
    message_id: `temp-${Date.now()}-${Math.random().toString(36).slice(2)}`,
    role,
    content,
    created_at: new Date().toISOString(),
  };
}

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: [],
  activeConversationId: null,
  messages: [],
  isStreaming: false,
  streamingText: "",
  searchQuery: "",
  abortController: null,

  loadConversations: async () => {
    const search = get().searchQuery || undefined;
    const conversations = await api.get<ConversationPublic[]>(
      `/conversations${search ? `?search=${encodeURIComponent(search)}` : ""}`
    );
    set({ conversations });
  },

  selectConversation: async (conversationId) => {
    const messages = await api.get<MessagePublic[]>(`/conversations/${conversationId}/messages`);
    set({ activeConversationId: conversationId, messages, streamingText: "" });
  },

  startNewChat: () => {
    set({ activeConversationId: null, messages: [], streamingText: "" });
  },

  renameConversation: async (conversationId, title) => {
    await api.patch(`/conversations/${conversationId}`, { title });
    await get().loadConversations();
  },

  deleteConversation: async (conversationId) => {
    await api.delete(`/conversations/${conversationId}`);
    if (get().activeConversationId === conversationId) {
      set({ activeConversationId: null, messages: [] });
    }
    await get().loadConversations();
  },

  setSearchQuery: (query) => set({ searchQuery: query }),

  sendMessage: async (content, model, useMemory, useRag, documentIds) => {
    const userMsg = tempMessage("user", content);
    set((state) => ({
      messages: [...state.messages, userMsg],
      isStreaming: true,
      streamingText: "",
    }));

    const controller = new AbortController();
    set({ abortController: controller });

    await streamChat(
      {
        conversation_id: get().activeConversationId,
        message: content,
        model,
        use_memory: useMemory,
        use_rag: useRag,
        document_ids: documentIds,
      },
      {
        onToken: (token) => {
          set((state) => ({ streamingText: state.streamingText + token }));
        },
        onDone: (conversationId, fullText) => {
          const assistantMsg = tempMessage("assistant", fullText);
          set((state) => ({
            activeConversationId: conversationId,
            messages: [...state.messages, assistantMsg],
            isStreaming: false,
            streamingText: "",
            abortController: null,
          }));
          get().loadConversations();
        },
        onError: (message) => {
          const errorMsg = tempMessage("assistant", `⚠️ ${message}`);
          set((state) => ({
            messages: [...state.messages, errorMsg],
            isStreaming: false,
            streamingText: "",
            abortController: null,
          }));
        },
      },
      controller.signal
    );
  },

  stopStreaming: () => {
    const { abortController, streamingText } = get();
    abortController?.abort();
    if (streamingText) {
      const partialMsg = tempMessage("assistant", streamingText + " _(stopped)_");
      set((state) => ({
        messages: [...state.messages, partialMsg],
        isStreaming: false,
        streamingText: "",
        abortController: null,
      }));
    } else {
      set({ isStreaming: false, streamingText: "", abortController: null });
    }
  },

  regenerateLast: async (model, useMemory, useRag, documentIds) => {
    const { messages } = get();
    const lastUserMessage = [...messages].reverse().find((m) => m.role === "user");
    if (!lastUserMessage) return;

    // Drop the last assistant reply before regenerating.
    set((state) => ({
      messages:
        state.messages[state.messages.length - 1]?.role === "assistant"
          ? state.messages.slice(0, -1)
          : state.messages,
    }));

    await get().sendMessage(lastUserMessage.content, model, useMemory, useRag, documentIds);
  },
}));
