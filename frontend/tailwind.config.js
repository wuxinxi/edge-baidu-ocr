/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        arena: {
          bg: '#0f172a',
          card: '#1e293b',
          border: '#334155',
          accent: '#38bdf8',
        }
      }
    },
  },
  plugins: [],
}
