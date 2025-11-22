import { withAuth } from 'next-auth/middleware';
import { NextResponse } from 'next/server';
import type { NextRequestWithAuth } from 'next-auth/middleware';
import { authOptions } from '@/lib/auth-options'; // Assuming authOptions is exported from here
import { getUserPermissions, hasPermission, getTenantIdFromSlug } from '@/lib/rbac/utils';
import { PermissionKey } from '@/lib/rbac/permissions';
import { RbacSessionUserSchema } from '@/lib/rbac/schemas';

// Extend the session type for better type safety in middleware
declare module 'next-auth' {
  interface Session {
    user: {
      id: string;
      email: string;
      tenantId?: string; // Add tenantId to session user
      roleId?: string;    // Add roleId to session user
      roleName?: string;  // Add roleName to session user
    };
  }
}

/**
 * Defines the required permissions for specific routes.
 * The key is a regex pattern for the route, and the value is the required permission(s).
 * Routes are matched in order, so more specific routes should come before general ones.
 * This map assumes tenant-scoped routes are structured as `/[tenantSlug]/[path]`.
 */
const routePermissions: Record<string, PermissionKey | PermissionKey[]> = {
  '^/([^/]+)/dashboard$': PermissionKey.DASHBOARD_ACCESS,
  '^/([^/]+)/settings/tenant$': PermissionKey.TENANT_UPDATE,
  '^/([^/]+)/settings/users$': [PermissionKey.USER_READ, PermissionKey.USER_MANAGE_ROLES],
  '^/([^/]+)/settings/users/create$': PermissionKey.USER_CREATE,
  '^/([^/]+)/settings/users/[^/]+$': PermissionKey.USER_UPDATE, // For specific user profiles
  '^/([^/]+)/subscriptions$': PermissionKey.SUBSCRIPTION_READ,
  '^/([^/]+)/subscriptions/manage$': PermissionKey.SUBSCRIPTION_MANAGE,
  '^/([^/]+)/products$': PermissionKey.PRODUCT_READ,
  '^/([^/]+)/products/manage$': PermissionKey.PRODUCT_MANAGE,
  // Add more route-permission mappings as needed
};

export default withAuth(
  async function middleware(req: NextRequestWithAuth) {
    const { pathname, searchParams } = req.nextUrl;
    const token = req.nextauth.token;

    // 1. Handle unauthenticated users
    if (!token) {
      // Redirect to login if trying to access a protected route without a token
      // `withAuth` handles this by default for routes in `matcher`
      return NextResponse.redirect(new URL('/api/auth/signin', req.url));
    }

    // Validate and parse the session user data
    const parsedUser = RbacSessionUserSchema.safeParse(token);
    if (!parsedUser.success) {
      console.error('Invalid session user data in middleware:', parsedUser.error.flatten());
      // Potentially clear session and redirect to login or error page
      return NextResponse.redirect(new URL('/api/auth/signin', req.url));
    }
    const user = parsedUser.data;

    // 2. Extract tenant slug from the path
    const tenantSlugMatch = pathname.match(/^\/([^/]+)/);
    const tenantSlug = tenantSlugMatch ? tenantSlugMatch[1] : null;

    let tenantId: string | undefined = user.tenantId; // Try to get from session first

    if (tenantSlug) {
      // If tenantSlug is in the path, ensure it matches the user's tenant or resolve it
      const resolvedTenantId = await getTenantIdFromSlug(tenantSlug);

      if (!resolvedTenantId) {
        // Tenant not found for the given slug
        return NextResponse.redirect(new URL('/404', req.url));
      }

      if (user.tenantId && user.tenantId !== resolvedTenantId) {
        // User is trying to access a tenant they are not associated with
        console.warn(`User ${user.id} (tenant ${user.tenantId}) attempted to access tenant ${resolvedTenantId} via slug ${tenantSlug}`);
        return NextResponse.redirect(new URL('/access-denied', req.url));
      }
      tenantId = resolvedTenantId;
    }

    // If a tenant-scoped route is accessed, but no tenantId could be determined
    if (tenantSlug && !tenantId) {
      console.warn(`Tenant ID could not be determined for tenantSlug: ${tenantSlug} for user: ${user.id}`);
      return NextResponse.redirect(new URL('/access-denied', req.url));
    }

    // 3. Fetch user permissions for the current tenant context
    let userPermissions: PermissionKey[] = [];
    if (tenantId) {
      userPermissions = await getUserPermissions(user.id, tenantId);
    } else {
      // For global routes (e.g., /account, /profile), permissions might be global or not required
      // For this boilerplate, we assume most protected routes are tenant-scoped.
      // If global permissions are needed, implement a separate logic here.
      console.log(`Accessing global route ${pathname} for user ${user.id}. No tenant-specific permissions fetched.`);
    }

    // 4. Enforce RBAC for the current route
    for (const pattern in routePermissions) {
      const regex = new RegExp(pattern);
      if (regex.test(pathname)) {
        const requiredPerms = routePermissions[pattern];

        if (!hasPermission(userPermissions, requiredPerms)) {
          console.warn(`Access denied for user ${user.id} to ${pathname}. Missing permissions: ${JSON.stringify(requiredPerms)}`);
          return NextResponse.redirect(new URL('/access-denied', req.url));
        }
        // If permission is granted, continue to the next middleware or route handler
        return NextResponse.next();
      }
    }

    // If no specific permission is defined for the route, allow access by default
    // Or, implement a stricter default deny policy.
    return NextResponse.next();
  },
  {
    callbacks: {
      // The `authorized` callback determines if a user is authenticated.
      // If it returns `false`, the user is redirected to the sign-in page.
      async authorized({ token, req }) {
        // Allow access to public routes or API routes that don't require auth
        const { pathname } = req.nextUrl;
        if (pathname.startsWith('/api/auth') || pathname.startsWith('/_next') || pathname.startsWith('/static') || pathname === '/login' || pathname === '/register' || pathname === '/access-denied') {
          return true;
        }
        // For all other routes, a token must exist (user must be authenticated)
        return !!token;
      },
    },
    // Matcher to specify which routes the middleware should run on.
    // This should include all routes that require authentication and/or RBAC.
    // Exclude API routes handled by NextAuth.js itself and static assets.
    matcher: [
      '/((?!api/auth|_next/static|_next/image|favicon.ico|login|register|access-denied).*)',
    ],
  }
);
