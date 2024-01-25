/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './**/templates/**/*.html',
    './**/templates/*.html',
  ],
  plugins: [require("daisyui")],
  theme: {
    extend: {},
  },
}

