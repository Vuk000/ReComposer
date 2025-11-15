/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Violet Bloom Design System
        primary: {
          DEFAULT: '#8c5cff',
          foreground: '#ffffff',
        },
        secondary: {
          DEFAULT: '#2a2c33',
          foreground: '#f0f0f0',
        },
        accent: {
          DEFAULT: '#1e293b',
          foreground: '#79c0ff',
        },
        background: '#1a1b1e',
        foreground: '#f0f0f0',
        card: {
          DEFAULT: '#222327',
          foreground: '#f0f0f0',
        },
        popover: {
          DEFAULT: '#222327',
          foreground: '#f0f0f0',
        },
        muted: {
          DEFAULT: '#2a2c33',
          foreground: '#a0a0a0',
        },
        destructive: {
          DEFAULT: '#f87171',
          foreground: '#ffffff',
        },
        border: '#33353a',
        input: '#33353a',
        ring: '#8c5cff',
        // Chart colors
        chart: {
          1: '#4ade80',
          2: '#8c5cff',
          3: '#fca5a5',
          4: '#5993f4',
          5: '#a0a0a0',
        },
        // Sidebar colors
        sidebar: {
          DEFAULT: '#161618',
          foreground: '#f0f0f0',
          primary: '#8c5cff',
          'primary-foreground': '#ffffff',
          accent: '#2a2c33',
          'accent-foreground': '#8c5cff',
          border: '#33353a',
          ring: '#8c5cff',
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

