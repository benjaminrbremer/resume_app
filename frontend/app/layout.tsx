import type { Metadata } from "next";
import "./globals.css";
import NavClient from "@/components/NavClient";

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
        <NavClient />
        <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
          {children}
        </main>
      </body>
    </html>
  );
}
