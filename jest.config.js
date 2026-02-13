export default {
  testEnvironment: 'jsdom',
  moduleFileExtensions: ['js', 'json', 'vue'],
  transform: {
    '^.+\\.vue$': '@vue/vue3-jest',
    '^.+\\.[jt]s$': 'babel-jest'
  },
  testMatch: [
    '<rootDir>/src/**/*.spec.[jt]s',
    '<rootDir>/src/**/*.test.[jt]s'
  ]
};
