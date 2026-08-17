/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        paper: "#F7F7F3",
        surface: "#FFFFFF",
        ink: {
          DEFAULT: "#15171E",
          soft: "#565B67",
          faint: "#8A8F9A",
        },
        line: {
          DEFAULT: "#E6E4DD",
          soft: "#EFEEE8",
        },
        accent: {
          DEFAULT: "#28345E",
          bright: "#3E5CC4",
          soft: "#EEF0F8",
        },
        signal: {
          critical: "#B23B32",
          "critical-soft": "#F7E9E7",
          high: "#B8752A",
          "high-soft": "#F7EFE2",
          medium: "#9C7F14",
          "medium-soft": "#F7F1DD",
          low: "#2F7D57",
          "low-soft": "#E8F3ED",
        },
      },
      fontFamily: {
        display: ["'Fraunces'", "serif"],
        body: ["'Inter'", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(21,23,30,0.04), 0 1px 1px rgba(21,23,30,0.03)",
        pop: "0 12px 32px rgba(21,23,30,0.10), 0 2px 8px rgba(21,23,30,0.06)",
      },
      borderRadius: {
        xl2: "0.875rem",
      },
    },
  },
  plugins: [],
}
