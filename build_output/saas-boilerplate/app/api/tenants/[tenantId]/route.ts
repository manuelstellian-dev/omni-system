import { NextRequest, NextResponse } from 'next/server';
import { TenantRouteContext } from '@/types/next-api'; // Import the explicit context type

// Example GET handler for /api/tenants/[tenantId]
export async function GET(
  request: NextRequest,
  context: TenantRouteContext // Explicitly type the context parameter
) {
  const { tenantId } = context.params;
  // Your existing GET logic here
  return NextResponse.json({ tenantId, message: `GET tenant ${tenantId}` });
}

// Example DELETE handler for /api/tenants/[tenantId]
export async function DELETE(
  request: NextRequest,
  context: TenantRouteContext // Explicitly type the context parameter
) {
  const { tenantId } = context.params;
  // Your existing DELETE logic here
  return NextResponse.json({ tenantId, message: `DELETE tenant ${tenantId}` });
}

// Example PATCH handler for /api/tenants/[tenantId]
export async function PATCH(
  request: NextRequest,
  context: TenantRouteContext // Explicitly type the context parameter
) {
  const { tenantId } = context.params;
  // Your existing PATCH logic here
  return NextResponse.json({ tenantId, message: `PATCH tenant ${tenantId}` });
}
