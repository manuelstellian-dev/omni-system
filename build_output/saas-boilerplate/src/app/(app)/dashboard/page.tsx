// src/app/(app)/dashboard/page.tsx
import { DashboardShell } from '@/components/ui/dashboard-shell';
import { getServerSession } from 'next-auth'; // Correct v4 import
import { authOptions } from '@/lib/auth'; // Import authOptions
import { prisma } from '@/lib/prisma';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { userHasPermission } from '@/lib/rbac/utils';
import { Permissions } from '@/lib/rbac/permissions';

export default async function DashboardPage() {
  const session = await getServerSession(authOptions); // Pass authOptions to getServerSession

  if (!session?.user) {
    // Handle unauthenticated state, e.g., redirect to login or show a message
    return (
      <DashboardShell title="Dashboard" description="Access denied.">
        <p>Please log in to view your dashboard.</p>
      </DashboardShell>
    );
  }

  // Example usage of session and permissions (assuming user.role is available)
  const canViewBilling = userHasPermission(session.user, Permissions.VIEW_BILLING);

  return (
    <DashboardShell title="Dashboard" description="Manage your account and subscriptions.">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Welcome, {session.user.name || session.user.email}!</CardTitle>
            <CardDescription>Your current role: {session.user.role || 'User'}</CardDescription>
          </CardHeader>
          <CardContent>
            <p>This is your personalized dashboard.</p>
            {canViewBilling && (
              <Button className="mt-4">Go to Billing</Button>
            )}
          </CardContent>
        </Card>
        {/* Add more dashboard components or content here */}
      </div>
    </DashboardShell>
  );
}
