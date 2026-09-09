import "./globals.css";

export const metadata = {
  title: "SETU AI",
  description: "Sovereign AI Workbench",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className="bg-[#0a0a0a] text-white h-screen overflow-hidden">
        {children}
      </body>
    </html>
  );
}