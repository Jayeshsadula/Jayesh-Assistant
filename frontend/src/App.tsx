import { useEffect } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import ChatPage from "@/pages/ChatPage";
import LoginPage from "@/pages/LoginPage";
import SettingsPage from "@/pages/SettingsPage";
import SignupPage from "@/pages/SignupPage";
import ProtectedRoute from "@/routes/ProtectedRoute";
import { useAuthStore } from "@/store/authStore";
import { useSettingsStore } from "@/store/settingsStore";

export default function App() {
  const initAuthListener = useAuthStore((state) => state.initAuthListener);
  const user = useAuthStore((state) => state.user);
  const loadSettings = useSettingsStore((state) => state.loadSettings);
  const isSettingsLoaded = useSettingsStore((state) => state.isLoaded);

  useEffect(() => {
    initAuthListener();
  }, [initAuthListener]);

  useEffect(() => {
    if (user && !isSettingsLoaded) {
      loadSettings();
    }
  }, [user, isSettingsLoaded, loadSettings]);

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <ChatPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <SettingsPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
