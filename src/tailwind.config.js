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
  daisyui: {
    themes: [
      {
        chipin: {
          "primary": "#FF7C02",
          "secondary": "#FF7C02",
          "secondary-content": "#FFFFFF",
          "accent": "#37cdbe",
          "neutral": "#3d4451",
          "base-100": "#000000",
          "base-200": "#383838",
          "base-content": "#ffffff",
        },
      },
      "dark",
      "cupcake",
    ],
  },
}

