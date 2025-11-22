import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { prisma } from '@/lib/prisma';
import { stripe } from '@/lib/stripe'; // Existing Stripe instance
import { GetSubscriptionSchema, CancelSubscriptionSchema, SubscriptionOutputSchema } from '@/schemas/subscription';
import { checkPermissions } from '@/lib/rbac'; // Assuming RBAC utility exists
import { z } from 'zod';

// GET /api/tenants/[tenantId]/subscriptions/[subscriptionId]
// Retrieves a specific subscription for a tenant.
export async function GET(
  req: NextRequest,
  { params }: { params: { tenantId: string; subscriptionId: string } },
): Promise<NextResponse> {
  const session = await getServerSession(authOptions);

  if (!session || !session.user?.email) {
    return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
  }

  const { tenantId, subscriptionId } = params;

  // Validate path parameters using Zod schema
  const validation = GetSubscriptionSchema.safeParse({ tenantId, subscriptionId });
  if (!validation.success) {
    return NextResponse.json({ message: 'Invalid request parameters.', errors: validation.error.flatten() }, { status: 400 });
  }

  // RBAC check: User must be part of the tenant and have permission to read subscriptions
  const hasPermission = await checkPermissions(session, tenantId, ['subscription:read']);
  if (!hasPermission) {
    return NextResponse.json({ message: 'Forbidden: Insufficient permissions or tenant mismatch.' }, { status: 403 });
  }

  try {
    const subscription = await prisma.subscription.findUnique({
      where: {
        id: subscriptionId,
        tenantId: tenantId, // Ensure subscription belongs to the specified tenant
      },
    });

    if (!subscription) {
      return NextResponse.json({ message: 'Subscription not found or does not belong to this tenant.' }, { status: 404 });
    }

    // Validate and return the subscription
    const validatedSubscription = SubscriptionOutputSchema.safeParse(subscription);
    if (!validatedSubscription.success) {
      console.error('[API] Data integrity error: Subscription from DB does not match schema.', validatedSubscription.error);
      return NextResponse.json({ message: 'Internal server error: Data integrity issue.' }, { status: 500 });
    }

    return NextResponse.json(validatedSubscription.data, { status: 200 });
  } catch (error) {
    console.error(`[API] Failed to retrieve subscription ${subscriptionId} for tenant ${tenantId}:`, error);
    return NextResponse.json(
      { message: 'Failed to retrieve subscription.', error: (error as Error).message },
      { status: 500 },
    );
  }
}

// DELETE /api/tenants/[tenantId]/subscriptions/[subscriptionId]
// Cancels a specific subscription for a tenant.
export async function DELETE(
  req: NextRequest,
  { params }: { params: { tenantId: string; subscriptionId: string } },
): Promise<NextResponse> {
  const session = await getServerSession(authOptions);

  if (!session || !session.user?.email) {
    return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
  }

  const { tenantId, subscriptionId } = params;

  // Validate path parameters using Zod schema
  const validation = CancelSubscriptionSchema.safeParse({ tenantId, subscriptionId });
  if (!validation.success) {
    return NextResponse.json({ message: 'Invalid request parameters.', errors: validation.error.flatten() }, { status: 400 });
  }

  // RBAC check: User must be part of the tenant and have permission to cancel subscriptions
  const hasPermission = await checkPermissions(session, tenantId, ['subscription:cancel']);
  if (!hasPermission) {
    return NextResponse.json({ message: 'Forbidden: Insufficient permissions or tenant mismatch.' }, { status: 403 });
  }

  try {
    const subscription = await prisma.subscription.findUnique({
      where: {
        id: subscriptionId,
        tenantId: tenantId, // Ensure subscription belongs to the specified tenant
      },
      select: {
        id: true,
        stripeSubscriptionId: true,
        status: true,
        cancelAtPeriodEnd: true,
      },
    });

    if (!subscription) {
      return NextResponse.json({ message: 'Subscription not found or does not belong to this tenant.' }, { status: 404 });
    }

    if (subscription.status === 'canceled' || subscription.cancelAtPeriodEnd) {
      return NextResponse.json({ message: 'Subscription is already canceled or pending cancellation.' }, { status: 400 });
    }

    // Cancel the subscription in Stripe
    // We set cancel_at_period_end to true to allow the user to finish their current billing cycle.
    // The webhook will handle updating the database when the subscription actually ends.
    const stripeSubscription = await stripe.subscriptions.update(
      subscription.stripeSubscriptionId,
      { cancel_at_period_end: true },
    );

    // Update the database immediately to reflect the user's intent to cancel
    // The webhook will finalize the status change to 'canceled' when the period ends.
    await prisma.subscription.update({
      where: { id: subscription.id },
      data: {
        cancelAtPeriodEnd: stripeSubscription.cancel_at_period_end,
        // Optionally update status to 'pending_cancellation' or similar if desired,
        // but 'cancelAtPeriodEnd: true' is usually sufficient until the webhook fires.
      },
    });

    return NextResponse.json({ message: 'Subscription cancellation initiated successfully. It will be canceled at the end of the current billing period.' }, { status: 200 });
  } catch (error) {
    console.error(`[API] Failed to cancel subscription ${subscriptionId} for tenant ${tenantId}:`, error);
    // Check for specific Stripe errors
    if (error instanceof Error && (error as any).type === 'StripeCardError') {
      return NextResponse.json({ message: 'Stripe error: ' + error.message }, { status: 400 });
    }
    return NextResponse.json(
      { message: 'Failed to cancel subscription.', error: (error as Error).message },
      { status: 500 },
    );
  }
}
