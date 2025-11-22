import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth'; // Assuming authOptions are defined here
import { PrismaClient } from '@prisma/client';
import { createUserSchema, tenantParamsSchema } from '@/schemas/user';
import { PermissionKey } from '@/lib/rbac/permissions';
import { checkPermissions } from '@/lib/rbac/utils'; // Assuming this utility exists
import bcrypt from 'bcryptjs'; // Assuming bcryptjs is installed and used for password hashing

const prisma = new PrismaClient();

// GET /api/tenants/[tenantId]/users - List users within a tenant
export async function GET(
  req: NextRequest,
  { params }: { params: { tenantId: string } }
) {
  const session = await getServerSession(authOptions);

  if (!session || !session.user) {
    return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
  }

  const { tenantId } = params;

  // Validate tenantId from URL params
  const parsedParams = tenantParamsSchema.safeParse(params);
  if (!parsedParams.success) {
    return NextResponse.json({ message: 'Invalid tenant ID format.', errors: parsedParams.error.flatten() }, { status: 400 });
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
    const users = await prisma.user.findMany({
      where: {
        tenantId: tenantId,
      },
      select: { // Select specific fields to avoid exposing sensitive data like password hash
        id: true,
        name: true,
        email: true,
        emailVerified: true,
        image: true,
        createdAt: true,
        updatedAt: true,
        role: { // Include role name
          select: {
            id: true,
            name: true,
          },
        },
      },
    });

    return NextResponse.json(users, { status: 200 });
  } catch (error) {
    console.error(`Error listing users for tenant ${tenantId}:`, error);
    return NextResponse.json({ message: 'Internal Server Error' }, { status: 500 });
  }
}

// POST /api/tenants/[tenantId]/users - Create a new user within a tenant
export async function POST(
  req: NextRequest,
  { params }: { params: { tenantId: string } }
) {
  const session = await getServerSession(authOptions);

  if (!session || !session.user) {
    return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
  }

  const { tenantId } = params;

  // Validate tenantId from URL params
  const parsedParams = tenantParamsSchema.safeParse(params);
  if (!parsedParams.success) {
    return NextResponse.json({ message: 'Invalid tenant ID format.', errors: parsedParams.error.flatten() }, { status: 400 });
  }

  // Enforce tenant isolation and RBAC
  if (session.user.tenantId !== tenantId) {
    return NextResponse.json({ message: 'Forbidden: Tenant mismatch.' }, { status: 403 });
  }

  const hasPermission = await checkPermissions(session.user, [PermissionKey.USER_CREATE], tenantId);
  if (!hasPermission) {
    return NextResponse.json({ message: 'Forbidden: Insufficient permissions.' }, { status: 403 });
  }

  let body;
  try {
    body = await req.json();
  } catch (error) {
    return NextResponse.json({ message: 'Invalid JSON body.' }, { status: 400 });
  }

  // Validate request body
  const parsedBody = createUserSchema.safeParse(body);
  if (!parsedBody.success) {
    return NextResponse.json({ message: 'Invalid request body.', errors: parsedBody.error.flatten() }, { status: 400 });
  }

  const { email, name, password, roleId } = parsedBody.data;

  try {
    // Check if roleId exists and belongs to the system (or is valid)
    if (roleId) {
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

    const newUser = await prisma.user.create({
      data: {
        email,
        name,
        password: hashedPassword,
        tenant: {
          connect: { id: tenantId },
        },
        role: {
          connect: { id: roleId || session.user.roleId }, // Default to current user's role if not specified, or a default role
        },
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

    return NextResponse.json(newUser, { status: 201 });
  } catch (error: any) {
    if (error.code === 'P2002' && error.meta?.target?.includes('email')) {
      return NextResponse.json({ message: 'User with this email already exists in this tenant.' }, { status: 409 });
    }
    console.error(`Error creating user for tenant ${tenantId}:`, error);
    return NextResponse.json({ message: 'Internal Server Error' }, { status: 500 });
  }
}
