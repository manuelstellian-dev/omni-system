// src/types/next-api.d.ts
// This file defines custom types for Next.js API routes.

/**
 * Context for tenant-specific API routes.
 */
interface TenantRouteContext {
  params: {
    tenantId: string;
  };
}

/**
 * Context for subscription-specific API routes.
 */
interface SubscriptionRouteContext {
  params: {
    tenantId: string;
    subscriptionId: string;
  };
}
