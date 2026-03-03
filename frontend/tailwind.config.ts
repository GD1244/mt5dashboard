import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        // Dark theme base
        zinc: {
          850: '#1f2937',
          900: '#18181b',
          950: '#09090b',
        },
        // Heatmap colors
        heat: {
          deepRed: '#7f1d1d',
          red: '#dc2626',
          orange: '#ea580c',
          neutral: '#3f3f46',
          lime: '#65a30d',
          green: '#16a34a',
          deepGreen: '#14532d',
          emerald: '#10b981',
        },
        // Gold/Silver/Bronze for ranks
        rank: {
          gold: '#fbbf24',
          silver: '#94a3b8',
          bronze: '#b45309',
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'flash-green': 'flashGreen 0.5s ease-out',
        'flash-red': 'flashRed 0.5s ease-out',
      },
      keyframes: {
        flashGreen: {
          '0%': { backgroundColor: 'rgba(16, 185, 129, 0.4)' },
          '100%': { backgroundColor: 'transparent' },
        },
        flashRed: {
          '0%': { backgroundColor: 'rgba(239, 68, 68, 0.4)' },
          '100%': { backgroundColor: 'transparent' },
        },
      },
    },
  },
  plugins: [],
}

export default config