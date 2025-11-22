import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma'; // Assuming prisma client is exported from here
import { Tenant } from '@prisma/client';
import { POST as createTenantApi } from '@/app/api/tenants/route'; // Assuming tenant creation API is here
import { GET as getTenantApi } from '@/app/api/tenants/[slug]/route'; // Assuming tenant retrieval API is here

// Helper to create a mock NextRequest
const mockRequest = (method: string, body?: Record<string, unknown>, params?: Record<string, string>) => {
  const req = new NextRequest('http://localhost/api/tenants', {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  }) as any; // Cast to any to allow adding params

  if (params) {
    req.params = params;
  }
  return req;
};

describe('Tenant API Endpoints', () => {
  const mockTenant: Tenant = {
    id: 'tenant123',
    name: 'Test Tenant',
    slug: 'test-tenant',
    stripeCustomerId: null,
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  describe('POST /api/tenants', () => {
    it('should create a new tenant successfully', async () => {
      (prisma.tenant.findUnique as jest.Mock).mockResolvedValue(null); // No existing tenant
      (prisma.tenant.create as jest.Mock).mockResolvedValue(mockTenant);

      const request = mockRequest('POST', { name: 'Test Tenant', slug: 'test-tenant' });
      const response = await createTenantApi(request);

      expect(response.status).toBe(201);
      const data = await response.json();
      expect(data).toEqual(expect.objectContaining({
        id: mockTenant.id,
        name: mockTenant.name,
        slug: mockTenant.slug,
      }));
      expect(prisma.tenant.create).toHaveBeenCalledWith({
        data: { name: 'Test Tenant', slug: 'test-tenant' },
      });
    });

    it('should return 409 if tenant slug already exists', async () => {
      (prisma.tenant.findUnique as jest.Mock).mockResolvedValue(mockTenant); // Tenant already exists

      const request = mockRequest('POST', { name: 'Another Tenant', slug: 'test-tenant' });
      const response = await createTenantApi(request);

      expect(response.status).toBe(409);
      const data = await response.json();
      expect(data).toEqual({ error: 'Tenant with this slug already exists.' });
      expect(prisma.tenant.create).not.toHaveBeenCalled();
    });

    it('should return 400 for invalid input', async () => {
      const request = mockRequest('POST', { name: '', slug: 'invalid' }); // Empty name
      const response = await createTenantApi(request);

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty('error');
      expect(prisma.tenant.create).not.toHaveBeenCalled();
    });
  });

  describe('GET /api/tenants/[slug]', () => {
    it('should retrieve a tenant by slug successfully', async () => {
      (prisma.tenant.findUnique as jest.Mock).mockResolvedValue(mockTenant);

      const request = mockRequest('GET', undefined, { slug: 'test-tenant' });
      const response = await getTenantApi(request, { params: { slug: 'test-tenant' } });

      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data).toEqual(expect.objectContaining({
        id: mockTenant.id,
        name: mockTenant.name,
        slug: mockTenant.slug,
      }));
      expect(prisma.tenant.findUnique).toHaveBeenCalledWith({
        where: { slug: 'test-tenant' },
      });
    });

    it('should return 404 if tenant not found', async () => {
      (prisma.tenant.findUnique as jest.Mock).mockResolvedValue(null);

      const request = mockRequest('GET', undefined, { slug: 'non-existent' });
      const response = await getTenantApi(request, { params: { slug: 'non-existent' } });

      expect(response.status).toBe(404);
      const data = await response.json();
      expect(data).toEqual({ error: 'Tenant not found.' });
    });

    it('should return 400 if slug is missing', async () => {
      const request = mockRequest('GET');
      const response = await getTenantApi(request, { params: { slug: '' } }); // Missing slug

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toEqual({ error: 'Tenant slug is required.' });
    });
  });
});
