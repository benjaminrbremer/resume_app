import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Resume App",
  description: "Natural language resume and cover letter tailoring",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900">
        <nav className="border-b border-gray-200 bg-white">
          <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
            <div className="flex h-14 items-center gap-8">
              <a href="/" className="text-lg font-semibold text-indigo-600">
                ResumeApp
              </a>
              <a
                href="/experience"
                className="text-sm font-medium text-gray-600 hover:text-gray-900"
              >
                Experience
              </a>
              <a
                href="/applications"
                className="text-sm font-medium text-gray-600 hover:text-gray-900"
              >
                Applications
              </a>
            </div>
          </div>
        </nav>
        <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
          {children}
        </main>
      </body>
    </html>
  );
}
