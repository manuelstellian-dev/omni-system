/** @type {import('ts-jest').JestConfigWithTsJest} */
const nextJest = require('next/jest');

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files in your test environment
  dir: './',
});

// Add any custom config to be passed to Jest
const customJestConfig = {
  // Add more setup options before each test is run
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleDirectories: ['node_modules', '<rootDir>/'],
  testEnvironment: 'node', // Use 'node' for backend/API tests, 'jsdom' for frontend/UI tests
  testPathIgnorePatterns: ['<rootDir>/.next/', '<rootDir>/node_modules/', '<rootDir>/e2e/'],
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coveragePathIgnorePatterns: [
    '<rootDir>/node_modules/',
    '<rootDir>/prisma/',
    '<rootDir>/.next/',
    '<rootDir>/src/instrumentation.ts',
    '<rootDir>/src/lib/observability/',
  ],
  // A map from regular expressions to paths to transformers
  transform: {
    '^.+\.(ts|tsx)$': ['ts-jest', {
      tsconfig: '<rootDir>/tsconfig.jest.json',
    }],
  },
  // Module file extensions for importing
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  // Alias paths for imports (e.g., @/lib -> src/lib)
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  globals: {
    'ts-jest': {
      tsconfig: '<rootDir>/tsconfig.jest.json',
    },
  },
};

// createJestConfig is exported this way to ensure that next/jest can load the Next.js config which is async
module.exports = createJestConfig(customJestConfig);
