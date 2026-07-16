export type MessageRole = "user" | "assistant" | "system" | "tool";

export type ModelName =
  | "qwen2.5:7b"
  | "llama3.1:8b"
  | "mistral:7b"
  | "gemma2:9b"
  | "deepseek-r1:7b";

export type ThemePreference = "light" | "dark" | "system";

export type MemoryType = "preference" | "interest" | "project" | "fact";

export type DocumentStatus = "processing" | "ready" | "failed";

export interface ConversationPublic {
  conversation_id: string;
  title: string;
  model: string;
  created_at: string;
  updated_at: string;
}

export interface MessagePublic {
  message_id: string;
  role: MessageRole;
  content: string;
  model_used?: string | null;
  created_at: string;
}

export interface MemoryPublic {
  memory_id: string;
  memory_type: MemoryType;
  content: string;
  created_at: string;
}

export interface DocumentPublic {
  document_id: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  status: DocumentStatus;
  chunk_count: number;
  uploaded_at: string;
}

export interface UserSettingsPublic {
  theme: ThemePreference;
  default_model: ModelName;
  memory_enabled: boolean;
  rag_enabled: boolean;
}

export interface ChatRequestPayload {
  conversation_id?: string | null;
  message: string;
  model: ModelName;
  use_memory: boolean;
  use_rag: boolean;
  document_ids: string[];
}

export interface ModelsResponse {
  configured_models: string[];
  pulled_models: string[];
  default_model: string;
  ready_models: string[];
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details: Record<string, unknown>;
  };
}
