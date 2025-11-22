import nextJest from 'next/jest';

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files in your test environment
  dir: './',
});

// Add any custom config to be passed to Jest
const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  testEnvironment: 'jest-environment-jsdom',
  preset: 'ts-jest', // Use ts-jest for TypeScript files
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },
  // Explicitly tell Jest how to transform TypeScript files
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest',
  },
  // Configure ts-jest
  globals: {
    'ts-jest': {
      tsconfig: 'tsconfig.json', // Point to your project's tsconfig
    },
  },
};

// createJestConfig is exported this way to ensure that next/jest can load the Next.js config which is async
export default createJestConfig(customJestConfig);
