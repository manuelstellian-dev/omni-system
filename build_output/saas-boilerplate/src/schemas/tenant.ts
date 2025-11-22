import { z } from 'zod';

/**
 * Schema for creating a new tenant.
 * Requires a unique name and a URL-friendly slug.
 */
export const createTenantSchema = z.object({
  name: z.string({
    required_error: 'Tenant name is required.',
    invalid_type_error: 'Tenant name must be a string.',
  })
    .min(3, 'Tenant name must be at least 3 characters long.')
    .max(100, 'Tenant name must not exceed 100 characters.'),
  slug: z.string({
    required_error: 'Tenant slug is required.',
    invalid_type_error: 'Tenant slug must be a string.',
  })
    .min(3, 'Tenant slug must be at least 3 characters long.')
    .max(100, 'Tenant slug must not exceed 100 characters.')
    .regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, 'Slug must be lowercase, alphanumeric, and use hyphens for spaces. No leading/trailing hyphens or multiple consecutive hyphens.'),
});

/**
 * Inferred type for creating a new tenant.
 */
export type CreateTenantInput = z.infer<typeof createTenantSchema>;

/**
 * Schema for updating an existing tenant.
 * Requires the tenant's ID and allows optional updates to name and slug.
 */
export const updateTenantSchema = z.object({
  id: z.string({
    required_error: 'Tenant ID is required for update.',
    invalid_type_error: 'Tenant ID must be a string.',
  }).cuid('Invalid Tenant ID format.'), // Assuming CUID for tenant IDs
  name: z.string({
    invalid_type_error: 'Tenant name must be a string.',
  })
    .min(3, 'Tenant name must be at least 3 characters long.')
    .max(100, 'Tenant name must not exceed 100 characters.')
    .optional(),
  slug: z.string({
    invalid_type_error: 'Tenant slug must be a string.',
  })
    .min(3, 'Tenant slug must be at least 3 characters long.')
    .max(100, 'Tenant slug must not exceed 100 characters.')
    .regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, 'Slug must be lowercase, alphanumeric, and use hyphens for spaces. No leading/trailing hyphens or multiple consecutive hyphens.')
    .optional(),
});

/**
 * Inferred type for updating an existing tenant.
 */
export type UpdateTenantInput = z.infer<typeof updateTenantSchema>;

/**
 * Schema for validating a tenant ID, typically used for read or delete operations.
 */
export const tenantIdSchema = z.object({
  tenantId: z.string({
    required_error: 'Tenant ID is required.',
    invalid_type_error: 'Tenant ID must be a string.',
  }).cuid('Invalid Tenant ID format.'), // Assuming CUID for tenant IDs
});

/**
 * Inferred type for a tenant ID parameter.
 */
export type TenantIdParam = z.infer<typeof tenantIdSchema>;

/**
 * Schema for validating a tenant slug, typically used for public facing routes.
 */
export const tenantSlugSchema = z.object({
  tenantSlug: z.string({
    required_error: 'Tenant slug is required.',
    invalid_type_error: 'Tenant slug must be a string.',
  })
    .min(3, 'Tenant slug must be at least 3 characters long.')
    .max(100, 'Tenant slug must not exceed 100 characters.')
    .regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, 'Slug must be lowercase, alphanumeric, and use hyphens for spaces. No leading/trailing hyphens or multiple consecutive hyphens.'),
});

/**
 * Inferred type for a tenant slug parameter.
 */
export type TenantSlugParam = z.infer<typeof tenantSlugSchema>;