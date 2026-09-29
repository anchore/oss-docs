// project-level postcss config so Hugo does not hand PostCSS the docsy copy inside the
// module cache, which is outside the paths Node.js is allowed to read (security.node).
module.exports = {
  plugins: {
    autoprefixer: {},
  },
};
