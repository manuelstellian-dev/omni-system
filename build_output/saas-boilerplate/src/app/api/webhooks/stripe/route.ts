import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';
import { PrismaClient } from '@prisma/client';
import { stripe, stripeWebhookSecret } from '@/lib/stripe';
import {
  StripeCheckoutSessionSchema,
  StripeSubscriptionSchema,
  convertUnixToDate,
} from '@/lib/stripe-webhook-events';

const prisma = new PrismaClient();

/**
 * Handles Stripe webhook events.
 * This API route is responsible for verifying the webhook signature and processing
 * various Stripe events, primarily related to subscriptions, to update the database.
 *
 * @param req The incoming NextRequest containing the Stripe webhook event.
 * @returns A NextResponse indicating the status of the webhook processing.
 */
export async function POST(req: NextRequest): Promise<NextResponse> {
  const body = await req.text();
  const signature = req.headers.get('stripe-signature');

  // 1. Validate the presence of the Stripe signature header.
  if (!signature) {
    console.error('Stripe webhook: Missing stripe-signature header.');
    return new NextResponse('Missing stripe-signature header', { status: 400 });
  }

  let event: Stripe.Event;

  // 2. Verify the webhook signature to ensure the event is from Stripe and not tampered with.
  try {
    event = stripe.webhooks.constructEvent(body, signature, stripeWebhookSecret);
  } catch (err: unknown) {
    const errorMessage = err instanceof Error ? err.message : 'Unknown error during signature verification';
    console.error(`Stripe webhook: Signature verification failed. ${errorMessage}`);
    return new NextResponse(`Webhook Error: ${errorMessage}`, { status: 400 });
  }

  console.log(`Stripe webhook received: ${event.type}`);

  // 3. Process the Stripe event based on its type.
  try {
    switch (event.type) {
      case 'checkout.session.completed': {
        // Validate the event data against the Zod schema for Checkout Session.
        const parsedSession = StripeCheckoutSessionSchema.safeParse(event.data.object);

        if (!parsedSession.success) {
          console.error('Stripe webhook: Invalid checkout.session.completed data.', parsedSession.error);
          return new NextResponse('Invalid event data', { status: 400 });
        }

        const session = parsedSession.data;

        // Ensure it's a subscription checkout, paid, and completed.
        if (session.mode === 'subscription' && session.payment_status === 'paid' && session.status === 'complete') {
          const subscriptionId = session.subscription;
          const customerId = session.customer;
          // Assuming tenantId is passed in the metadata of the checkout session.
          const tenantId = session.metadata?.tenantId;

          if (!subscriptionId || !customerId || !tenantId) {
            console.error('Stripe webhook: Missing subscriptionId, customerId, or tenantId in checkout session metadata.', { subscriptionId, customerId, tenantId });
            return new NextResponse('Missing required data for subscription', { status: 400 });
          }

          // Retrieve the full subscription object to get price details, as session might not have all details.
          const subscription = await stripe.subscriptions.retrieve(subscriptionId);
          const priceId = subscription.items.data[0]?.price.id;

          if (!priceId) {
            console.error('Stripe webhook: Could not find price ID for subscription.', { subscriptionId });
            return new NextResponse('Could not find price ID for subscription', { status: 400 });
          }

          // Use a Prisma transaction to ensure atomicity when updating Tenant and creating Subscription.
          await prisma.$transaction(async (tx) => {
            // Update the Tenant with the Stripe Customer ID.
            await tx.tenant.update({
              where: { id: tenantId },
              data: { stripeCustomerId: customerId },
            });

            // Create a new Subscription record in the database.
            await tx.subscription.create({
              data: {
                tenantId: tenantId,
                stripeSubscriptionId: subscription.id,
                stripeCustomerId: customerId,
                stripePriceId: priceId,
                status: subscription.status,
                currentPeriodStart: convertUnixToDate(subscription.current_period_start),
                currentPeriodEnd: convertUnixToDate(subscription.current_period_end),
                cancelAtPeriodEnd: subscription.cancel_at_period_end,
              },
            });
          });

          console.log(`Stripe webhook: Subscription ${subscriptionId} created for tenant ${tenantId} with customer ${customerId}.`);
        }
        break;
      }

      case 'customer.subscription.updated':
      case 'customer.subscription.deleted': {
        // Validate the event data against the Zod schema for Subscription.
        const parsedSubscription = StripeSubscriptionSchema.safeParse(event.data.object);

        if (!parsedSubscription.success) {
          console.error('Stripe webhook: Invalid customer.subscription data.', parsedSubscription.error);
          return new NextResponse('Invalid event data', { status: 400 });
        }

        const subscription = parsedSubscription.data;
        const customerId = subscription.customer;
        const priceId = subscription.items.data[0]?.price.id;

        if (!priceId) {
          console.error('Stripe webhook: Could not find price ID for subscription update/delete.', { subscriptionId: subscription.id });
          return new NextResponse('Could not find price ID for subscription', { status: 400 });
        }

        // Find the tenant associated with this Stripe customer ID.
        const tenant = await prisma.tenant.findUnique({
          where: { stripeCustomerId: customerId },
          select: { id: true },
        });

        if (!tenant) {
          console.warn(`Stripe webhook: Tenant not found for customer ID ${customerId}. Skipping subscription update.`);
          // It's possible a customer exists in Stripe but not yet fully linked in our DB, or it's an old customer.
          // Return 200 to Stripe to acknowledge receipt, even if we don't process it further.
          return new NextResponse('Tenant not found', { status: 200 });
        }

        // Update the existing subscription record in the database.
        await prisma.subscription.update({
          where: { stripeSubscriptionId: subscription.id },
          data: {
            tenantId: tenant.id, // Ensure tenantId is linked
            stripeCustomerId: customerId,
            stripePriceId: priceId,
            status: subscription.status,
            currentPeriodStart: convertUnixToDate(subscription.current_period_start),
            currentPeriodEnd: convertUnixToDate(subscription.current_period_end),
            cancelAtPeriodEnd: subscription.cancel_at_period_end,
          },
        });

        console.log(`Stripe webhook: Subscription ${subscription.id} for customer ${customerId} updated/deleted.`);
        break;
      }

      case 'customer.created': {
        // This event can be optionally handled if you need to create a customer record
        // in your database immediately upon Stripe customer creation. For this project,
        // we primarily link the customer ID during the checkout.session.completed event.
        console.log(`Stripe webhook: Customer created event received for customer ${event.data.object.id}.`);
        break;
      }

      default:
        // Log unhandled event types for debugging purposes.
        console.warn(`Stripe webhook: Unhandled event type ${event.type}`);
    }
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error processing event';
    console.error(`Stripe webhook: Error processing event ${event.type}: ${errorMessage}`, error);
    return new NextResponse(`Webhook handler failed: ${errorMessage}`, { status: 500 });
  }

  // 4. Acknowledge receipt of the event to Stripe.
  return new NextResponse('Webhook received', { status: 200 });
}