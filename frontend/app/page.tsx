export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
        Resume App
      </h1>
      <p className="mt-4 max-w-xl text-lg text-gray-500">
        Track your experience, skills, and job applications. Generate tailored
        resumes and cover letters through a natural language interface.
      </p>
      <div className="mt-8 flex gap-4">
        <a
          href="/experience"
          className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500"
        >
          Manage Experience
        </a>
        <a
          href="/applications"
          className="rounded-lg border border-gray-300 bg-white px-5 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-50"
        >
          View Applications
        </a>
      </div>
    </div>
  );
}
