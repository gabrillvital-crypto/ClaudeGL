/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        teal: {
          DEFAULT: '#0E8FA3',
          dark: '#0b7a8c',
          light: '#e0f7fa',
          lighter: '#cceef3',
        },
      },
    },
  },
  plugins: [],
}
