module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/static/js/**/*.js"
  ],
  safelist: [
    'bg-primary',
    'bg-accent',
    'text-muted',
    'bg-warning',
    'bg-danger',
    'text-primary',
    'text-danger',
    'hover:text-blue-700',
    'hover:bg-blue-700',
    'hover:bg-emerald-600',
    'hover:text-red-700',
  ],
  theme: {
    extend: {
      colors: {
        primary: "#2563EB",
        secondary: "#9333EA",
        muted: "#6B7280",
        accent: "#10B981",
        danger: "#EF4444",
        warning: "#F59E0B",
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        serif: ['Merriweather', 'serif'],
      },
    },
  },
  plugins: [],
}
