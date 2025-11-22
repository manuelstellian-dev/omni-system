import { z } from 'zod';

// Schema for creating a Stripe Checkout Session
export const CreateCheckoutSessionSchema = z.object({
  priceId: z.string().min(1, 'Stripe Price ID is required.'),
});

export type CreateCheckoutSessionInput = z.infer<typeof CreateCheckoutSessionSchema>;

// Schema for retrieving a single subscription
export const GetSubscriptionSchema = z.object({
  tenantId: z.string().cuid('Invalid tenant ID format.'),
  subscriptionId: z.string().cuid('Invalid subscription ID format.'),
});

export type GetSubscriptionInput = z.infer<typeof GetSubscriptionSchema>;

// Schema for cancelling a subscription
export const CancelSubscriptionSchema = z.object({
  tenantId: z.string().cuid('Invalid tenant ID format.'),
  subscriptionId: z.string().cuid('Invalid subscription ID format.'),
});

export type CancelSubscriptionInput = z.infer<typeof CancelSubscriptionSchema>;

// Schema for listing subscriptions (no specific body, just path params)
export const ListSubscriptionsSchema = z.object({
  tenantId: z.string().cuid('Invalid tenant ID format.'),
});

export type ListSubscriptionsInput = z.infer<typeof ListSubscriptionsSchema>;

// Schema for the Subscription model output (optional, but good for consistency)
export const SubscriptionOutputSchema = z.object({
  id: z.string().cuid(),
  tenantId: z.string().cuid(),
  stripeSubscriptionId: z.string(),
  stripeCustomerId: z.string(),
  stripePriceId: z.string(),
  status: z.string(),
  currentPeriodStart: z.date(),
  currentPeriodEnd: z.date(),
  cancelAtPeriodEnd: z.boolean(),
  createdAt: z.date(),
  updatedAt: z.date(),
});

export type SubscriptionOutput = z.infer<typeof SubscriptionOutputSchema>;
