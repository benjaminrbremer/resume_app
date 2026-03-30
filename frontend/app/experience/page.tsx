"use client";

import { useEffect, useState } from "react";
import {
  ExperienceFormData,
  ExperienceRecord,
  SkillFormData,
  SkillRecord,
  createExperience,
  createSkill,
  deleteExperience,
  deleteSkill,
  getExperience,
  getSkill,
  listExperience,
  listSkills,
  updateExperience,
  updateSkill,
} from "@/lib/api";

const USERNAME = "alice"; // temporary until session auth is implemented

const TYPE_BADGE: Record<string, string> = {
  general: "bg-gray-100 text-gray-700",
  job: "bg-blue-100 text-blue-700",
  project: "bg-purple-100 text-purple-700",
  volunteer: "bg-green-100 text-green-700",
};

const TYPE_LABEL: Record<string, string> = {
  general: "General",
  job: "Job",
  project: "Project",
  volunteer: "Volunteer",
};

const DATE_RE = /^\d{4}-(0[1-9]|1[0-2])$/;

type Tab = "jobs" | "projects" | "skills" | "other";
type FormMode = "idle" | "new" | "editing";

// Which experience types belong to each tab
const TAB_TYPES: Record<Exclude<Tab, "skills">, ExperienceFormData["type"][]> = {
  jobs: ["job"],
  projects: ["project"],
  other: ["general", "volunteer"],
};

// Default type when creating a new entry in each experience tab
const TAB_DEFAULT_TYPE: Record<Exclude<Tab, "skills">, ExperienceFormData["type"]> = {
  jobs: "job",
  projects: "project",
  other: "general",
};

const TAB_LABELS: Record<Tab, string> = {
  jobs: "Jobs",
  projects: "Projects",
  skills: "Skills",
  other: "Other",
};

