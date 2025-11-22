import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { prisma } from '@/lib/prisma';
import { ListSubscriptionsSchema, SubscriptionOutputSchema } from '@/schemas/subscription';
import { checkPermissions } from '@/lib/rbac'; // Assuming RBAC utility exists
import { z } from 'zod';

// GET /api/tenants/[tenantId]/subscriptions
// Retrieves all subscriptions for a specific tenant.
export async function GET(
  req: NextRequest,
  { params }: { params: { tenantId: string } },
): Promise<NextResponse> {
  const session = await getServerSession(authOptions);

  if (!session || !session.user?.email) {
    return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
  }

  const { tenantId } = params;

  // Validate tenantId format using Zod schema
  const validation = ListSubscriptionsSchema.safeParse({ tenantId });
  if (!validation.success) {
    return NextResponse.json({ message: 'Invalid tenant ID format.', errors: validation.error.flatten() }, { status: 400 });
  }

  // RBAC check: User must be part of the tenant and have permission to read subscriptions
  const hasPermission = await checkPermissions(session, tenantId, ['subscription:read']);
  if (!hasPermission) {
    return NextResponse.json({ message: 'Forbidden: Insufficient permissions or tenant mismatch.' }, { status: 403 });
  }

  try {
    const subscriptions = await prisma.subscription.findMany({
      where: { tenantId: tenantId },
      orderBy: { createdAt: 'desc' },
    });

    // Validate and return the subscriptions
    const validatedSubscriptions = z.array(SubscriptionOutputSchema).safeParse(subscriptions);
    if (!validatedSubscriptions.success) {
      console.error('[API] Data integrity error: Subscriptions from DB do not match schema.', validatedSubscriptions.error);
      // For "Opinionated Excellence", we should ensure data integrity.
      return NextResponse.json({ message: 'Internal server error: Data integrity issue.' }, { status: 500 });
    }

    return NextResponse.json(validatedSubscriptions.data, { status: 200 });
  } catch (error) {
    console.error(`[API] Failed to retrieve subscriptions for tenant ${tenantId}:`, error);
    return NextResponse.json(
      { message: 'Failed to retrieve subscriptions.', error: (error as Error).message },
      { status: 500 },
    );
  }
}
