import type { DefaultSession, DefaultUser } from 'next-auth';
import type { JWT } from 'next-auth/jwt';

/**
 * Extends the NextAuth.js `Session` interface to include custom user properties.
 * This allows TypeScript to recognize `id`, `tenantId`, and `roleId` on the session user object.
 */
declare module 'next-auth' {
  interface Session {
    user: {
      id: string;
      tenantId: string;
      roleId: string;
    } & DefaultSession['user'];
  }

  /**
   * Extends the NextAuth.js `User` interface to include custom properties
   * that are returned by providers (e.g., from the database adapter).
   */
  interface User extends DefaultUser {
    id: string;
    tenantId: string;
    roleId: string;
  }
}

/**
 * Extends the NextAuth.js `JWT` interface to include custom properties.
 * This ensures that `id`, `tenantId`, and `roleId` are correctly typed within the JWT token.
 */
declare module 'next-auth/jwt' {
  interface JWT {
    id: string;
    tenantId: string;
    roleId: string;
  }
}
