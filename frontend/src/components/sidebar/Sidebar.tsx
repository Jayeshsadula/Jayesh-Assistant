import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { LogOut, MessageSquare, Pencil, Plus, Search, Settings, Trash2 } from "lucide-react";

import { cn } from "@/lib/cn";
import { useAuthStore } from "@/store/authStore";
import { useChatStore } from "@/store/chatStore";

export default function Sidebar() {
  const navigate = useNavigate();
  const { logout } = useAuthStore();
  const {
    conversations,
    activeConversationId,
    searchQuery,
    loadConversations,
    selectConversation,
    startNewChat,
    renameConversation,
    deleteConversation,
    setSearchQuery,
  } = useChatStore();

  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState("");

  useEffect(() => {
    loadConversations();
  }, [searchQuery]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleNewChat = () => {
    startNewChat();
  };

  const handleRenameSubmit = async (conversationId: string) => {
    if (renameValue.trim()) {
      await renameConversation(conversationId, renameValue.trim());
    }
    setRenamingId(null);
  };

  return (
    <aside className="flex h-full w-72 shrink-0 flex-col border-r border-border dark:border-border-dark bg-panel dark:bg-panel-dark">
      <div className="p-3">
        <button
          onClick={handleNewChat}
          className="flex w-full items-center gap-2 rounded-lg border border-border dark:border-border-dark px-3 py-2 text-sm font-medium transition hover:bg-surface dark:hover:bg-surface-dark"
        >
          <Plus size={16} />
          New Chat
        </button>
      </div>

      <div className="px-3 pb-2">
        <div className="flex items-center gap-2 rounded-lg border border-border dark:border-border-dark px-2.5 py-1.5">
          <Search size={14} className="text-gray-400 shrink-0" />
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search chats"
            className="w-full bg-transparent text-sm outline-none placeholder:text-gray-400"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-2">
        {conversations.map((conv) => (
          <div
            key={conv.conversation_id}
            className={cn(
              "group flex items-center gap-2 rounded-lg px-2.5 py-2 text-sm cursor-pointer transition",
              activeConversationId === conv.conversation_id
                ? "bg-surface dark:bg-surface-dark"
                : "hover:bg-surface/60 dark:hover:bg-surface-dark/60"
            )}
            onClick={() => selectConversation(conv.conversation_id)}
          >
            <MessageSquare size={15} className="shrink-0 text-gray-400" />
            {renamingId === conv.conversation_id ? (
              <input
                autoFocus
                value={renameValue}
                onChange={(e) => setRenameValue(e.target.value)}
                onBlur={() => handleRenameSubmit(conv.conversation_id)}
                onKeyDown={(e) => e.key === "Enter" && handleRenameSubmit(conv.conversation_id)}
                onClick={(e) => e.stopPropagation()}
                className="w-full bg-transparent text-sm outline-none"
              />
            ) : (
              <span className="flex-1 truncate">{conv.title}</span>
            )}

            <div className="hidden shrink-0 gap-1 group-hover:flex">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setRenamingId(conv.conversation_id);
                  setRenameValue(conv.title);
                }}
                className="rounded p-1 hover:bg-border dark:hover:bg-border-dark"
                title="Rename"
              >
                <Pencil size={13} />
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  deleteConversation(conv.conversation_id);
                }}
                className="rounded p-1 hover:bg-border dark:hover:bg-border-dark"
                title="Delete"
              >
                <Trash2 size={13} />
              </button>
            </div>
          </div>
        ))}

        {conversations.length === 0 && (
          <p className="px-2.5 py-4 text-center text-xs text-gray-400">No conversations yet</p>
        )}
      </div>

      <div className="border-t border-border dark:border-border-dark p-2">
        <button
          onClick={() => navigate("/settings")}
          className="flex w-full items-center gap-2 rounded-lg px-2.5 py-2 text-sm transition hover:bg-surface dark:hover:bg-surface-dark"
        >
          <Settings size={15} />
          Settings
        </button>
        <button
          onClick={logout}
          className="flex w-full items-center gap-2 rounded-lg px-2.5 py-2 text-sm text-red-500 transition hover:bg-surface dark:hover:bg-surface-dark"
        >
          <LogOut size={15} />
          Log out
        </button>
      </div>
    </aside>
  );
}
