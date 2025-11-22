import { DashboardShell } from '@/components/ui/dashboard-shell';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { prisma } from '@/lib/prisma';
import { redirect } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { PermissionKey } from '@/lib/rbac/permissions';
import { hasPermission } from '@/lib/rbac/utils';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'; // Assuming Avatar components exist
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'; // Assuming DropdownMenu components exist

export default async function UserManagementPage() {
  const session = await getServerSession(authOptions);

  if (!session?.user || !session.user.tenantId || !session.user.roleId) {
    redirect('/login');
  }

  const tenantId = session.user.tenantId;
  const userRoleId = session.user.roleId;

  const canReadUsers = hasPermission(userRoleId, PermissionKey.USER_READ);
  const canCreateUsers = hasPermission(userRoleId, PermissionKey.USER_CREATE);
  const canUpdateUsers = hasPermission(userRoleId, PermissionKey.USER_UPDATE);
  const canDeleteUsers = hasPermission(userRoleId, PermissionKey.USER_DELETE);
  const canManageRoles = hasPermission(userRoleId, PermissionKey.USER_MANAGE_ROLES);

  if (!canReadUsers) {
    redirect('/dashboard?error=Unauthorized');
  }

  const users = await prisma.user.findMany({
    where: { tenantId: tenantId },
    select: { id: true, name: true, email: true, image: true, role: { select: { name: true } } },
    orderBy: { createdAt: 'asc' },
  });

  return (
    <DashboardShell title="User Management" description="Manage users within your tenant.">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div className="grid gap-1">
            <CardTitle>Users</CardTitle>
            <CardDescription>A list of all users in your tenant.</CardDescription>
          </div>
          {canCreateUsers && <Button>Invite User</Button>}
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {users.length === 0 ? (
              <p className="text-muted-foreground">No users found in this tenant.</p>
            ) : (
              users.map((user) => (
                <div key={user.id} className="flex items-center justify-between p-2 border rounded-md">
                  <div className="flex items-center space-x-4">
                    <Avatar>
                      <AvatarImage src={user.image || undefined} alt={user.name || 'User'} />
                      <AvatarFallback>{user.name?.charAt(0) || user.email.charAt(0)}</AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="font-medium">{user.name || user.email}</p>
                      <p className="text-sm text-muted-foreground">{user.email}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-muted-foreground">{user.role.name}</span>
                    {(canUpdateUsers || canDeleteUsers || canManageRoles) && (
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" className="h-8 w-8 p-0">
                            <span className="sr-only">Open menu</span>
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              className="h-4 w-4"
                            >
                              <circle cx="12" cy="12" r="1" />
                              <circle cx="12" cy="5" r="1" />
                              <circle cx="12" cy="19" r="1" />
                            </svg>
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          {canUpdateUsers && <DropdownMenuItem>Edit User</DropdownMenuItem>}
                          {canManageRoles && <DropdownMenuItem>Change Role</DropdownMenuItem>}
                          {canDeleteUsers && <DropdownMenuItem className="text-red-600">Delete User</DropdownMenuItem>}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </DashboardShell>
  );
}
