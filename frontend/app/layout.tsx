import "./globals.css";
import { ThemeProvider } from "../components/ThemeProvider";
import Navbar from "../components/Navbar";

export const metadata = {
  title: "SETU.AI — Sovereign Air-Gapped AI Workbench",
  description: "Institutional Sovereign AI Workbench for Refineries, PSUs, and Defense Organizations. Zero network egress, formal AST verification, and autonomous execution.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className="bg-[#060911] text-slate-100 min-h-screen flex flex-col antialiased selection:bg-emerald-500/30 selection:text-emerald-300">
        <ThemeProvider>
          <div className="min-h-screen flex flex-col bg-grid-pattern bg-radial-glow">
            <Navbar />
            <div className="flex-1">
              {children}
            </div>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}