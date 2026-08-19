import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Try the Model — Credit Risk Default Prediction",
  description: "Fill out a simplified loan application and get a live prediction from the real deployed model.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-screen bg-surface-2 text-text-primary">{children}</body>
    </html>
  );
}
