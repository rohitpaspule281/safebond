import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#1F2A2A",
        sage: {
          50: "#F3F7F4",
          100: "#DCEAE2",
          200: "#BED6C8",
          300: "#9CBBAE",
          400: "#73988A",
          500: "#57796D",
          600: "#48655A",
          700: "#3A524A",
          800: "#2D403A",
          900: "#22312D"
        },
        sand: {
          50: "#FCF9F4",
          100: "#F5EDE1",
          200: "#EAD9C1",
          300: "#DFC29F",
          400: "#D2AA7A",
          500: "#B98B5F",
          600: "#946F4C",
          700: "#74563D",
          800: "#55402E",
          900: "#3E2F24"
        },
        coral: {
          50: "#FFF5F1",
          100: "#FFE4D6",
          200: "#FFC5AE",
          300: "#FFA281",
          400: "#FA7C5A",
          500: "#E65E42",
          600: "#C4462F",
          700: "#9F3526",
          800: "#7F2B21",
          900: "#64251E"
        },
        mist: "#E9F1EC"
      },
      boxShadow: {
        panel: "0 24px 80px rgba(40, 55, 49, 0.14)",
        soft: "0 12px 40px rgba(60, 82, 75, 0.12)"
      },
      borderRadius: {
        "4xl": "2rem"
      },
      backgroundImage: {
        "wellness-radial":
          "radial-gradient(circle at top left, rgba(232,244,236,0.95) 0%, rgba(252,249,244,0.96) 38%, rgba(248,241,232,0.94) 100%)",
        "dashboard-grid":
          "linear-gradient(rgba(87,121,109,0.07) 1px, transparent 1px), linear-gradient(90deg, rgba(87,121,109,0.07) 1px, transparent 1px)"
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-8px)" }
        },
        pulseGlow: {
          "0%, 100%": { opacity: "0.72", transform: "scale(1)" },
          "50%": { opacity: "1", transform: "scale(1.04)" }
        }
      },
      animation: {
        float: "float 8s ease-in-out infinite",
        "pulse-glow": "pulseGlow 6s ease-in-out infinite"
      }
    }
  },
  plugins: []
};

export default config;
