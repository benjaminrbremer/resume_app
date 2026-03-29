export default function ExperiencePage() {
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Experience</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage your work experience, personal projects, and skills.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        {["Work Experience", "Projects", "Skills"].map((category) => (
          <div
            key={category}
            className="rounded-xl border border-gray-200 bg-white p-6"
          >
            <h2 className="text-base font-semibold text-gray-900">{category}</h2>
            <p className="mt-2 text-sm text-gray-400">Coming soon</p>
          </div>
        ))}
      </div>
    </div>
  );
}
