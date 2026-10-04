/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        sama: {
          50:  '#fdf8f3',
          100: '#f9ede0',
          200: '#f2d9bc',
          300: '#e8be8e',
          400: '#dc9d5f',
          500: '#d4843a',
          600: '#c06b2e',
          700: '#9f5327',
          800: '#804326',
          900: '#693923',
        },
      },
      fontFamily: {
        serif: ['Georgia', 'Cambria', 'serif'],
      },
    },
  },
  plugins: [],
}
