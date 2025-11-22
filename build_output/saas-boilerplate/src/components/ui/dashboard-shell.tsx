import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { redirect } from 'next/navigation';
import Link from 'next/link';
import { TenantSwitcher } from '@/components/dashboard/tenant-switcher';
import { prisma } from '@/lib/prisma';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { signOut } from 'next-auth/react'; // Client-side sign out

interface DashboardShellProps {
  children: React.ReactNode;
  title: string;
  description?: string;
}

export async function DashboardShell({ children, title, description }: DashboardShellProps) {
  const session = await getServerSession(authOptions);

  if (!session?.user || !session.user.tenantId) {
    redirect('/login');
  }

  const currentTenant = await prisma.tenant.findUnique({
    where: { id: session.user.tenantId },
    select: { id: true, name: true, slug: true },
  });

  if (!currentTenant) {
    redirect('/error?message=TenantNotFound');
  }

  // Fetch all tenants the user is associated with for the switcher
  const userTenants = await prisma.tenant.findMany({
    where: { users: { some: { id: session.user.id } } },
    select: { id: true, name: true, slug: true },
    orderBy: { name: 'asc' },
  });

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-40 border-b bg-background">
        <div className="container flex h-16 items-center justify-between py-4">
          <div className="flex items-center space-x-4">
            <Link href="/dashboard" className="font-bold text-lg">
              {currentTenant.name}
            </Link>
            <TenantSwitcher currentTenant={currentTenant} userTenants={userTenants} />
          </div>
          <nav>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={session.user.image || undefined} alt={session.user.name || 'User'} />
                    <AvatarFallback>{session.user.name?.charAt(0) || session.user.email?.charAt(0)}</AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" forceMount>
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">{session.user.name}</p>
                    <p className="text-xs leading-none text-muted-foreground">
                      {session.user.email}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link href="/dashboard/settings">Settings</Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => signOut({ callbackUrl: '/login' })}>
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </nav>
        </div>
      </header>
      <div className="container flex-1 items-start md:grid md:grid-cols-[220px_1fr] md:gap-6 lg:grid-cols-[240px_1fr] lg:gap-10">
        <aside className="fixed top-16 z-30 -ml-2 hidden h-[calc(100vh-4rem)] w-full shrink-0 md:sticky md:block">
          <div className="relative overflow-hidden h-full py-6 pr-6 lg:py-8">
            <nav className="flex flex-col space-y-1">
              <Link
                href="/dashboard"
                className="inline-flex items-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 hover:text-accent-foreground h-9 px-4 py-2 hover:bg-accent hover:text-accent-foreground"
              >
                Dashboard
              </Link>
              <Link
                href="/dashboard/settings"
                className="inline-flex items-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 hover:text-accent-foreground h-9 px-4 py-2 hover:bg-accent hover:text-accent-foreground"
              >
                Tenant Settings
              </Link>
              <Link
                href="/dashboard/users"
                className="inline-flex items-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 hover:text-accent-foreground h-9 px-4 py-2 hover:bg-accent hover:text-accent-foreground"
              >
                User Management
              </Link>
              <Link
                href="/dashboard/billing"
                className="inline-flex items-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 hover:text-accent-foreground h-9 px-4 py-2 hover:bg-accent hover:text-accent-foreground"
              >
                Billing
              </Link>
            </nav>
          </div>
        </aside>
        <main className="relative py-6 lg:gap-10 lg:py-8 xl:grid xl:grid-cols-[1fr_300px]">
          <div className="mx-auto w-full min-w-0">
            <div className="space-y-2">
              <h1 className="text-3xl font-bold tracking-tight md:text-4xl">{title}</h1>
              {description && <p className="text-lg text-muted-foreground">{description}</p>}
            </div>
            <div className="pb-12 pt-8">{children}</div>
          </div>
        </main>
      </div>
    </div>
  );
}
