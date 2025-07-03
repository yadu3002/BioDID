import request from 'supertest';
import express from 'express';
import didRoutes from '../routes/didRoutes.js';

const app = express();
app.use(express.json());
app.use(didRoutes);

// Mock Veramo setup
jest.mock('../veramo-setup.js', () => ({
  dbConnection: { isInitialized: true },
  agent: {
    didManagerCreate: jest.fn().mockResolvedValue({
      did: 'did:example:xyz123',
    }),
  },
}));

describe('/create-did route', () => {
  it('returns a DID if successful', async () => {
    const res = await request(app).post('/create-did');
    expect(res.statusCode).toBe(200);
    expect(res.body.did).toMatch(/^did:/);
  });

  it.skip('returns error if agent fails [not implemented]', () => {
  });
});
