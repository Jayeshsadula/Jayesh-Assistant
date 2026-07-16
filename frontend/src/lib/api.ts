import { auth } from "@/lib/firebase";
import type { ApiErrorBody } from "@/types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string;

export class ApiError extends Error {
  code: string;
  status: number;
  details: Record<string, unknown>;

  constructor(status: number, body: ApiErrorBody) {
    super(body.error.message);
    this.code = body.error.code;
    this.status = status;
    this.details = body.error.details;
  }
}

async function getAuthHeader(): Promise<Record<string, string>> {
  const user = auth.currentUser;
  if (!user) return {};
  const token = await user.getIdToken();
  return { Authorization: `Bearer ${token}` };
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let body: ApiErrorBody;
    try {
      body = await response.json();
    } catch {
      body = { error: { code: "unknown_error", message: response.statusText, details: {} } };
    }
    throw new ApiError(response.status, body);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const authHeader = await getAuthHeader();
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...authHeader,
      ...(options.headers || {}),
    },
  });
  return handleResponse<T>(response);
}

export const api = {
  get: <T>(path: string) => request<T>(path, { method: "GET" }),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PATCH", body: body ? JSON.stringify(body) : undefined }),
  put: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PUT", body: body ? JSON.stringify(body) : undefined }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),

  /** Multipart upload (used for document uploads); does not set Content-Type manually. */
  upload: async <T>(path: string, formData: FormData): Promise<T> => {
    const authHeader = await getAuthHeader();
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: { ...authHeader },
      body: formData,
    });
    return handleResponse<T>(response);
  },

  /** Returns the base URL + auth header, for use by the raw SSE fetch in the chat store. */
  getStreamConfig: async (path: string) => ({
    url: `${API_BASE_URL}${path}`,
    headers: {
      "Content-Type": "application/json",
      ...(await getAuthHeader()),
    },
  }),
};
