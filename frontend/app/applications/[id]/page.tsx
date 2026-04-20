"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  getApplication,
  getApplicationDocuments,
  getApplicationExperience,
  saveAndGenerate,
  type ApplicationRecordWithJobInfo,
  type ApplicationExperienceResponse,
  type ExperienceItemWithSelection,
} from "@/lib/api";

const USERNAME = "alice";

type DocTab = "resume" | "cover_letter";
type ActionStatus = "idle" | "saving" | "done" | "error";

const EXP_TYPE_LABELS: Record<string, string> = {
  general: "General",
  job: "Job Experience",
  project: "Projects",
  volunteer: "Volunteer",
};

function formatDate(date: string | null | undefined): string {
  if (!date) return "";
  return date;
}

function ExperienceGroup({
  label,
  items,
  selectedIds,
  onToggle,
}: {
  label: string;
  items: ExperienceItemWithSelection[];
  selectedIds: Set<string>;
  onToggle: (id: string) => void;
}) {
  if (items.length === 0) return null;
  return (
    <div className="mb-4">
      <h3 className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-gray-500">
        {label}
      </h3>
      <div className="space-y-1">
        {items.map((item) => {
          const displayName =
            item.title ??
            (item.company ? `${item.title ?? ""} at ${item.company}` : "") ??
            item.name ??
            item.id;
          const dates = [formatDate(item.start_date), formatDate(item.end_date)]
            .filter(Boolean)
            .join(" – ");
          return (
            <label
              key={item.id}
              className="flex cursor-pointer items-start gap-2 rounded-lg px-2 py-1.5 hover:bg-gray-50"
            >
              <input
                type="checkbox"
                checked={selectedIds.has(item.id)}
                onChange={() => onToggle(item.id)}
                className="mt-0.5 h-4 w-4 shrink-0 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <span className="text-sm text-gray-800">
                {displayName}
                {dates && (
                  <span className="ml-1.5 text-xs text-gray-400">{dates}</span>
                )}
              </span>
            </label>
          );
        })}
      </div>
    </div>
  );
}

