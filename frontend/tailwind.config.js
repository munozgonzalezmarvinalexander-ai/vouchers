/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#0f1729',
        brand: {
          DEFAULT: '#1b5e9c', 50: '#eef4fb', 100: '#d8e6f5',
          600: '#1b5e9c', 700: '#174e84',
        },
      },
      fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] },
    },
  },
  plugins: [],
}
