import { NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import { prisma } from '@/lib/prisma'; // Assuming prisma client is exported from here
import { authOptions } from '@/lib/auth-options'; // Assuming authOptions are exported from here
import { User } from '@prisma/client';

// Mock the entire authOptions module to control its behavior
// This is useful if authOptions has complex dependencies or external calls
// For this test, we'll directly test the credentials provider logic within authOptions.

describe('Authentication Credentials Provider', () => {
  const mockUser: User = {
    id: 'user123',
    name: 'Test User',
    email: 'test@example.com',
    emailVerified: new Date(),
    image: null,
    password: 'hashedpassword123', // In a real app, this would be a hash
    tenantId: 'tenant1',
    roleId: 'role1',
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  // Find the CredentialsProvider from the authOptions
  const credentialsProvider = authOptions.providers.find(
    (provider) => provider.id === 'credentials'
  ) as CredentialsProvider;

  if (!credentialsProvider) {
    throw new Error('CredentialsProvider not found in authOptions');
  }

  const authorizeFn = credentialsProvider.authorize;

  it('should return a user with valid credentials', async () => {
    // Mock prisma.user.findUnique to return a user
    (prisma.user.findUnique as jest.Mock).mockResolvedValue(mockUser);

    // Mock the password comparison. In a real app, this would be bcrypt.compare
    // For this test, we'll simulate the placeholder logic from src/lib/auth-options.ts
    // where `password === user.password` is used.
    const user = await authorizeFn(
      { email: 'test@example.com', password: 'hashedpassword123' },
      {} as any // Mock the request object if needed
    );

    expect(prisma.user.findUnique).toHaveBeenCalledWith({
      where: { email: 'test@example.com' },
    });
    expect(user).toEqual(expect.objectContaining({
      id: mockUser.id,
      email: mockUser.email,
      name: mockUser.name,
    }));
  });

  it('should return null for invalid password', async () => {
    (prisma.user.findUnique as jest.Mock).mockResolvedValue(mockUser);

    const user = await authorizeFn(
      { email: 'test@example.com', password: 'wrongpassword' },
      {} as any
    );

    expect(prisma.user.findUnique).toHaveBeenCalledWith({
      where: { email: 'test@example.com' },
    });
    expect(user).toBeNull();
  });

  it('should return null for non-existent user', async () => {
    (prisma.user.findUnique as jest.Mock).mockResolvedValue(null);

    const user = await authorizeFn(
      { email: 'nonexistent@example.com', password: 'anypassword' },
      {} as any
    );

    expect(prisma.user.findUnique).toHaveBeenCalledWith({
      where: { email: 'nonexistent@example.com' },
    });
    expect(user).toBeNull();
  });

  it('should return null if email is not provided', async () => {
    const user = await authorizeFn(
      { email: '', password: 'anypassword' },
      {} as any
    );

    expect(prisma.user.findUnique).not.toHaveBeenCalled(); // Should not query DB without email
    expect(user).toBeNull();
  });

  it('should return null if password is not provided', async () => {
    (prisma.user.findUnique as jest.Mock).mockResolvedValue(mockUser);

    const user = await authorizeFn(
      { email: 'test@example.com', password: '' },
      {} as any
    );

    expect(prisma.user.findUnique).toHaveBeenCalledWith({
      where: { email: 'test@example.com' },
    });
    expect(user).toBeNull();
  });
});
