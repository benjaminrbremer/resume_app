"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createApplication } from "@/lib/api";

const USERNAME = "alice";

export default function NewApplicationPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    title: "",
    company: "",
    website_url: "",
    job_description: "",
  });
  const [generateResume, setGenerateResume] = useState(false);
  const [generateCoverLetter, setGenerateCoverLetter] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.title.trim() || !form.company.trim()) {
      setError("Role and company are required.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const app = await createApplication(USERNAME, {
        title: form.title.trim(),
        company: form.company.trim(),
        website_url: form.website_url.trim() || undefined,
        job_description: form.job_description.trim() || undefined,
        generate_resume: generateResume,
        generate_cover_letter: generateCoverLetter,
      });
      router.push(`/applications/${app.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create application.");
      setSaving(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-6 flex items-center gap-3">
        <button
          onClick={() => router.push("/applications")}
          className="rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50"
        >
          ← Back
        </button>
        <h1 className="text-2xl font-bold text-gray-900">New Application</h1>
      </div>

      <form onSubmit={handleSubmit} className="rounded-xl border border-gray-200 bg-white p-6">
        {error && (
          <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Role / Job Title <span className="text-red-500">*</span>
            </label>
            <input
              name="title"
              value={form.title}
              onChange={handleChange}
              placeholder="e.g. Senior Software Engineer"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Company <span className="text-red-500">*</span>
            </label>
            <input
              name="company"
              value={form.company}
              onChange={handleChange}
              placeholder="e.g. Acme Corp"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Company Website
              <span className="ml-1 text-xs font-normal text-gray-400">(used for research)</span>
            </label>
            <input
              name="website_url"
              value={form.website_url}
              onChange={handleChange}
              placeholder="e.g. https://acme.com"
              type="url"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Job Description
            </label>
            <textarea
              name="job_description"
              value={form.job_description}
              onChange={handleChange}
              rows={10}
              placeholder="Paste the full job description here…"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <p className="mb-2 text-sm font-medium text-gray-700">
              Document Generation
              <span className="ml-1 text-xs font-normal text-gray-400">(optional — can also be done from the application page)</span>
            </p>
            <div className="flex gap-6">
              <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={generateResume}
                  onChange={(e) => setGenerateResume(e.target.checked)}
                  className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                Generate Resume
              </label>
              <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={generateCoverLetter}
                  onChange={(e) => setGenerateCoverLetter(e.target.checked)}
                  className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                Generate Cover Letter
              </label>
            </div>
          </div>
        </div>

        {saving && (generateResume || generateCoverLetter) && (
          <div className="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
            Creating application and generating documents… this can take 60–90 seconds.
          </div>
        )}

        <div className="mt-6 flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="rounded-lg bg-indigo-600 px-5 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving && !(generateResume || generateCoverLetter) ? "Creating…" : saving ? "Creating…" : "Create Application →"}
          </button>
        </div>
      </form>
    </div>
  );
}