export default function ExperiencePage() {
  const [activeTab, setActiveTab] = useState<Tab>("jobs");

  // List data
  const [experiences, setExperiences] = useState<ExperienceRecord[]>([]);
  const [skills, setSkills] = useState<SkillRecord[]>([]);

  // Shared form state
  const [formMode, setFormMode] = useState<FormMode>("idle");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoadingForm, setIsLoadingForm] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // Experience form fields
  const [expTitle, setExpTitle] = useState("");
  const [expType, setExpType] = useState<ExperienceFormData["type"]>("job");
  const [expStartDate, setExpStartDate] = useState("");
  const [expEndDate, setExpEndDate] = useState("");
  const [expContent, setExpContent] = useState("");

  // Skill form fields
  const [skillName, setSkillName] = useState("");
  const [skillProficiency, setSkillProficiency] = useState("");
  const [skillContent, setSkillContent] = useState("");

  async function loadExperiences() {
    try {
      setExperiences(await listExperience(USERNAME));
    } catch {
      // silently fail
    }
  }

  async function loadSkills() {
    try {
      setSkills(await listSkills(USERNAME));
    } catch {
      // silently fail
    }
  }

  useEffect(() => {
    loadExperiences();
    loadSkills();
  }, []);

  function handleTabChange(tab: Tab) {
    setActiveTab(tab);
    handleCancel();
  }

  // -------------------------------------------------------------------------
  // Shared form actions
  // -------------------------------------------------------------------------

  function handleNew() {
    setSelectedId(null);
    setFormMode("new");
    setFormErrors({});
    setSaveError(null);
    if (activeTab === "skills") {
      setSkillName("");
      setSkillProficiency("");
      setSkillContent("");
    } else {
      const defaultType = TAB_DEFAULT_TYPE[activeTab];
      setExpTitle("");
      setExpType(defaultType);
      setExpStartDate("");
      setExpEndDate("");
      setExpContent("");
    }
  }

  function handleCancel() {
    setFormMode("idle");
    setSelectedId(null);
    setFormErrors({});
    setSaveError(null);
  }

  // -------------------------------------------------------------------------
  // Experience actions
  // -------------------------------------------------------------------------

  async function handleSelectExperience(expId: string) {
    setSelectedId(expId);
    setFormMode("editing");
    setFormErrors({});
    setSaveError(null);
    setIsLoadingForm(true);
    try {
      const record = await getExperience(expId);
      setExpTitle(record.title);
      setExpType(record.type);
      setExpStartDate(record.start_date ?? "");
      setExpEndDate(record.end_date ?? "");
      setExpContent(record.content ?? "");
    } catch {
      setSaveError("Failed to load details.");
    } finally {
      setIsLoadingForm(false);
    }
  }

  function validateExperienceForm(): boolean {
    const errors: Record<string, string> = {};
    if (!expTitle.trim()) errors.title = "Title is required.";
    if (expStartDate && !DATE_RE.test(expStartDate)) errors.start_date = "Use YYYY-MM format.";
    if (expEndDate && !DATE_RE.test(expEndDate)) errors.end_date = "Use YYYY-MM format.";

    const today = new Date().toISOString().slice(0, 7); // YYYY-MM

    if (expStartDate && DATE_RE.test(expStartDate) && expStartDate > today) {
      errors.start_date = "Start date cannot be in the future.";
    }
    if (expEndDate && DATE_RE.test(expEndDate)) {
      if (expEndDate > today) {
        errors.end_date = "End date cannot be in the future.";
      } else if (!expStartDate) {
        errors.start_date = "Start date is required when an end date is set.";
      } else if (DATE_RE.test(expStartDate) && expStartDate > expEndDate) {
        errors.end_date = "End date must be on or after the start date.";
      }
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleSaveExperience(e: React.FormEvent) {
    e.preventDefault();
    if (!validateExperienceForm()) return;
    setIsSaving(true);
    setSaveError(null);
    const payload: ExperienceFormData = {
      type: expType,
      title: expTitle.trim(),
      start_date: expStartDate,
      end_date: expEndDate,
      content: expContent,
    };
    try {
      if (formMode === "new") {
        await createExperience(USERNAME, payload);
      } else if (selectedId) {
        await updateExperience(selectedId, payload);
      }
      await loadExperiences();
      handleCancel();
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : "Failed to save. Please try again.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDeleteExperience(expId: string) {
    try {
      await deleteExperience(expId);
      if (selectedId === expId) handleCancel();
      await loadExperiences();
    } catch {
      setSaveError("Failed to delete. Please try again.");
    }
  }

  // -------------------------------------------------------------------------
  // Skill actions
  // -------------------------------------------------------------------------

  async function handleSelectSkill(skillId: string) {
    setSelectedId(skillId);
    setFormMode("editing");
    setFormErrors({});
    setSaveError(null);
    setIsLoadingForm(true);
    try {
      const record = await getSkill(skillId);
      setSkillName(record.name);
      setSkillProficiency(record.proficiency ?? "");
      setSkillContent(record.content ?? "");
    } catch {
      setSaveError("Failed to load skill details.");
    } finally {
      setIsLoadingForm(false);
    }
  }

  function validateSkillForm(): boolean {
    const errors: Record<string, string> = {};
    if (!skillName.trim()) errors.name = "Name is required.";
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleSaveSkill(e: React.FormEvent) {
    e.preventDefault();
    if (!validateSkillForm()) return;
    setIsSaving(true);
    setSaveError(null);
    const payload: SkillFormData = {
      name: skillName.trim(),
      proficiency: skillProficiency,
      content: skillContent,
    };
    try {
      if (formMode === "new") {
        await createSkill(USERNAME, payload);
      } else if (selectedId) {
        await updateSkill(selectedId, payload);
      }
      await loadSkills();
      handleCancel();
    } catch {
      setSaveError("Failed to save. Please try again.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDeleteSkill(skillId: string) {
    try {
      await deleteSkill(skillId);
      if (selectedId === skillId) handleCancel();
      await loadSkills();
    } catch {
      setSaveError("Failed to delete skill. Please try again.");
    }
  }

  // -------------------------------------------------------------------------
  // Derived list for current experience tab
  // -------------------------------------------------------------------------

  const visibleExperiences =
    activeTab === "skills"
      ? []
      : experiences.filter((e) => TAB_TYPES[activeTab].includes(e.type));

  // -------------------------------------------------------------------------
  // Form header label
  // -------------------------------------------------------------------------

  const editorLabel =
    formMode === "new"
      ? `New ${TAB_LABELS[activeTab].replace(/s$/, "")}`
      : formMode === "editing"
      ? `Edit ${TAB_LABELS[activeTab].replace(/s$/, "")}`
      : `${TAB_LABELS[activeTab].replace(/s$/, "")} Editor`;

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4">
      {/* Left panel */}
      <div className="flex w-1/3 flex-col rounded-xl border border-gray-200 bg-white">
        {/* Tab bar */}
        <div className="flex border-b border-gray-200">
          {(["jobs", "projects", "skills", "other"] as Tab[]).map((tab) => (
            <button
              key={tab}
              onClick={() => handleTabChange(tab)}
              className={`flex-1 py-2.5 text-xs font-semibold transition-colors ${
                activeTab === tab
                  ? "border-b-2 border-indigo-600 text-indigo-600"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              {TAB_LABELS[tab]}
            </button>
          ))}
        </div>

        {/* Sub-header with count + New button */}
        <div className="flex items-center justify-between border-b border-gray-200 px-4 py-2">
          <span className="text-xs text-gray-500">
            {activeTab === "skills"
              ? `${skills.length} skill${skills.length === 1 ? "" : "s"}`
              : `${visibleExperiences.length} entr${visibleExperiences.length === 1 ? "y" : "ies"}`}
          </span>
          <button
            onClick={handleNew}
            className="text-xs font-semibold text-indigo-600 hover:text-indigo-500"
          >
            + New
          </button>
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto p-3">
          {activeTab === "skills" ? (
            skills.length === 0 ? (
              <p className="text-sm text-gray-400">No skills yet — click + New to add your first.</p>
            ) : (
              <ul className="space-y-2">
                {skills.map((skill) => (
                  <li
                    key={skill.id}
                    onClick={() => handleSelectSkill(skill.id)}
                    className={`cursor-pointer rounded-lg border p-3 transition-colors ${
                      selectedId === skill.id
                        ? "border-indigo-300 bg-indigo-50"
                        : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium text-gray-900">{skill.name}</p>
                        {skill.proficiency && (
                          <p className="mt-0.5 truncate text-xs text-gray-500">{skill.proficiency}</p>
                        )}
                      </div>
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDeleteSkill(skill.id); }}
                        className="shrink-0 text-xs text-gray-400 hover:text-red-500"
                        aria-label={`Delete ${skill.name}`}
                      >
                        ✕
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            )
          ) : visibleExperiences.length === 0 ? (
            <p className="text-sm text-gray-400">
              No entries yet — click + New to add your first.
            </p>
          ) : (
            <ul className="space-y-2">
              {visibleExperiences.map((exp) => (
                <li
                  key={exp.id}
                  onClick={() => handleSelectExperience(exp.id)}
                  className={`cursor-pointer rounded-lg border p-3 transition-colors ${
                    selectedId === exp.id
                      ? "border-indigo-300 bg-indigo-50"
                      : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-gray-900">{exp.title}</p>
                      <div className="mt-1 flex flex-wrap items-center gap-2">
                        {/* Show type badge only on Other tab (mixed types) */}
                        {activeTab === "other" && (
                          <span
                            className={`inline-block rounded px-1.5 py-0.5 text-xs font-medium ${
                              TYPE_BADGE[exp.type] ?? TYPE_BADGE.general
                            }`}
                          >
                            {TYPE_LABEL[exp.type] ?? exp.type}
                          </span>
                        )}
                        {(exp.start_date || exp.end_date) && (
                          <span className="text-xs text-gray-500">
                            {exp.start_date ?? "?"} – {exp.end_date ?? "present"}
                          </span>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDeleteExperience(exp.id); }}
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

      {/* Right panel — form editor */}
      <div className="flex flex-1 flex-col rounded-xl border border-gray-200 bg-white">
        <div className="border-b border-gray-200 px-4 py-3">
          <h2 className="text-sm font-semibold text-gray-700">{editorLabel}</h2>
        </div>

        {formMode === "idle" ? (
          <div className="flex flex-1 items-center justify-center">
            <p className="text-sm text-gray-400">Select an entry to edit, or click + New.</p>
          </div>
        ) : isLoadingForm ? (
          <div className="flex flex-1 items-center justify-center">
            <p className="text-sm text-gray-400">Loading…</p>
          </div>
        ) : activeTab === "skills" ? (
          /* ---- Skill form ---- */
          <form onSubmit={handleSaveSkill} className="flex flex-1 flex-col gap-4 overflow-y-auto p-4">
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-700">
                Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={skillName}
                onChange={(e) => setSkillName(e.target.value)}
                placeholder="e.g. TypeScript"
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-indigo-400 focus:outline-none"
              />
              {formErrors.name && <p className="mt-1 text-xs text-red-500">{formErrors.name}</p>}
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-gray-700">Proficiency</label>
              <input
                type="text"
                value={skillProficiency}
                onChange={(e) => setSkillProficiency(e.target.value)}
                placeholder="e.g. Advanced, 5 years, Expert"
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-indigo-400 focus:outline-none"
              />
            </div>

            <div className="flex flex-1 flex-col">
              <label className="mb-1 block text-xs font-medium text-gray-700">Notes</label>
              <textarea
                value={skillContent}
                onChange={(e) => setSkillContent(e.target.value)}
                placeholder="Additional context about this skill…"
                rows={8}
                className="flex-1 resize-none rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-indigo-400 focus:outline-none"
              />
            </div>

            {saveError && <p className="text-xs text-red-500">{saveError}</p>}
            <FormActions
              formMode={formMode}
              selectedId={selectedId}
              isSaving={isSaving}
              onDelete={handleDeleteSkill}
              onCancel={handleCancel}
            />
          </form>
        ) : (
          /* ---- Experience form (jobs / projects / other) ---- */
          <form onSubmit={handleSaveExperience} className="flex flex-1 flex-col gap-4 overflow-y-auto p-4">
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-700">
                Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={expTitle}
                onChange={(e) => setExpTitle(e.target.value)}
                placeholder={
                  activeTab === "jobs"
                    ? "e.g. Senior Engineer at Acme Corp"
                    : activeTab === "projects"
                    ? "e.g. Open-source CLI tool"
                    : "e.g. Habitat for Humanity build"
                }
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-indigo-400 focus:outline-none"
              />
              {formErrors.title && <p className="mt-1 text-xs text-red-500">{formErrors.title}</p>}
            </div>

            {/* Type dropdown only on Other tab */}
            {activeTab === "other" && (
              <div>
                <label className="mb-1 block text-xs font-medium text-gray-700">Type</label>
                <select
                  value={expType}
                  onChange={(e) => setExpType(e.target.value as ExperienceFormData["type"])}
                  className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-900 focus:border-indigo-400 focus:outline-none"
                >
                  <option value="general">General</option>
                  <option value="volunteer">Volunteer</option>
                </select>
              </div>
            )}

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="mb-1 block text-xs font-medium text-gray-700">Start Date</label>
                <input
                  type="month"
                  value={expStartDate}
                  onChange={(e) => setExpStartDate(e.target.value)}
                  className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-900 focus:border-indigo-400 focus:outline-none"
                />
                {formErrors.start_date && (
                  <p className="mt-1 text-xs text-red-500">{formErrors.start_date}</p>
                )}
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-gray-700">End Date</label>
                <input
                  type="month"
                  value={expEndDate}
                  onChange={(e) => setExpEndDate(e.target.value)}
                  className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-900 focus:border-indigo-400 focus:outline-none"
                />
                {formErrors.end_date && (
                  <p className="mt-1 text-xs text-red-500">{formErrors.end_date}</p>
                )}
              </div>
            </div>

            <div className="flex flex-1 flex-col">
              <label className="mb-1 block text-xs font-medium text-gray-700">Notes / Summary</label>
              <textarea
                value={expContent}
                onChange={(e) => setExpContent(e.target.value)}
                placeholder="Describe this experience…"
                rows={8}
                className="flex-1 resize-none rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-indigo-400 focus:outline-none"
              />
            </div>

            {saveError && <p className="text-xs text-red-500">{saveError}</p>}
            <FormActions
              formMode={formMode}
              selectedId={selectedId}
              isSaving={isSaving}
              onDelete={handleDeleteExperience}
              onCancel={handleCancel}
            />
          </form>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Shared action button row
// ---------------------------------------------------------------------------

function FormActions({
  formMode,
  selectedId,
  isSaving,
  onDelete,
  onCancel,
}: {
  formMode: FormMode;
  selectedId: string | null;
  isSaving: boolean;
  onDelete: (id: string) => void;
  onCancel: () => void;
}) {
  return (
    <div className="flex items-center justify-between">
      {formMode === "editing" && selectedId ? (
        <button
          type="button"
          onClick={() => onDelete(selectedId)}
          className="text-xs text-gray-400 hover:text-red-500"
        >
          Delete
        </button>
      ) : (
        <span />
      )}
      <div className="flex gap-3">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-lg border border-gray-200 px-4 py-2 text-sm font-semibold text-gray-600 hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isSaving}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-50"
        >
          {isSaving ? "Saving…" : "Save"}
        </button>
      </div>
    </div>
  );
}
