import Link from 'next/link';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gradient-to-br from-gray-900 to-black text-white">
      <h1 className="text-6xl font-extrabold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600 text-center">
        Welcome to saas-boilerplate
      </h1>
      <p className="text-xl text-gray-300 mb-8 max-w-2xl text-center">
        Your foundation for building robust SaaS applications with Next.js 15, Prisma, Stripe, and NextAuth.js.
      </p>
      <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
        <Link href="/api/auth/signin" className="px-8 py-4 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg shadow-md transition-all duration-300 ease-in-out transform hover:scale-105 text-lg text-center">
          Get Started
        </Link>
        <Link href="https://github.com/your-org/saas-boilerplate" target="_blank" rel="noopener noreferrer" className="px-8 py-4 border border-gray-600 text-gray-300 hover:text-white hover:border-white font-semibold rounded-lg shadow-md transition-all duration-300 ease-in-out transform hover:scale-105 text-lg text-center">
          View on GitHub
        </Link>
      </div>
      <footer className="absolute bottom-8 text-gray-500 text-sm">
        Built with ❤️ for the modern SaaS developer.
      </footer>
    </main>
  );
}