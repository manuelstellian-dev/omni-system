# OMNI CAPABILITIES & FEATURE SET

## 1. THE "GOD-MODE" SCAFFOLD
When the user requests a stack, OMNI provides an enterprise-grade foundation instantly:
* **Next.js 15 (App Router)** with Server Actions.
* **Strict TypeScript:** No `any` types allowed.
* **Authentication:** Auth.js or Clerk (pre-configured).
* **Database:** PostgreSQL + Prisma/Drizzle (with migrations auto-run).
* **Validation:** Zod schemas for both API inputs and Frontend forms.
* **Payments:** Stripe subscription boilerplate (webhooks pre-wired).
* **Email:** Resend/React-Email templates integrated.

## 2. INTELLIGENT EVOLUTION
OMNI allows iterative development:
* **Command:** "Add a blog feature."
* **Action:** OMNI understands it needs to update the Prisma schema, create new API routes, generate UI pages, and update the navigation bar. It does not just "write a file"; it "integrates a feature".

## 3. DEPLOYMENT AUTOMATION
OMNI does not leave code on localhost.
* **Infrastructure as Code:** Generates Terraform or Pulumi stacks.
* **CI/CD:** Writes GitHub Actions for testing, linting, and deploying.
* **Preview:** Can spin up a Docker container locally and expose it via tunnel (ngrok) for immediate user review.

## 4. DOCUMENTATION ENGINE
* **Auto-Readme:** Generates a perfect README.md with setup instructions.
* **ADR Generation:** Architecture Decision Records are created automatically when major tech choices are made.
* **API Docs:** Auto-generates Swagger/OpenAPI specs from the code.

## 5. ERROR EXTERMINATION
* If the user pastes a stack trace, OMNI doesn't just explain it. It parses the trace, locates the file, applies the fix, runs the build to verify, and commits the result.