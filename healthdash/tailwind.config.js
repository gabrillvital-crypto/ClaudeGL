/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        efcaz: {
          DEFAULT: '#0f4c9b',
          muted: '#0d3f80',
        },
      },
      // Status semânticos — usados APENAS para indicadores de estado
      // verde  → emerald-400 / emerald-500
      // amarelo → amber-400
      // vermelho → red-400 / red-500
    },
  },
  plugins: [],
}
