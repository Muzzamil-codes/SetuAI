"use client";
import React from "react";

export type ColorTheme = "light" | "elevated" | "dark";

interface ThemeToggleProps {
  currentTheme: ColorTheme;
  onThemeChange: (theme: ColorTheme) => void;
}

export function ThemeToggle({ currentTheme, onThemeChange }: ThemeToggleProps) {
  const options: { id: ColorTheme; label: string }[] = [
    { id: "light", label: "Light" },
    { id: "elevated", label: "Dark + White" },
    { id: "dark", label: "Dark" },
  ];

  return (
    <div className="flex bg-gray-200/80 dark:bg-gray-800 p-1 rounded-lg border border-gray-300/60 dark:border-gray-700 text-xs font-medium space-x-1">
      {options.map((opt) => (
        <button
          key={opt.id}
          onClick={() => onThemeChange(opt.id)}
          className={`px-3 py-1.5 rounded-md transition-all ${
            currentTheme === opt.id
              ? "bg-blue-600 text-white shadow-sm font-semibold"
              : "text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}