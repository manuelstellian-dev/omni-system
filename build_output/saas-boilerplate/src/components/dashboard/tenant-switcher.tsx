"use client";

import * as React from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { ChevronDownIcon } from '@heroicons/react/20/solid'; // Assuming Heroicons are available or replace with custom SVG

interface Tenant {
  id: string;
  name: string;
  slug: string;
}

interface TenantSwitcherProps {
  currentTenant: Tenant;
  userTenants: Tenant[];
}

export function TenantSwitcher({ currentTenant, userTenants }: TenantSwitcherProps) {
  const router = useRouter();
  const pathname = usePathname();

  const onTenantSelect = (tenantSlug: string) => {
    // This assumes a URL structure like /<tenant-slug>/dashboard or that a server action
    // would update the session's active tenant and then redirect.
    // For this task, we'll simulate a redirect to the dashboard with the new tenant slug.
    // In a real multi-tenant app, the tenant slug might be part of the URL, e.g., /<tenant-slug>/dashboard
    // Or, a server action would update the session and then revalidate/redirect.
    // Given the current (app)/dashboard structure, we'll just redirect to the main dashboard
    // and assume the session context will be updated by a server action or middleware.
    // For now, we'll just log and redirect to the main dashboard.
    console.log(`Switching to tenant: ${tenantSlug}`);
    // A more robust solution would involve a server action to update the active tenant in the session
    // and then a client-side redirect or revalidation.
    // For demonstration, we'll just redirect to the main dashboard path.
    // If the app supported /<tenant-slug>/dashboard, it would be router.push(`/${tenantSlug}/dashboard`);
    router.push('/dashboard');
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" role="combobox" aria-expanded={false} className="w-[200px] justify-between">
          {currentTenant.name}
          <ChevronDownIcon className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-[200px]">
        {userTenants.map((tenant) => (
          <DropdownMenuItem
            key={tenant.id}
            onSelect={() => onTenantSelect(tenant.slug)}
            className="cursor-pointer"
          >
            {tenant.name}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
