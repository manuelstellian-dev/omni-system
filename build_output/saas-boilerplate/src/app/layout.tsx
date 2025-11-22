import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth'; // Assuming authOptions are defined here
import Providers from './providers'; // Assuming this client component exists to wrap SessionProvider

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'saas-boilerplate',
  description: 'A robust SaaS boilerplate built with Next.js, Prisma, Stripe, and NextAuth.js.',
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const session = await getServerSession(authOptions);

  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers session={session}>
          {children}
        </Providers>
      </body>
    </html>
  );
}