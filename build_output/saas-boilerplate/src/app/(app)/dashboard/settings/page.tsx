import { DashboardShell } from '@/components/ui/dashboard-shell';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { prisma } from '@/lib/prisma';
import { redirect } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input'; // Assuming Input component exists
import { Label } from '@/components/ui/label'; // Assuming Label component exists
import { Button } from '@/components/ui/button'; // Assuming Button component exists
import { PermissionKey } from '@/lib/rbac/permissions'; // Assuming permissions are defined here
import { hasPermission } from '@/lib/rbac/utils'; // Assuming a utility to check permissions
import { z } from 'zod';
import { revalidatePath } from 'next/cache';

const tenantSettingsSchema = z.object({
  name: z.string().min(3, 'Tenant name must be at least 3 characters long.').max(100),
  slug: z.string().min(3, 'Tenant slug must be at least 3 characters long.').max(100).regex(/^[a-z0-9-]+$/, 'Slug can only contain lowercase letters, numbers, and hyphens.').optional(),
});

type TenantSettingsFormState = {
  message: string;
  errors?: { name?: string[]; slug?: string[] };
};

export default async function TenantSettingsPage() {
  const session = await getServerSession(authOptions);

  if (!session?.user || !session.user.tenantId || !session.user.roleId) {
    redirect('/login');
  }

  const tenantId = session.user.tenantId;
  const userRoleId = session.user.roleId;

  const canReadSettings = hasPermission(userRoleId, PermissionKey.TENANT_READ);
  const canUpdateSettings = hasPermission(userRoleId, PermissionKey.TENANT_UPDATE);

  if (!canReadSettings) {
    redirect('/dashboard?error=Unauthorized'); // Redirect if no read permission
  }

  const tenant = await prisma.tenant.findUnique({
    where: { id: tenantId },
    select: { id: true, name: true, slug: true },
  });

  if (!tenant) {
    redirect('/error?message=TenantNotFound');
  }

  const updateTenantAction = async (
    prevState: TenantSettingsFormState,
    formData: FormData
  ): Promise<TenantSettingsFormState> => {
    'use server';

    if (!canUpdateSettings) {
      return { message: 'You do not have permission to update tenant settings.' };
    }

    const name = formData.get('name') as string;
    const slug = formData.get('slug') as string;

    const validatedFields = tenantSettingsSchema.safeParse({ name, slug });

    if (!validatedFields.success) {
      return {
        message: 'Validation failed.',
        errors: validatedFields.error.flatten().fieldErrors,
      };
    }

    try {
      await prisma.tenant.update({
        where: { id: tenantId },
        data: {
          name: validatedFields.data.name,
          slug: validatedFields.data.slug, // Update slug if provided and valid
        },
      });
      revalidatePath('/dashboard/settings');
      return { message: 'Tenant settings updated successfully.' };
    } catch (error) {
      console.error('Failed to update tenant settings:', error);
      return { message: 'Failed to update tenant settings. Please try again.' };
    }
  };

  return (
    <DashboardShell title="Tenant Settings" description="Manage your tenant's general information.">
      <Card>
        <CardHeader>
          <CardTitle>General Settings</CardTitle>
          <CardDescription>Update your tenant's name and slug.</CardDescription>
        </CardHeader>
        <CardContent>
          <form action={updateTenantAction} className="space-y-4">
            <div className="grid gap-2">
              <Label htmlFor="name">Tenant Name</Label>
              <Input
                id="name"
                name="name"
                type="text"
                defaultValue={tenant.name}
                disabled={!canUpdateSettings}
              />
              {/* {state?.errors?.name && (
                <p className="text-sm text-red-500">{state.errors.name.join(', ')}</p>
              )} */}
            </div>
            <div className="grid gap-2">
              <Label htmlFor="slug">Tenant Slug</Label>
              <Input
                id="slug"
                name="slug"
                type="text"
                defaultValue={tenant.slug}
                disabled={!canUpdateSettings}
              />
              {/* {state?.errors?.slug && (
                <p className="text-sm text-red-500">{state.errors.slug.join(', ')}</p>
              )} */}
            </div>
            {canUpdateSettings && (
              <Button type="submit">Save Changes</Button>
            )}
            {/* {state?.message && <p className="text-sm text-green-500">{state.message}</p>} */}
          </form>
        </CardContent>
      </Card>
    </DashboardShell>
  );
}
