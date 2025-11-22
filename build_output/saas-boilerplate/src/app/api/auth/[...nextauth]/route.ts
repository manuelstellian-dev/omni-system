import NextAuth from "next-auth";
import { authOptions } from "@/lib/auth-options";

// NextAuth v5 for App Router exports handlers directly from the object returned by NextAuth()
// The 'handlers' property contains the GET, POST, etc., functions.
const { handlers } = NextAuth(authOptions);

export const GET = handlers.GET;
export const POST = handlers.POST;
// If you have other HTTP methods (PUT, DELETE, etc.) defined in authOptions,
// you would export them similarly: e.g., export const PUT = handlers.PUT;
