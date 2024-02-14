module.exports = {
  presets: [require("@neo4j-ndl/base").tailwindConfig],
  prefix: "",
  content: ["./src/**/*.{js,jsx,ts,tsx,css}", "./public/**/*.html"],
};
