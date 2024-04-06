/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        cerebri: ["Cerebri Sans"],
        cerebribold: ["Cerebri Sans bold"],
        cerebriregular: ["Cerebri Sans regular"],
        cerebrisemibold: ["Cerebri Sans semibold"],
        cerebriMedium: ["CerebriSansProMedium"],
      },

      boxShadow: {
        drop: "0 19px 13px 0 rgba(193, 197, 209, 0.15)",
        dropCard: "0 0 8px 2px rgba(178, 178, 178, 0.405)",
      },

      colors: {
        // Define your custom colors here
        blackText: "#495057", // Example of adding a primary color with hex code
        customGray: "#E8E9EA",
        customsky: "#E0E8F8",
        lightSky: "#F2F6FF",
        customBlue: "#316FF6",
        borderSky: "#DDE8FF",
        white: "#FFFFFF",
        senderBG: "#F6F6F9",
        greyText: "#797C8C",
        customColor: "var(--primary-color)",
      },

      backgroundColor: {
        customBg: "var(--secondary-color)",
        customBgDark: "var(--primary-color)",
        darkBg: "var(--dark-color)",
      },

      borderColor: {
        customBorder: "var(--secondary-color)",
        customBorderDark: "var(--primary-color)",
      },
    },

    screens: {
      xxl: { max: "1700px" },
      "1xl": { max: "1460px" },
      xl: { max: "1350px" },
      lg: { max: "1024px" },
      md: { max: "768px" },
      sm: { max: "640px" },
      xs: { max: "500px" },
      xxs: { max: "424px" },
    },
  },
  plugins: [],
};
