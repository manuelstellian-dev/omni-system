import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth'; // Assuming authOptions is defined here
import { prisma } from '@/lib/prisma'; // Assuming prisma client is exported from here
import { createStripeCheckoutSession } from '@/lib/stripe-billing'; // Existing utility
import { CreateCheckoutSessionSchema } from '@/schemas/subscription'; // New schema
import { checkPermissions } from '@/lib/rbac'; // Assuming RBAC utility exists

// POST /api/tenants/[tenantId]/subscriptions/checkout
// Initiates a Stripe Checkout Session for a new subscription.
export async function POST(
  req: NextRequest,
  { params }: { params: { tenantId: string } },
): Promise<NextResponse> {
  const session = await getServerSession(authOptions);

  if (!session || !session.user?.email) {
    return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
  }

  const { tenantId } = params;

  // Validate tenantId format (CUIDs typically start with 'cl')
  if (!tenantId || !tenantId.startsWith('cl')) {
    return NextResponse.json({ message: 'Invalid tenant ID format.' }, { status: 400 });
  }

  // RBAC check: User must be part of the tenant and have permission to create subscriptions
  const hasPermission = await checkPermissions(session, tenantId, ['subscription:create']);
  if (!hasPermission) {
    return NextResponse.json({ message: 'Forbidden: Insufficient permissions or tenant mismatch.' }, { status: 403 });
  }

  let body;
  try {
    body = await req.json();
  } catch (error) {
    return NextResponse.json({ message: 'Invalid JSON body.' }, { status: 400 });
  }

  const validation = CreateCheckoutSessionSchema.safeParse(body);

  if (!validation.success) {
    return NextResponse.json({ message: 'Invalid request body.', errors: validation.error.flatten() }, { status: 400 });
  }

  const { priceId } = validation.data;

  try {
    // Retrieve the tenant to ensure it exists and get customer details if available
    const tenant = await prisma.tenant.findUnique({
      where: { id: tenantId },
      select: { id: true, name: true, stripeCustomerId: true },
    });

    if (!tenant) {
      return NextResponse.json({ message: 'Tenant not found.' }, { status: 404 });
    }

    // Use the existing utility to create the Stripe Checkout Session
    const checkoutSessionUrl = await createStripeCheckoutSession(
      tenant.id,
      priceId,
      session.user.email, // Use the authenticated user's email
    );

    return NextResponse.json({ url: checkoutSessionUrl }, { status: 200 });
  } catch (error) {
    console.error(`[API] Failed to create Stripe Checkout Session for tenant ${tenantId}:`, error);
    return NextResponse.json(
      { message: 'Failed to initiate subscription checkout.', error: (error as Error).message },
      { status: 500 },
    );
  }
}
