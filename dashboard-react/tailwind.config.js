/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        teal: {
          DEFAULT: '#0E8FA3',
          light: '#5BBFCC',
          dark: '#0A6A7A',
        },
      },
      fontFamily: {
        sans: ['Calibri', 'Arial', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
