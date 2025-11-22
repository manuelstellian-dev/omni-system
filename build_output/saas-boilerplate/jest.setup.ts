import '@testing-library/jest-dom';

// Define a dummy type for MyService to make the example compile
interface MyService {
  getData(): string;
}

// Mock a service for testing purposes
jest.mock('./services/myService', () => {
  return {
    __esModule: true,
    // FIX: Added missing closing angle bracket for the type assertion
    default: { // Corrected syntax
      getData: () => 'mocked data'
    } as MyService,
  };
});

// Other global setup (e.g., custom matchers, environment variables)
// For example, if you have custom matchers, they might look like this:
/*
expect.extend({
  toBeWithinRange(received: number, floor: number, ceiling: number) {
    const pass = received >= floor && received <= ceiling;
    if (pass) {
      return {
        message: () => `expected ${received} not to be within range ${floor} - ${ceiling}`,
        pass: true,
      };
    } else {
      return {
        message: () => `expected ${received} to be within range ${floor} - ${ceiling}`,
        pass: false,
      };
    }
  },
});
*/
