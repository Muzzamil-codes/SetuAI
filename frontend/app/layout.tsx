import "./globals.css";

export const metadata = {
  title: "SETU AI",
  description: "Sovereign AI Workbench",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-[var(--background)] text-[var(--foreground)] h-screen overflow-hidden antialiased">
        {children}
      </body>
    </html>
  );
}