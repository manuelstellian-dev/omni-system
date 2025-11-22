import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth'; // Assuming authOptions are defined here
import { PrismaClient } from '@prisma/client';
import { updateUserSchema, userParamsSchema } from '@/schemas/user';
import { PermissionKey } from '@/lib/rbac/permissions';
import { checkPermissions } from '@/lib/rbac/utils'; // Assuming this utility exists
import bcrypt from 'bcryptjs'; // Assuming bcryptjs is installed and used for password hashing

const prisma = new PrismaClient();

// GET /api/tenants/[tenantId]/users/[userId] - Get a specific user
export async function GET(
  req: NextRequest,
  { params }: { params: { tenantId: string; userId: string } }
) {
  const session = await getServerSession(authOptions);

  if (!session || !session.user) {
    return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
  }

  const { tenantId, userId } = params;

  // Validate tenantId and userId from URL params
  const parsedParams = userParamsSchema.safeParse(params);
  if (!parsedParams.success) {
    return NextResponse.json({ message: 'Invalid ID format.', errors: parsedParams.error.flatten() }, { status: 400 });
  }

  // Enforce tenant isolation and RBAC
  if (session.user.tenantId !== tenantId) {
    return NextResponse.json({ message: 'Forbidden: Tenant mismatch.' }, { status: 403 });
  }

  const hasPermission = await checkPermissions(session.user, [PermissionKey.USER_READ], tenantId);
  if (!hasPermission) {
    return NextResponse.json({ message: 'Forbidden: Insufficient permissions.' }, { status: 403 });
  }

  try {
    const user = await prisma.user.findUnique({
      where: {
        id: userId,
        tenantId: tenantId, // Ensure user belongs to the specified tenant
      },
      select: {
        id: true,
        name: true,
        email: true,
        emailVerified: true,
        image: true,
        createdAt: true,
        updatedAt: true,
        role: {
          select: {
            id: true,
            name: true,
          },
        },
      },
    });

    if (!user) {
      return NextResponse.json({ message: 'User not found.' }, { status: 404 });
    }

    return NextResponse.json(user, { status: 200 });
  } catch (error) {
    console.error(`Error fetching user ${userId} for tenant ${tenantId}:`, error);
    return NextResponse.json({ message: 'Internal Server Error' }, { status: 500 });
  }
}

// PUT /api/tenants/[tenantId]/users/[userId] - Update a specific user
export async function PUT(
  req: NextRequest,
  { params }: { params: { tenantId: string; userId: string } }
) {
  const session = await getServerSession(authOptions);

  if (!session || !session.user) {
    return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
  }

  const { tenantId, userId } = params;

  // Validate tenantId and userId from URL params
  const parsedParams = userParamsSchema.safeParse(params);
  if (!parsedParams.success) {
    return NextResponse.json({ message: 'Invalid ID format.', errors: parsedParams.error.flatten() }, { status: 400 });
  }

  // Enforce tenant isolation and RBAC
  if (session.user.tenantId !== tenantId) {
    return NextResponse.json({ message: 'Forbidden: Tenant mismatch.' }, { status: 403 });
  }

  const hasUpdatePermission = await checkPermissions(session.user, [PermissionKey.USER_UPDATE], tenantId);
  if (!hasUpdatePermission) {
    return NextResponse.json({ message: 'Forbidden: Insufficient permissions to update user.' }, { status: 403 });
  }

  let body;
  try {
    body = await req.json();
  } catch (error) {
    return NextResponse.json({ message: 'Invalid JSON body.' }, { status: 400 });
  }

  // Validate request body
  const parsedBody = updateUserSchema.safeParse(body);
  if (!parsedBody.success) {
    return NextResponse.json({ message: 'Invalid request body.', errors: parsedBody.error.flatten() }, { status: 400 });
  }

  const { email, name, password, roleId } = parsedBody.data;

  try {
    // Check if the user exists and belongs to the tenant
    const existingUser = await prisma.user.findUnique({
      where: {
        id: userId,
        tenantId: tenantId,
      },
    });

    if (!existingUser) {
      return NextResponse.json({ message: 'User not found.' }, { status: 404 });
    }

    // If roleId is being updated, check for USER_MANAGE_ROLES permission
    if (roleId && roleId !== existingUser.roleId) {
      const hasManageRolesPermission = await checkPermissions(session.user, [PermissionKey.USER_MANAGE_ROLES], tenantId);
      if (!hasManageRolesPermission) {
        return NextResponse.json({ message: 'Forbidden: Insufficient permissions to change user roles.' }, { status: 403 });
      }
      // Also check if the new roleId is valid
      const roleExists = await prisma.role.findUnique({
        where: { id: roleId },
      });
      if (!roleExists) {
        return NextResponse.json({ message: 'Invalid role ID provided.' }, { status: 400 });
      }
    }

    // Hash password if provided
    let hashedPassword = undefined;
    if (password) {
      hashedPassword = await bcrypt.hash(password, 10); // Salt rounds = 10
    }

    const updatedUser = await prisma.user.update({
      where: {
        id: userId,
        tenantId: tenantId, // Crucial for multi-tenancy update isolation
      },
      data: {
        email,
        name,
        password: hashedPassword,
        roleId,
      },
      select: {
        id: true,
        name: true,
        email: true,
        emailVerified: true,
        image: true,
        createdAt: true,
        updatedAt: true,
        role: {
          select: {
            id: true,
            name: true,
          },
        },
      },
    });

    return NextResponse.json(updatedUser, { status: 200 });
  } catch (error: any) {
    if (error.code === 'P2002' && error.meta?.target?.includes('email')) {
      return NextResponse.json({ message: 'User with this email already exists in this tenant.' }, { status: 409 });
    }
    console.error(`Error updating user ${userId} for tenant ${tenantId}:`, error);
    return NextResponse.json({ message: 'Internal Server Error' }, { status: 500 });
  }
}

// DELETE /api/tenants/[tenantId]/users/[userId] - Delete a specific user
export async function DELETE(
  req: NextRequest,
  { params }: { params: { tenantId: string; userId: string } }
) {
  const session = await getServerSession(authOptions);

  if (!session || !session.user) {
    return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
  }

  const { tenantId, userId } = params;

  // Validate tenantId and userId from URL params
  const parsedParams = userParamsSchema.safeParse(params);
  if (!parsedParams.success) {
    return NextResponse.json({ message: 'Invalid ID format.', errors: parsedParams.error.flatten() }, { status: 400 });
  }

  // Enforce tenant isolation and RBAC
  if (session.user.tenantId !== tenantId) {
    return NextResponse.json({ message: 'Forbidden: Tenant mismatch.' }, { status: 403 });
  }

  const hasPermission = await checkPermissions(session.user, [PermissionKey.USER_DELETE], tenantId);
  if (!hasPermission) {
    return NextResponse.json({ message: 'Forbidden: Insufficient permissions.' }, { status: 403 });
  }

  try {
    // Check if the user exists and belongs to the tenant before attempting deletion
    const existingUser = await prisma.user.findUnique({
      where: {
        id: userId,
        tenantId: tenantId,
      },
    });

    if (!existingUser) {
      return NextResponse.json({ message: 'User not found.' }, { status: 404 });
    }

    await prisma.user.delete({
      where: {
        id: userId,
        tenantId: tenantId, // Crucial for multi-tenancy delete isolation
      },
    });

    return NextResponse.json({ message: 'User deleted successfully.' }, { status: 200 });
  } catch (error) {
    console.error(`Error deleting user ${userId} for tenant ${tenantId}:`, error);
    return NextResponse.json({ message: 'Internal Server Error' }, { status: 500 });
  }
}
