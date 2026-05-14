"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getUsername, clearUsername } from "@/lib/auth";

export default function NavClient() {
  const router = useRouter();
  const [username, setUsernameState] = useState<string | null>(null);

  useEffect(() => {
    setUsernameState(getUsername());
  }, []);

  function handleLogout() {
    clearUsername();
    router.push("/login");
  }

  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-14 items-center gap-8">
          <a href="/" className="text-lg font-semibold text-indigo-600">
            ResumeApp
          </a>
          <a href="/experience" className="text-sm font-medium text-gray-600 hover:text-gray-900">
            Experience
          </a>
          <a href="/example-documents" className="text-sm font-medium text-gray-600 hover:text-gray-900">
            Documents
          </a>
          <a href="/applications" className="text-sm font-medium text-gray-600 hover:text-gray-900">
            Applications
          </a>

          {username && (
            <div className="ml-auto flex items-center gap-4">
              <span className="text-sm text-gray-500">{username}</span>
              <button
                onClick={handleLogout}
                className="rounded-lg border border-gray-200 px-3 py-1.5 text-xs font-semibold text-gray-600 hover:bg-gray-50"
              >
                Log out
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
