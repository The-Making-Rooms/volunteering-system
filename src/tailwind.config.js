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
          "secondary": "#37373f",
          "secondary-content": "#FFFFFF",
          "accent": "#37cdbe",
          "neutral": "#37373f",
          "base-100": "#242529",
          "base-200": "#383838",
          "base-300": "#494949",
          "base-content": "#ffffff",
        },
        bumblebee: {
          ...require("daisyui/src/theming/themes")["bumblebee"],
          "primary": "#FF7C02",
          "secondary": "#e8e8e8",

        },

        corporate: {
          ...require("daisyui/src/theming/themes")["corporate"],
        },

        

      },


    ],
  },

  darkMode: ['class', '[data-theme="chipin"]']
}

