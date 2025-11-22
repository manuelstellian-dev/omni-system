import { NextResponse } from 'next/server';
// import { auth } from "@/lib/auth"; // Uncomment if you need session in API routes
import { prisma } from "@/lib/db"; // Assuming your Prisma client is exported from here
import { z } from 'zod'; // For input validation

// Define the context type for API routes with dynamic segments
interface RouteContext {
  params: {
    tenantId: string;
  };
}

// Zod schema for tenant ID validation
const tenantIdSchema = z.string().uuid("Invalid tenant ID format.");

// Zod schema for PATCH request body (example)
const updateTenantSchema = z.object({
  name: z.string().min(1, "Tenant name cannot be empty.").optional(),
  // Add other updatable fields here
});

export async function GET(request: Request, context: RouteContext) {
  // Optional: Add authentication/authorization check
  // const session = await auth();
  // if (!session) {
  //   return new NextResponse("Unauthorized", { status: 401 });
  // }

  const validation = tenantIdSchema.safeParse(context.params.tenantId);
  if (!validation.success) {
    return new NextResponse(validation.error.errors[0].message, { status: 400 });
  }
  const tenantId = validation.data;

  try {
    const tenant = await prisma.tenant.findUnique({
      where: { id: tenantId },
    });

    if (!tenant) {
      return new NextResponse("Tenant not found", { status: 404 });
    }

    return NextResponse.json(tenant);
  } catch (error) {
    console.error("[TENANT_GET_ERROR]", error);
    return new NextResponse("Internal Server Error", { status: 500 });
  }
}

export async function DELETE(request: Request, context: RouteContext) {
  // Optional: Add authentication/authorization check
  // const session = await auth();
  // if (!session) {
  //   return new NextResponse("Unauthorized", { status: 401 });
  // }

  const validation = tenantIdSchema.safeParse(context.params.tenantId);
  if (!validation.success) {
    return new NextResponse(validation.error.errors[0].message, { status: 400 });
  }
  const tenantId = validation.data;

  try {
    await prisma.tenant.delete({
      where: { id: tenantId },
    });

    return new NextResponse(null, { status: 204 }); // No content
  } catch (error) {
    console.error("[TENANT_DELETE_ERROR]", error);
    // Handle specific Prisma errors if needed, e.g., P2025 for not found
    return new NextResponse("Internal Server Error", { status: 500 });
  }
}

export async function PATCH(request: Request, context: RouteContext) {
  // Optional: Add authentication/authorization check
  // const session = await auth();
  // if (!session) {
  //   return new NextResponse("Unauthorized", { status: 401 });
  // }

  const validation = tenantIdSchema.safeParse(context.params.tenantId);
  if (!validation.success) {
    return new NextResponse(validation.error.errors[0].message, { status: 400 });
  }
  const tenantId = validation.data;

  try {
    const body = await request.json();
    const parsedBody = updateTenantSchema.safeParse(body);

    if (!parsedBody.success) {
      return new NextResponse(parsedBody.error.errors[0].message, { status: 400 });
    }

    const updatedTenant = await prisma.tenant.update({
      where: { id: tenantId },
      data: parsedBody.data,
    });

    return NextResponse.json(updatedTenant);
  } catch (error) {
    console.error("[TENANT_PATCH_ERROR]", error);
    return new NextResponse("Internal Server Error", { status: 500 });
  }
}
