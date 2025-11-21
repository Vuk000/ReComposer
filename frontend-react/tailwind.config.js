/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Natural Blue-Purple Design System
        primary: {
          DEFAULT: '#8b5cf6',
          foreground: '#ffffff',
        },
        secondary: {
          DEFAULT: '#64748b',
          foreground: '#f1f5f9',
        },
        accent: {
          DEFAULT: '#7c3aed',
          foreground: '#ffffff',
        },
        background: '#0f172a',
        foreground: '#e2e8f0',
        card: {
          DEFAULT: '#1e293b',
          foreground: '#e2e8f0',
        },
        popover: {
          DEFAULT: '#1e293b',
          foreground: '#e2e8f0',
        },
        muted: {
          DEFAULT: '#334155',
          foreground: '#94a3b8',
        },
        destructive: {
          DEFAULT: '#ef4444',
          foreground: '#ffffff',
        },
        border: '#334155',
        input: '#334155',
        ring: '#8b5cf6',
        // Chart colors
        chart: {
          1: '#34d399',
          2: '#8b5cf6',
          3: '#f472b6',
          4: '#60a5fa',
          5: '#a78bfa',
        },
        // Sidebar colors
        sidebar: {
          DEFAULT: '#0c1222',
          foreground: '#e2e8f0',
          primary: '#8b5cf6',
          'primary-foreground': '#ffffff',
          accent: '#1e293b',
          'accent-foreground': '#a78bfa',
          border: '#1e293b',
          ring: '#8b5cf6',
        },
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'sans-serif'],
        serif: ['Lora', 'serif'],
        mono: ['IBM Plex Mono', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '1.4rem',
      },
      boxShadow: {
        DEFAULT: '0 2px 3px 0 rgba(0, 0, 0, 0.2)',
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-in-left': {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        'slide-in-right': {
          '0%': { opacity: '0', transform: 'translateX(20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        'scale-in': {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
      animation: {
        'fade-in': 'fade-in 0.5s ease-out',
        'slide-in-left': 'slide-in-left 0.5s ease-out',
        'slide-in-right': 'slide-in-right 0.5s ease-out',
        'scale-in': 'scale-in 0.3s ease-out',
      },
    },
  },
  plugins: [],
}

