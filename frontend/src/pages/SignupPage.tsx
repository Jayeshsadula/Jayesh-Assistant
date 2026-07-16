import { FormEvent, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { Sparkles } from "lucide-react";

import { useAuthStore } from "@/store/authStore";

export default function SignupPage() {
  const { user, signup, error, clearError } = useAuthStore();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (user) return <Navigate to="/" replace />;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    clearError();
    try {
      await signup(email, password);
      navigate("/");
    } catch {
      // error surfaced via store
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-panel dark:bg-panel-dark px-4">
      <div className="w-full max-w-sm rounded-2xl border border-border dark:border-border-dark bg-surface dark:bg-surface-dark p-8 shadow-sm animate-fade-in">
        <div className="mb-6 flex flex-col items-center gap-2 text-center">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-accent text-white">
            <Sparkles size={20} />
          </div>
          <h1 className="text-lg font-semibold">Create your account</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Get started with JAYESH Assistant
          </p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <input
            type="email"
            required
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="rounded-lg border border-border dark:border-border-dark bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-accent"
          />
          <input
            type="password"
            required
            minLength={6}
            placeholder="Password (min. 6 characters)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="rounded-lg border border-border dark:border-border-dark bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-accent"
          />
          {error && <p className="text-sm text-red-500">{error}</p>}
          <button
            type="submit"
            disabled={isSubmitting}
            className="mt-2 rounded-lg bg-accent px-3 py-2 text-sm font-medium text-white transition hover:bg-accent-hover disabled:opacity-60"
          >
            {isSubmitting ? "Creating account…" : "Sign up"}
          </button>
        </form>

        <p className="mt-5 text-center text-sm text-gray-500 dark:text-gray-400">
          Already have an account?{" "}
          <a href="/login" className="font-medium text-accent hover:text-accent-hover">
            Sign in
          </a>
        </p>
      </div>
    </div>
  );
}
