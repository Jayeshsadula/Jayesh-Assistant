import { useEffect } from "react";

import ChatInput from "@/components/chat/ChatInput";
import ChatWindow from "@/components/chat/ChatWindow";
import Sidebar from "@/components/sidebar/Sidebar";
import { useChatStore } from "@/store/chatStore";

export default function ChatPage() {
  const loadConversations = useChatStore((state) => state.loadConversations);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-surface dark:bg-surface-dark">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <ChatWindow />
        <ChatInput />
      </div>
    </div>
  );
}
