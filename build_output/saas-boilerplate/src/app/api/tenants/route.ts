import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth'; // Assuming authOptions is defined here
import { prisma } from '@/lib/prisma'; // Assuming prisma client is initialized here
import { z } from 'zod';
import { PermissionKey, hasPermission, getUserPermissions } from '@/lib/rbac/permissions'; // Assuming these are defined here

// Utility for slug generation (simple version, can be replaced with a library)
function slugify(text: string): string {
  return text
    .toString()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^\w-]+/g, '')
    .replace(/--+/g, '-');
}

// Zod schema for tenant creation request body
const createTenantSchema = z.object({
  name: z.string().min(3, 'Tenant name must be at least 3 characters long.'),
});

/**
 * @swagger
 * /api/tenants:
 *   post:
 *     summary: Create a new tenant
 *     description: Creates a new tenant and assigns the creating user as an admin of this new tenant.
 *                  Requires 'TENANT_CREATE' permission within the user's current tenant context.
 *                  This endpoint is not designed for initial tenant creation by users without an existing tenant association.
 *     tags:
 *       - Tenants
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               name:
 *                 type: string
 *                 description: The name of the new tenant.
 *                 example: My New Company
 *     responses:
 *       201:
 *         description: Tenant created successfully, and user assigned as admin.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 id:
 *                   type: string
 *                 name:
 *                   type: string
 *                 slug:
 *                   type: string
 *                 createdAt:
 *                   type: string
 *                 updatedAt:
 *                   type: string
 *       400:
 *         description: Invalid request body.
 *       401:
 *         description: Unauthorized. User not authenticated.
 *       403:
 *         description: Forbidden. User does not have 'TENANT_CREATE' permission or is not in a valid tenant context.
 *       409:
 *         description: Conflict. Tenant with the given name or slug already exists.
 *       500:
 *         description: Internal server error.
 */
export async function POST(req: NextRequest) {
  const session = await getServerSession(authOptions);

  if (!session || !session.user) {
    return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
  }

  const { user } = session;

  // RBAC check for creating a tenant
  // This endpoint assumes that if a user has a tenantId in their session,
  // they are creating an *additional* tenant, and need TENANT_CREATE permission within their current tenant.
  // Initial tenant creation for new users (without a tenantId in session) should be handled by a different flow (e.g., signup).
  // This strict interpretation is based on `getUserPermissions` requiring a `tenantId` in the provided context.
  if (!user.tenantId) {
    return NextResponse.json(
      { message: 'Forbidden: User must be associated with a tenant to create new tenants via this endpoint.' },
      { status: 403 }
    );
  }

  const userPermissions = await getUserPermissions(user.id, user.tenantId);
  if (!hasPermission(userPermissions, [PermissionKey.TENANT_CREATE])) {
    return NextResponse.json({ message: 'Forbidden: You do not have permission to create tenants.' }, { status: 403 });
  }

  try {
    const body = await req.json();
    const validatedData = createTenantSchema.parse(body);

    const { name } = validatedData;
    const slug = slugify(name);

    // Check for existing tenant with same name or slug
    const existingTenant = await prisma.tenant.findFirst({
      where: {
        OR: [{ name: name }, { slug: slug }],
      },
    });

    if (existingTenant) {
      return NextResponse.json({ message: 'Tenant with this name or slug already exists.' }, { status: 409 });
    }

    // Use a transaction to ensure atomicity: create tenant, find/create admin role, update user
    const result = await prisma.$transaction(async (tx) => {
      const newTenant = await tx.tenant.create({
        data: {
          name,
          slug,
          // stripeCustomerId will be set during subscription setup
        },
      });

      // Find or create a default 'Admin' role
      let adminRole = await tx.role.findUnique({
        where: { name: 'Admin' },
      });

      if (!adminRole) {
        // If 'Admin' role doesn't exist, create it with basic tenant management permissions
        adminRole = await tx.role.create({
          data: {
            name: 'Admin',
            description: 'Administrator role with full access within a tenant.',
            permissions: {
              connectOrCreate: [
                {
                  where: { action: PermissionKey.TENANT_READ },
                  create: { action: PermissionKey.TENANT_READ, description: 'Allows viewing tenant details and settings.' },
                },
                {
                  where: { action: PermissionKey.TENANT_UPDATE },
                  create: { action: PermissionKey.TENANT_UPDATE, description: 'Allows updating tenant details and settings.' },
                },
                {
                  where: { action: PermissionKey.USER_READ },
                  create: { action: PermissionKey.USER_READ, description: 'Allows viewing user profiles and lists within the tenant.' },
                },
                {
                  where: { action: PermissionKey.USER_CREATE },
                  create: { action: PermissionKey.USER_CREATE, description: 'Allows inviting or creating new users within the tenant.' },
                },
                {
                  where: { action: PermissionKey.USER_UPDATE },
                  create: { action: PermissionKey.USER_UPDATE, description: 'Allows updating existing user profiles within the tenant.' },
                },
                {
                  where: { action: PermissionKey.USER_DELETE },
                  create: { action: PermissionKey.USER_DELETE, description: 'Allows removing users from the tenant.' },
                },
                {
                  where: { action: PermissionKey.USER_MANAGE_ROLES },
                  create: { action: PermissionKey.USER_MANAGE_ROLES, description: 'Allows changing user roles within the tenant.' },
                },
                {
                  where: { action: PermissionKey.SUBSCRIPTION_READ },
                  create: { action: PermissionKey.SUBSCRIPTION_READ, description: 'Allows viewing subscription status and details.' },
                },
                {
                  where: { action: PermissionKey.SUBSCRIPTION_MANAGE },
                  create: { action: PermissionKey.SUBSCRIPTION_MANAGE, description: 'Allows managing (upgrading/downgrading/cancelling) subscriptions.' },
                },
                {
                  where: { action: PermissionKey.PRODUCT_READ },
                  create: { action: PermissionKey.PRODUCT_READ, description: 'Allows viewing available products and plans.' },
                },
                // TENANT_DELETE is a highly sensitive permission, typically not granted by default to a new tenant admin.
                // {
                //   where: { action: PermissionKey.TENANT_DELETE },
                //   create: { action: PermissionKey.TENANT_DELETE, description: 'Allows deleting the tenant (irreversible action).' },
                // },
              ],
            },
          },
        });
      }

      // Update the creating user to be associated with the new tenant and assigned the Admin role
      await tx.user.update({
        where: { id: user.id },
        data: {
          tenantId: newTenant.id,
          roleId: adminRole.id,
        },
      });

      return newTenant;
    });

    return NextResponse.json(result, { status: 201 });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json({ message: 'Invalid request body', errors: error.errors }, { status: 400 });
    }
    console.error('Error creating tenant:', error);
    return NextResponse.json({ message: 'Internal server error' }, { status: 500 });
  }
}

