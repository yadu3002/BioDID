module.exports = {
  testMatch: ["**/test/**/*.test.js"],
  transform: {
    "^.+\\.js$": "babel-jest"
  },
  testEnvironment: "node"
};
