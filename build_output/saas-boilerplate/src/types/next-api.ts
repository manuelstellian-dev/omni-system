// src/types/next-api.ts
// This file is created to resolve TS2307 for '@/types/next-api'.
// Add any specific types related to Next.js API routes or custom request objects here.

// Example: Extend Request type for API routes if you add user info via middleware
export type NextApiRequestWithUser = Request & {
  user?: {
    id: string;
    email: string;
    role?: string;
    // Add other user properties as needed
  };
};

// If no specific types are needed yet, you can simply export an empty object:
// export {};