function markdownToHtml(md: string): string {
  return md
    .replace(/^### (.+)$/gm, "<h3>$1</h3>")
    .replace(/^## (.+)$/gm, "<h2>$1</h2>")
    .replace(/^# (.+)$/gm, "<h1>$1</h1>")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/^- (.+)$/gm, "<li>$1</li>")
    .replace(/(<li>.*<\/li>)/gs, "<ul>$1</ul>")
    .replace(/\n\n/g, "</p><p>")
    .replace(/^(?!<[hul])/gm, "")
    .replace(/^(.+)$/gm, (line) =>
      line.startsWith("<") ? line : `<p>${line}</p>`
    );
}

export default function ApplicationDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const router = useRouter();
  const appId = params.id;

  const [app, setApp] = useState<ApplicationRecordWithJobInfo | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  // Job info form state
  const [title, setTitle] = useState("");
  const [company, setCompany] = useState("");
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [jobDescription, setJobDescription] = useState("");

  // Experience selection
  const [experienceData, setExperienceData] =
    useState<ApplicationExperienceResponse | null>(null);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  // Changes prompt
  const [changesPrompt, setChangesPrompt] = useState("");

  // Generate checkboxes
  const [genResume, setGenResume] = useState(false);
  const [genCoverLetter, setGenCoverLetter] = useState(false);

  // Document content
  const [resumeMarkdown, setResumeMarkdown] = useState("");
  const [coverLetterMarkdown, setCoverLetterMarkdown] = useState("");
  const [activeTab, setActiveTab] = useState<DocTab>("resume");

  // Action state
  const [actionStatus, setActionStatus] = useState<ActionStatus>("idle");
  const [actionError, setActionError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      getApplication(appId),
      getApplicationDocuments(appId),
      getApplicationExperience(appId),
    ])
      .then(([appData, docs, exp]) => {
        setApp(appData);
        setTitle(appData.title);
        setCompany(appData.company);
        setWebsiteUrl(appData.website_url || "");
        setJobDescription(appData.job_description || "");

        setResumeMarkdown(docs.resume_markdown);
        setCoverLetterMarkdown(docs.cover_letter_markdown);
        if (docs.resume_markdown) setActiveTab("resume");
        else if (docs.cover_letter_markdown) setActiveTab("cover_letter");

        setExperienceData(exp);
        const preSelected = new Set<string>([
          ...exp.experience.filter((e) => e.selected).map((e) => e.id),
          ...exp.jobs.filter((j) => j.selected).map((j) => j.id),
          ...exp.skills.filter((s) => s.selected).map((s) => s.id),
        ]);
        setSelectedIds(preSelected);
      })
      .catch((e) => setLoadError(e.message));
  }, [appId]);

  function toggleId(id: string) {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }

  async function handleSaveAndGenerate() {
    setActionStatus("saving");
    setActionError(null);
    try {
      const result = await saveAndGenerate(appId, {
        username: USERNAME,
        selected_experience_ids: Array.from(selectedIds),
        changes_prompt: changesPrompt.trim() || undefined,
        generate_resume: genResume,
        generate_cover_letter: genCoverLetter,
        title,
        company,
        website_url: websiteUrl || undefined,
        job_description: jobDescription,
      });
      if (result.resume_markdown) {
        setResumeMarkdown(result.resume_markdown);
      }
      if (result.cover_letter_markdown) {
        setCoverLetterMarkdown(result.cover_letter_markdown);
      }
      if (genResume && result.resume_markdown) setActiveTab("resume");
      else if (genCoverLetter && result.cover_letter_markdown)
        setActiveTab("cover_letter");
      setActionStatus("done");
      setTimeout(() => setActionStatus("idle"), 3000);
    } catch (e) {
      setActionError(e instanceof Error ? e.message : "Action failed.");
      setActionStatus("error");
    }
  }

  const activeMarkdown =
    activeTab === "resume" ? resumeMarkdown : coverLetterMarkdown;

  const isGenerating = actionStatus === "saving" && (genResume || genCoverLetter);
  const buttonLabel = actionStatus === "saving"
    ? isGenerating ? "Generating… (60–90s)" : "Saving…"
    : genResume || genCoverLetter
    ? "Save & Generate"
    : "Save Changes";

  if (loadError) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-sm text-red-700">
        {loadError}
      </div>
    );
  }

  if (!app) {
    return (
      <div className="flex h-[calc(100vh-8rem)] items-center justify-center text-sm text-gray-400">
        Loading…
      </div>
    );
  }

  // Group experience items by type
  const expByType: Record<string, ExperienceItemWithSelection[]> = {};
  for (const item of experienceData?.experience ?? []) {
    const t = item.type ?? "general";
    if (!expByType[t]) expByType[t] = [];
    expByType[t].push(item);
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4">
      {/* Left panel */}
      <div className="flex w-1/2 flex-col gap-4 overflow-y-auto pb-4">
        {/* Back + title */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.push("/applications")}
            className="rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50"
          >
            ← Back
          </button>
          <h1 className="truncate text-lg font-bold text-gray-900">
            {app.title}{" "}
            <span className="font-normal text-gray-400">at {app.company}</span>
          </h1>
        </div>

        {/* Job info */}
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <h2 className="mb-3 text-sm font-semibold text-gray-700">Job Info</h2>
          <div className="space-y-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-600">
                Role / Job Title
              </label>
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-600">
                Company
              </label>
              <input
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-600">
                Company Website
              </label>
              <input
                value={websiteUrl}
                onChange={(e) => setWebsiteUrl(e.target.value)}
                type="url"
                placeholder="https://…"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-600">
                Job Description
              </label>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                rows={8}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>
        </div>

        {/* Experience */}
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <h2 className="mb-3 text-sm font-semibold text-gray-700">
            Experience
            <span className="ml-1.5 text-xs font-normal text-gray-400">
              (checked items will be used for document generation)
            </span>
          </h2>

          {!experienceData ? (
            <p className="text-sm text-gray-400">Loading…</p>
          ) : (
            <>
              {/* Experience entries by type */}
              {Object.entries(EXP_TYPE_LABELS).map(([typeKey, typeLabel]) => (
                <ExperienceGroup
                  key={typeKey}
                  label={typeLabel}
                  items={expByType[typeKey] ?? []}
                  selectedIds={selectedIds}
                  onToggle={toggleId}
                />
              ))}

              {/* Jobs table */}
              <ExperienceGroup
                label="Job Records"
                items={experienceData.jobs.map((j) => ({
                  ...j,
                  title: j.company ? `${j.title} at ${j.company}` : j.title,
                }))}
                selectedIds={selectedIds}
                onToggle={toggleId}
              />

              {/* Skills */}
              <ExperienceGroup
                label="Skills"
                items={experienceData.skills.map((s) => ({
                  ...s,
                  title: s.proficiency
                    ? `${s.name} (${s.proficiency})`
                    : s.name,
                }))}
                selectedIds={selectedIds}
                onToggle={toggleId}
              />

              {experienceData.experience.length === 0 &&
                experienceData.jobs.length === 0 &&
                experienceData.skills.length === 0 && (
                  <p className="text-sm text-gray-400">
                    No experience entries found. Add experience from the{" "}
                    <button
                      onClick={() => router.push("/experience")}
                      className="text-indigo-600 hover:underline"
                    >
                      experience page
                    </button>
                    .
                  </p>
                )}
            </>
          )}
        </div>

        {/* Changes prompt */}
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <h2 className="mb-1 text-sm font-semibold text-gray-700">
            Requested Changes
          </h2>
          <p className="mb-2 text-xs text-gray-400">
            Describe any changes you'd like made to the generated documents.
          </p>
          <textarea
            value={changesPrompt}
            onChange={(e) => setChangesPrompt(e.target.value)}
            rows={4}
            placeholder="e.g. Make it more concise. Emphasize leadership experience."
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        {/* Action area */}
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <div className="mb-3 flex items-center gap-5">
            <label className="flex cursor-pointer items-center gap-2 text-sm text-gray-700">
              <input
                type="checkbox"
                checked={genResume}
                onChange={(e) => setGenResume(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              Resume
            </label>
            <label className="flex cursor-pointer items-center gap-2 text-sm text-gray-700">
              <input
                type="checkbox"
                checked={genCoverLetter}
                onChange={(e) => setGenCoverLetter(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              Cover Letter
            </label>
          </div>
          <button
            onClick={handleSaveAndGenerate}
            disabled={actionStatus === "saving"}
            className="w-full rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {buttonLabel}
          </button>
          {actionStatus === "done" && (
            <p className="mt-2 text-xs text-green-600">Saved successfully.</p>
          )}
          {actionStatus === "error" && actionError && (
            <p className="mt-2 text-xs text-red-600">{actionError}</p>
          )}
          {actionStatus === "saving" && isGenerating && (
            <p className="mt-2 text-xs text-amber-700">
              This includes research and LLM generation. Please wait…
            </p>
          )}
        </div>
      </div>

      {/* Right panel — document preview */}
      <div className="flex w-1/2 flex-col rounded-xl border border-gray-200 bg-white">
        {/* Tab switcher */}
        <div className="flex gap-2 border-b border-gray-200 px-5 py-3">
          <button
            onClick={() => setActiveTab("resume")}
            className={`rounded-md px-3 py-1.5 text-xs font-semibold transition-colors ${
              activeTab === "resume"
                ? "bg-indigo-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            Resume
          </button>
          <button
            onClick={() => setActiveTab("cover_letter")}
            className={`rounded-md px-3 py-1.5 text-xs font-semibold transition-colors ${
              activeTab === "cover_letter"
                ? "bg-indigo-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            Cover Letter
          </button>
        </div>

        {/* Document content */}
        <div className="flex-1 overflow-y-auto p-5">
          {activeMarkdown ? (
            <div
              className="prose prose-sm max-w-none text-gray-800"
              dangerouslySetInnerHTML={{ __html: markdownToHtml(activeMarkdown) }}
            />
          ) : (
            <div className="flex h-full items-center justify-center">
              <p className="text-center text-sm text-gray-400">
                {activeTab === "resume"
                  ? "No resume generated yet. Check \"Resume\" below and click \"Save & Generate\"."
                  : "No cover letter generated yet. Check \"Cover Letter\" below and click \"Save & Generate\"."}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
