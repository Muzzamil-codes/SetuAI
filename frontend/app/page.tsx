"use client";
import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import TaskInputForm from "../components/TaskInputForm";
import { ThemeToggle, ColorTheme } from "../components/ThemeToggle";

export default function HomePage() {
  const router = useRouter();
  const [theme, setTheme] = useState<ColorTheme>("elevated");

  useEffect(() => {
    const saved = localStorage.getItem("setu-theme") as ColorTheme;
    if (saved) setTheme(saved);
  }, []);

  const handleThemeChange = (newTheme: ColorTheme) => {
    setTheme(newTheme);
    localStorage.setItem("setu-theme", newTheme);
  };

  const bgStyle =
    theme === "light"
      ? "bg-gray-100 text-gray-900"
      : "bg-black text-white";

  return (
    <main className={`min-h-screen p-6 flex flex-col items-center justify-center transition-colors duration-300 ${bgStyle}`}>
      <div className="w-full max-w-xl space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Project Setu</h1>
            <p className={`text-xs ${theme === "light" ? "text-gray-500" : "text-zinc-400"}`}>
              Confidential AI Verification Engine • SIH26117
            </p>
          </div>
          <ThemeToggle currentTheme={theme} onThemeChange={handleThemeChange} />
        </div>

        <TaskInputForm theme={theme} onTaskStarted={(id) => router.push(`/trace/${id}`)} />
      </div>
    </main>
  );
}