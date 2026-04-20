"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { listApplications, type ApplicationRecord } from "@/lib/api";

const USERNAME = "alice";

export default function ApplicationsPage() {
  const router = useRouter();
  const [applications, setApplications] = useState<ApplicationRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listApplications(USERNAME)
      .then(setApplications)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Applications</h1>
          <p className="mt-1 text-sm text-gray-500">
            Track your job applications and generate tailored documents.
          </p>
        </div>
        <button
          onClick={() => router.push("/applications/new")}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
        >
          New Application
        </button>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <div className="rounded-xl border border-gray-200 bg-white p-12 text-center">
          <p className="text-sm text-gray-400">Loading…</p>
        </div>
      ) : applications.length === 0 ? (
        <div className="rounded-xl border border-dashed border-gray-300 bg-white p-12 text-center">
          <p className="text-sm text-gray-400">No applications yet.</p>
          <p className="mt-1 text-xs text-gray-300">Click "New Application" to get started.</p>
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">
          {applications.map((app, idx) => (
            <button
              key={app.id}
              onClick={() => router.push(`/applications/${app.id}`)}
              className={`flex w-full items-center justify-between px-5 py-4 text-left hover:bg-gray-50 ${
                idx < applications.length - 1 ? "border-b border-gray-100" : ""
              }`}
            >
              <div>
                <p className="text-sm font-semibold text-gray-900">{app.title}</p>
                <p className="mt-0.5 text-xs text-gray-500">{app.company}</p>
              </div>
              <div className="flex items-center gap-3">
                {app.outcome && (
                  <span className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600">
                    {app.outcome}
                  </span>
                )}
                <span className="text-xs text-gray-400">
                  {new Date(app.started_dt).toLocaleDateString()}
                </span>
                <span className="text-gray-300">›</span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
