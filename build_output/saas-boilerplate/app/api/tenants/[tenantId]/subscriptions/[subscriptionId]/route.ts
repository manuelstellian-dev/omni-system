import { NextRequest, NextResponse } from 'next/server';
import { SubscriptionRouteContext } from '@/types/next-api'; // Import the explicit context type

// Example GET handler for /api/tenants/[tenantId]/subscriptions/[subscriptionId]
export async function GET(
  request: NextRequest,
  context: SubscriptionRouteContext // Explicitly type the context parameter
) {
  const { tenantId, subscriptionId } = context.params;
  // Your existing GET logic here
  return NextResponse.json({ tenantId, subscriptionId, message: `GET subscription ${subscriptionId} for tenant ${tenantId}` });
}

// Example DELETE handler for /api/tenants/[tenantId]/subscriptions/[subscriptionId]
export async function DELETE(
  request: NextRequest,
  context: SubscriptionRouteContext // Explicitly type the context parameter
) {
  const { tenantId, subscriptionId } = context.params;
  // Your existing DELETE logic here
  return NextResponse.json({ tenantId, subscriptionId, message: `DELETE subscription ${subscriptionId} for tenant ${tenantId}` });
}
