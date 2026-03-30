"use client";

import { useEffect, useRef, useState } from "react";
import {
  ExampleDocumentRecord,
  deleteExampleDocument,
  getExampleDocumentContentUrl,
  listExampleDocuments,
  updateExampleDocument,
  uploadExampleDocument,
} from "@/lib/api";

const USERNAME = "alice"; // temporary until session auth is implemented

const DOC_TYPE_LABEL: Record<string, string> = {
  resume: "Resume",
  cover_letter: "Cover Letter",
  other: "Other",
};

const DOC_TYPE_BADGE: Record<string, string> = {
  resume: "bg-blue-100 text-blue-700",
  cover_letter: "bg-purple-100 text-purple-700",
  other: "bg-gray-100 text-gray-700",
};

function formatDate(dt: string): string {
  return new Date(dt).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export default function ExampleDocumentsPage() {
  const [docs, setDocs] = useState<ExampleDocumentRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const selected = docs.find((d) => d.id === selectedId) ?? null;

  useEffect(() => {
    listExampleDocuments(USERNAME)
      .then((records) => {
        setDocs(records);
        if (records.length > 0) setSelectedId(records[0].id);
      })
      .catch((e) => setError(e.message))
      .finally(() => setIsLoading(false));
  }, []);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadError(null);
    setIsUploading(true);
    try {
      const record = await uploadExampleDocument(USERNAME, file);
      setDocs((prev) => [record, ...prev]);
      setSelectedId(record.id);
    } catch (e: unknown) {
      setUploadError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  async function handleTypeChange(docId: string, newType: string) {
    try {
      const updated = await updateExampleDocument(docId, newType);
      setDocs((prev) => prev.map((d) => (d.id === docId ? updated : d)));
    } catch {
      // silently ignore — UI will revert on next list fetch
    }
  }

  async function handleDelete(docId: string) {
    try {
      await deleteExampleDocument(docId);
      setDocs((prev) => {
        const next = prev.filter((d) => d.id !== docId);
        if (selectedId === docId) setSelectedId(next[0]?.id ?? null);
        return next;
      });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Delete failed");
    }
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4">
      {/* Left panel: list + upload */}
      <div className="flex w-72 flex-shrink-0 flex-col gap-3 overflow-y-auto">
        <div className="flex items-center justify-between">
          <h1 className="text-base font-semibold text-gray-900">Documents</h1>
          <button
            type="button"
            disabled={isUploading}
            onClick={() => fileInputRef.current?.click()}
            className="rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-500 disabled:opacity-50"
          >
            {isUploading ? "Uploading…" : "Upload"}
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt,.md"
            className="hidden"
            onChange={handleFileChange}
          />
        </div>

        {uploadError && <p className="text-xs text-red-500">{uploadError}</p>}
        {error && <p className="text-xs text-red-500">{error}</p>}

        {isLoading ? (
          <p className="text-sm text-gray-400">Loading…</p>
        ) : docs.length === 0 ? (
          <p className="text-sm text-gray-400">No documents yet.</p>
        ) : (
          <ul className="space-y-2">
            {docs.map((doc) => (
              <li
                key={doc.id}
                onClick={() => setSelectedId(doc.id)}
                className={`cursor-pointer rounded-xl border px-3 py-2.5 transition-colors ${
                  selectedId === doc.id
                    ? "border-indigo-300 bg-indigo-50"
                    : "border-gray-200 bg-white hover:border-gray-300"
                }`}
              >
                <p className="truncate text-sm font-medium text-gray-900">
                  {doc.original_filename}
                </p>
                <p className="mt-0.5 text-xs text-gray-400">{formatDate(doc.created_dt)}</p>
                <div className="mt-1.5 flex items-center gap-2">
                  <span
                    className={`inline-block rounded px-1.5 py-0.5 text-xs font-medium ${
                      doc.document_type
                        ? DOC_TYPE_BADGE[doc.document_type]
                        : "bg-gray-100 text-gray-500"
                    }`}
                  >
                    {doc.document_type ? DOC_TYPE_LABEL[doc.document_type] : "Unclassified"}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Right panel: preview + actions */}
      <div className="flex flex-1 flex-col gap-3 overflow-hidden">
        {selected ? (
          <>
            {/* Action bar */}
            <div className="flex items-center gap-3 rounded-xl border border-gray-200 bg-white px-4 py-2.5">
              <span className="truncate text-sm font-medium text-gray-900 flex-1">
                {selected.original_filename}
              </span>

              {/* Type selector */}
              <select
                value={selected.document_type ?? ""}
                onChange={(e) => handleTypeChange(selected.id, e.target.value)}
                className="rounded-lg border border-gray-200 px-2 py-1 text-xs text-gray-700 focus:border-indigo-400 focus:outline-none"
              >
                <option value="" disabled>
                  Classify…
                </option>
                <option value="resume">Resume</option>
                <option value="cover_letter">Cover Letter</option>
                <option value="other">Other</option>
              </select>

              {/* Download */}
              <a
                href={getExampleDocumentContentUrl(selected.id, true)}
                download={selected.original_filename}
                className="rounded-lg border border-gray-200 px-3 py-1 text-xs font-medium text-gray-700 hover:border-gray-300 hover:text-gray-900"
              >
                Download
              </a>

              {/* Delete */}
              <button
                type="button"
                onClick={() => handleDelete(selected.id)}
                className="text-xs font-medium text-red-500 hover:text-red-700"
              >
                Delete
              </button>
            </div>

            {/* Iframe preview */}
            <iframe
              key={selected.id}
              src={getExampleDocumentContentUrl(selected.id)}
              className="flex-1 rounded-xl border border-gray-200 bg-white"
              title={selected.original_filename}
            />
          </>
        ) : (
          <div className="flex flex-1 items-center justify-center rounded-xl border border-dashed border-gray-200 bg-white">
            <p className="text-sm text-gray-400">Select a document to preview it.</p>
          </div>
        )}
      </div>
    </div>
  );
}