/**
 * @swagger
 * /api/tenants:
 *   get:
 *     summary: List tenants
 *     description: Retrieves a list of tenants. Requires 'TENANT_READ' permission.
 *                  If the user has a tenantId in their session, only their associated tenant is returned.
 *                  This endpoint does not support super-admin functionality to list all tenants.
 *     tags:
 *       - Tenants
 *     responses:
 *       200:
 *         description: A list of tenants.
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 type: object
 *                 properties:
 *                   id:
 *                     type: string
 *                   name:
 *                     type: string
 *                   slug:
 *                     type: string
 *                   createdAt:
 *                     type: string
 *                   updatedAt:
 *                     type: string
 *       401:
 *         description: Unauthorized. User not authenticated.
 *       403:
 *         description: Forbidden. User does not have 'TENANT_READ' permission or is not in a valid tenant context.
 *       500:
 *         description: Internal server error.
 */
export async function GET(req: NextRequest) {
  const session = await getServerSession(authOptions);

  if (!session || !session.user) {
    return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
  }

  const { user } = session;

  // RBAC check for listing tenants
  // As per the provided RBAC context, getUserPermissions requires a tenantId.
  // Therefore, this endpoint will only allow listing tenants if the user is associated with one.
  // Super-admin functionality to list ALL tenants would require a different permission fetching mechanism
  // or a global permission check not currently supported by the provided snippets.
  if (!user.tenantId) {
    return NextResponse.json(
      { message: 'Forbidden: User must be associated with a tenant to list tenants via this endpoint.' },
      { status: 403 }
    );
  }

  const userPermissions = await getUserPermissions(user.id, user.tenantId);
  if (!hasPermission(userPermissions, [PermissionKey.TENANT_READ])) {
    return NextResponse.json({ message: 'Forbidden: You do not have permission to read tenant information.' }, { status: 403 });
  }

  try {
    // If TENANT_READ is granted, a user can only read their own tenant's details
    const tenants = await prisma.tenant.findMany({
      where: {
        id: user.tenantId,
      },
      select: {
        id: true,
        name: true,
        slug: true,
        createdAt: true,
        updatedAt: true,
      },
    });

    return NextResponse.json(tenants, { status: 200 });
  } catch (error) {
    console.error('Error fetching tenants:', error);
    return NextResponse.json({ message: 'Internal server error' }, { status: 500 });
  }
}