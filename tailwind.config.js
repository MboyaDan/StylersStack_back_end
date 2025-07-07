/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",   // scan your Jinja2 HTML templates
    "./app/static/js/**/*.js"      // optional: scan JS files
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

