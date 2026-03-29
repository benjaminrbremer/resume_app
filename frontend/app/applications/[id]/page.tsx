export default function ApplicationDetailPage({
  params,
}: {
  params: { id: string };
}) {
  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4">
      {/* Document preview panel */}
      <div className="flex w-1/2 flex-col rounded-xl border border-gray-200 bg-white">
        <div className="border-b border-gray-200 px-4 py-3">
          <h2 className="text-sm font-semibold text-gray-700">Document Preview</h2>
        </div>
        <div className="flex flex-1 items-center justify-center">
          <p className="text-sm text-gray-400">
            Generated resume and cover letter will appear here.
          </p>
        </div>
      </div>

      {/* Chat panel */}
      <div className="flex w-1/2 flex-col rounded-xl border border-gray-200 bg-white">
        <div className="border-b border-gray-200 px-4 py-3">
          <h2 className="text-sm font-semibold text-gray-700">
            Chat — Application{" "}
            <span className="font-mono text-xs text-gray-400">{params.id}</span>
          </h2>
        </div>

        {/* Message area */}
        <div className="flex-1 overflow-y-auto px-4 py-4">
          <p className="text-center text-sm text-gray-400">
            Chat messages will appear here.
          </p>
        </div>

        {/* Input area */}
        <div className="border-t border-gray-200 px-4 py-3">
          <div className="flex gap-2">
            <input
              type="text"
              disabled
              placeholder="Type a message…"
              className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50 disabled:cursor-not-allowed"
            />
            <button
              disabled
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white opacity-50 cursor-not-allowed"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
