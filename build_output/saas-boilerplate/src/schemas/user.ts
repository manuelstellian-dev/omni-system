import { z } from 'zod';

export const createUserSchema = z.object({
  email: z.string().email('Invalid email address.').max(255, 'Email cannot exceed 255 characters.').trim(),
  name: z.string().min(1, 'Name is required.').max(255, 'Name cannot exceed 255 characters.').trim().optional(),
  password: z.string().min(8, 'Password must be at least 8 characters long.').max(255, 'Password cannot exceed 255 characters.').optional(),
  roleId: z.string().cuid('Invalid role ID format.').max(255, 'Role ID cannot exceed 255 characters.').optional(), // Optional for now, but typically required for new users
});

export type CreateUserSchema = z.infer<typeof createUserSchema>;

export const updateUserSchema = z.object({
  name: z.string().min(1, 'Name is required.').max(255, 'Name cannot exceed 255 characters.').trim().optional(),
  email: z.string().email('Invalid email address.').max(255, 'Email cannot exceed 255 characters.').trim().optional(),
  roleId: z.string().cuid('Invalid role ID format.').max(255, 'Role ID cannot exceed 255 characters.').optional(),
  // Password updates should ideally be handled via a separate, more secure flow (e.g., 'change password' endpoint)
  // For simplicity, we'll allow it here, but it's often a separate concern.
  password: z.string().min(8, 'Password must be at least 8 characters long.').max(255, 'Password cannot exceed 255 characters.').optional(),
}).refine(data => Object.keys(data).length > 0, {
  message: 'At least one field must be provided for update.',
  path: ['_root'],
});

export type UpdateUserSchema = z.infer<typeof updateUserSchema>;

export const userParamsSchema = z.object({
  tenantId: z.string().cuid('Invalid tenant ID format.'),
  userId: z.string().cuid('Invalid user ID format.'),
});

export const tenantParamsSchema = z.object({
  tenantId: z.string().cuid('Invalid tenant ID format.'),
});
