import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        border: "var(--border)",
        card: "var(--card)",
        brand: {
          50: "#f0fdf4",
          100: "#e0f2fe",
          400: "#38bdf8",
          500: "#0ea5e9",
          600: "#0284c7",
          700: "#0369a1",
        },
        accent: {
          cyan: "#06b6d4",
          sky: "#38bdf8",
          indigo: "#6366f1",
          emerald: "#10b981",
          amber: "#f59e0b",
          rose: "#f43f5e",
        },
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "glass-gradient": "linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%)",
        "cyan-indigo-gradient": "linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #6366f1 100%)",
      },
      boxShadow: {
        "glow-cyan": "0 0 20px -3px rgba(6, 182, 212, 0.25)",
        "glow-indigo": "0 0 20px -3px rgba(99, 102, 241, 0.25)",
        "glow-rose": "0 0 20px -5px rgba(244, 63, 94, 0.3)",
        "glow-emerald": "0 0 20px -5px rgba(16, 185, 129, 0.3)",
        "card-subtle": "0 4px 20px -2px rgba(0, 0, 0, 0.5)",
      },
    },
  },
  plugins: [],
};
export default config;
