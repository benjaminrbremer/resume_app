"use client";

import { useEffect, useRef, useState } from "react";
import {
  ChatMessage,
  ExperienceRecord,
  deleteExperience,
  listExperience,
  sendExperienceChat,
} from "@/lib/api";

const USERNAME = "alice"; // temporary until session auth is implemented

const SEED_GREETING: ChatMessage = {
  role: "assistant",
  content:
    "Hi! I'm here to help you build your experience library. Tell me about your work history — you can start with your most recent job, a project you're proud of, or any skills you'd like to highlight.",
};

const TYPE_BADGE: Record<string, string> = {
  general: "bg-gray-100 text-gray-700",
  job_project: "bg-blue-100 text-blue-700",
  personal: "bg-green-100 text-green-700",
};

const TYPE_LABEL: Record<string, string> = {
  general: "General",
  job_project: "Job / Project",
  personal: "Personal",
};

export default function ExperiencePage() {
  const [experiences, setExperiences] = useState<ExperienceRecord[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([SEED_GREETING]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  async function loadExperiences() {
    try {
      const data = await listExperience(USERNAME);
      setExperiences(data);
    } catch {
      // silently fail on list refresh — not worth blocking the UI
    }
  }

  useEffect(() => {
    loadExperiences();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  async function handleSend() {
    const text = inputValue.trim();
    if (!text || isLoading) return;

    const userMsg: ChatMessage = { role: "user", content: text };
    const nextMessages = [...messages, userMsg];
    setMessages(nextMessages);
    setInputValue("");
    setIsLoading(true);
    setError(null);

    // history excludes the seed greeting (index 0) and the current user message (last item)
    // — the agent appends user_message itself, so sending it in history would duplicate it
    const history = nextMessages.slice(1, -1);

    try {
      const reply = await sendExperienceChat(USERNAME, text, history);
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
      await loadExperiences();
    } catch (err) {
      setError("Something went wrong. Please try again.");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleDelete(expId: string) {
    try {
      await deleteExperience(expId);
      await loadExperiences();
    } catch {
      setError("Failed to delete entry. Please try again.");
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4">
      {/* Left panel — experience list */}
      <div className="flex w-1/3 flex-col rounded-xl border border-gray-200 bg-white">
        <div className="border-b border-gray-200 px-4 py-3">
          <h2 className="text-sm font-semibold text-gray-700">Your Experience</h2>
        </div>
        <div className="flex-1 overflow-y-auto p-4">
          {experiences.length === 0 ? (
            <p className="text-sm text-gray-400">
              No entries yet — use the chat to add your experience.
            </p>
          ) : (
            <ul className="space-y-3">
              {experiences.map((exp) => (
                <li
                  key={exp.id}
                  className="rounded-lg border border-gray-200 p-3"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-gray-900">
                        {exp.title}
                      </p>
                      <div className="mt-1 flex flex-wrap items-center gap-2">
                        <span
                          className={`inline-block rounded px-1.5 py-0.5 text-xs font-medium ${
                            TYPE_BADGE[exp.type] ?? TYPE_BADGE.general
                          }`}
                        >
                          {TYPE_LABEL[exp.type] ?? exp.type}
                        </span>
                        {(exp.start_date || exp.end_date) && (
                          <span className="text-xs text-gray-500">
                            {exp.start_date ?? "?"} – {exp.end_date ?? "present"}
                          </span>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={() => handleDelete(exp.id)}
                      className="shrink-0 text-xs text-gray-400 hover:text-red-500"
                      aria-label={`Delete ${exp.title}`}
                    >
                      ✕
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Right panel — chat */}
      <div className="flex flex-1 flex-col rounded-xl border border-gray-200 bg-white">
        <div className="border-b border-gray-200 px-4 py-3">
          <h2 className="text-sm font-semibold text-gray-700">Experience Assistant</h2>
        </div>

        {/* Message thread */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="space-y-3">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm leading-relaxed ${
                    msg.role === "user"
                      ? "bg-indigo-600 text-white"
                      : "bg-gray-100 text-gray-800"
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}

            {/* Loading indicator */}
            {isLoading && (
              <div className="flex justify-start">
                <div className="rounded-2xl bg-gray-100 px-4 py-2 text-sm text-gray-500">
                  <span className="animate-pulse">···</span>
                </div>
              </div>
            )}

            {error && (
              <div className="flex justify-center">
                <p className="text-xs text-red-500">{error}</p>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input area */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex gap-3">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Describe your experience… (Enter to send, Shift+Enter for newline)"
              rows={2}
              disabled={isLoading}
              className="flex-1 resize-none rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-indigo-400 focus:outline-none disabled:opacity-50"
            />
            <button
              onClick={handleSend}
              disabled={isLoading || !inputValue.trim()}
              className="self-end rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-50"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
