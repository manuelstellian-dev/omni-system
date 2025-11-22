# Multi-stage Dockerfile for production builds of the Next.js application.
# Utilizes Next.js's standalone output for a highly optimized and self-contained image.

# Stage 1: Dependency Installation and Application Build
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Install pnpm globally for efficient dependency management
# OMNI: Using npm as per package.json context, but pnpm is often preferred for monorepos/performance.
# Sticking to npm for consistency with existing package.json scripts.

# Copy package.json and package-lock.json to leverage Docker cache
COPY package.json package-lock.json ./

# Install dependencies
# Use npm ci for clean installs in CI/CD and Docker builds
RUN npm ci

# Copy the rest of the application source code
COPY . .

# Generate Prisma client
# This is crucial for the application to interact with the database
RUN npx prisma generate

# Build the Next.js application
# Assumes 'output: "standalone"' is configured in next.config.js for optimal Docker builds
RUN npm run build

# Stage 2: Production Runtime Image
FROM node:20-alpine AS runner

# Set environment variables for production
ENV NODE_ENV production

# Create a non-root user for security best practices
RUN addgroup --system --gid 1001 nextjs
RUN adduser --system --uid 1001 nextjs

# Set working directory
WORKDIR /app

# Copy standalone output from the builder stage
# This includes .next/standalone, public, and node_modules required for runtime
COPY --from=builder --chown=nextjs:nextjs /app/.next/standalone ./.
COPY --from=builder --chown=nextjs:nextjs /app/public ./public

# Copy Prisma schema and generated client for runtime access
# The generated client is typically within node_modules/.prisma/client, which is part of standalone
# However, copying schema.prisma explicitly can be useful for debugging or specific Prisma commands if needed
COPY --from=builder --chown=nextjs:nextjs /app/prisma/schema.prisma ./prisma/schema.prisma

# Expose the port Next.js runs on
EXPOSE 3000

# Set the user to the non-root user
USER nextjs

# Start the Next.js production server
# The standalone output generates a server.js file that can be run directly
CMD ["node", "server.js"]
