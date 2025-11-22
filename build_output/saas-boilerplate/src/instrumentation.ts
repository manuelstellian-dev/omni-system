import { initOpenTelemetry } from './lib/observability/otel';

/**
 * This file is a special Next.js file that runs once on server startup.
 * It's the ideal place to initialize server-side-only configurations like OpenTelemetry.
 * @see https://nextjs.org/docs/app/building-your-application/optimizing/instrumentation
 */
export function register(): void {
  // Ensure OpenTelemetry is only initialized in the Node.js runtime (server-side).
  // This prevents it from running in the Edge runtime or client-side environments.
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    initOpenTelemetry();
  }
}
