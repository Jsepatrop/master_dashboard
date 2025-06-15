/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'cyber': {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49',
        },
        'neon': {
          'cyan': '#00ffff',
          'pink': '#ff00ff',
          'green': '#00ff00',
          'purple': '#8b5cf6',
          'blue': '#3b82f6',
          'orange': '#fb923c'
        },
        'dark': {
          100: '#1e1e2e',
          200: '#181825',
          300: '#11111b',
          400: '#0a0a0f',
          500: '#050507'
        }
      },
      fontFamily: {
        'cyber': ['Orbitron', 'monospace'],
        'mono': ['JetBrains Mono', 'monospace']
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'float': 'float 6s ease-in-out infinite',
        'matrix': 'matrix 20s linear infinite',
        'scan': 'scan 3s linear infinite',
        'flicker': 'flicker 0.15s infinite linear alternate'
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px #00ffff, 0 0 10px #00ffff, 0 0 15px #00ffff' },
          '100%': { boxShadow: '0 0 10px #00ffff, 0 0 20px #00ffff, 0 0 30px #00ffff' }
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' }
        },
        matrix: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' }
        },
        scan: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100vw)' }
        },
        flicker: {
          '0%': { opacity: '1' },
          '100%': { opacity: '0.8' }
        }
      },
      backdropBlur: {
        'xs': '2px',
      },
      screens: {
        '3xl': '1920px',
        '4xl': '2560px'
      }
    },
  },
  plugins: [],
}