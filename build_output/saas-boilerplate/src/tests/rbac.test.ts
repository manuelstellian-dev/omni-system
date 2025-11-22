import { prisma } from '@/lib/prisma'; // Assuming prisma client is exported from here
import { Role, Permission, User } from '@prisma/client';

// Assuming an RBAC utility function or service exists, e.g., in src/lib/rbac.ts
// For this test, we'll simulate a simple `checkPermission` function.
// In a real application, this might be a more complex service or middleware.

interface UserWithRoleAndPermissions extends User {
  role: Role & { permissions: Permission[] };
}

// Mock RBAC utility function
const checkPermission = async (userId: string, requiredAction: string): Promise<boolean> => {
  const user = await prisma.user.findUnique({
    where: { id: userId },
    include: {
      role: {
        include: {
          permissions: true,
        },
      },
    },
  });

  if (!user || !user.role) {
    return false;
  }

  return user.role.permissions.some(p => p.action === requiredAction);
};

describe('Role-Based Access Control (RBAC)', () => {
  const mockAdminRole: Role & { permissions: Permission[] } = {
    id: 'admin_role_id',
    name: 'Admin',
    description: 'Administrator role with full access',
    createdAt: new Date(),
    updatedAt: new Date(),
    permissions: [
      { id: 'p1', action: 'tenant:read', description: null, createdAt: new Date(), updatedAt: new Date() },
      { id: 'p2', action: 'tenant:create', description: null, createdAt: new Date(), updatedAt: new Date() },
      { id: 'p3', action: 'user:read', description: null, createdAt: new Date(), updatedAt: new Date() },
      { id: 'p4', action: 'user:create', description: null, createdAt: new Date(), updatedAt: new Date() },
      { id: 'p5', action: 'user:delete', description: null, createdAt: new Date(), updatedAt: new Date() },
    ],
  };

  const mockMemberRole: Role & { permissions: Permission[] } = {
    id: 'member_role_id',
    name: 'Member',
    description: 'Standard member role',
    createdAt: new Date(),
    updatedAt: new Date(),
    permissions: [
      { id: 'p1', action: 'tenant:read', description: null, createdAt: new Date(), updatedAt: new Date() },
      { id: 'p3', action: 'user:read', description: null, createdAt: new Date(), updatedAt: new Date() },
    ],
  };

  const mockAdminUser: UserWithRoleAndPermissions = {
    id: 'admin_user_id',
    name: 'Admin User',
    email: 'admin@example.com',
    emailVerified: new Date(),
    image: null,
    password: 'hashedpassword',
    tenantId: 'tenant1',
    roleId: mockAdminRole.id,
    createdAt: new Date(),
    updatedAt: new Date(),
    role: mockAdminRole,
  };

  const mockMemberUser: UserWithRoleAndPermissions = {
    id: 'member_user_id',
    name: 'Member User',
    email: 'member@example.com',
    emailVerified: new Date(),
    image: null,
    password: 'hashedpassword',
    tenantId: 'tenant1',
    roleId: mockMemberRole.id,
    createdAt: new Date(),
    updatedAt: new Date(),
    role: mockMemberRole,
  };

  it('admin user should have permission for allowed actions', async () => {
    (prisma.user.findUnique as jest.Mock).mockResolvedValue(mockAdminUser);

    expect(await checkPermission(mockAdminUser.id, 'tenant:create')).toBe(true);
    expect(await checkPermission(mockAdminUser.id, 'user:delete')).toBe(true);
    expect(prisma.user.findUnique).toHaveBeenCalledWith({
      where: { id: mockAdminUser.id },
      include: { role: { include: { permissions: true } } },
    });
  });

  it('admin user should not have permission for disallowed actions', async () => {
    (prisma.user.findUnique as jest.Mock).mockResolvedValue(mockAdminUser);

    expect(await checkPermission(mockAdminUser.id, 'billing:manage')).toBe(false);
  });

  it('member user should have permission for allowed actions', async () => {
    (prisma.user.findUnique as jest.Mock).mockResolvedValue(mockMemberUser);

    expect(await checkPermission(mockMemberUser.id, 'tenant:read')).toBe(true);
    expect(await checkPermission(mockMemberUser.id, 'user:read')).toBe(true);
  });

  it('member user should not have permission for disallowed actions', async () => {
    (prisma.user.findUnique as jest.Mock).mockResolvedValue(mockMemberUser);

    expect(await checkPermission(mockMemberUser.id, 'tenant:create')).toBe(false);
    expect(await checkPermission(mockMemberUser.id, 'user:delete')).toBe(false);
  });

  it('should return false for a non-existent user', async () => {
    (prisma.user.findUnique as jest.Mock).mockResolvedValue(null);

    expect(await checkPermission('non_existent_user_id', 'tenant:read')).toBe(false);
  });

  it('should return false for a user without a role', async () => {
    const userWithoutRole = { ...mockAdminUser, role: null };
    (prisma.user.findUnique as jest.Mock).mockResolvedValue(userWithoutRole);

    expect(await checkPermission(userWithoutRole.id, 'tenant:read')).toBe(false);
  });
});
