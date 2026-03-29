export default function ApplicationsPage() {
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
          disabled
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white opacity-50 cursor-not-allowed"
        >
          New Application
        </button>
      </div>

      <div className="rounded-xl border border-dashed border-gray-300 bg-white p-12 text-center">
        <p className="text-sm text-gray-400">No applications yet.</p>
        <p className="mt-1 text-xs text-gray-300">
          Application list coming soon.
        </p>
      </div>
    </div>
  );
}
