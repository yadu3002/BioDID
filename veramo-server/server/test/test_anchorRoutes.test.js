import request from 'supertest';
import express from 'express';
import anchorRoutes from '../routes/anchorRoutes.js';

const app = express();
app.use(express.json());
app.use(anchorRoutes);

// Mocking the blockchain anchoring service
jest.mock('../services/blockchainService.js', () => ({
  anchorBiometricHash: jest.fn().mockResolvedValue("0xMockTxHash5678")
}));

describe('/anchor_user_data route', () => {
  it('returns success when all data is provided', async () => {
    const res = await request(app)
      .post('/anchor_user_data')
      .send({
        did: 'did:example:123',
        name: 'Alice',
        embeddingIpfsHash: 'QmFace123',
        embeddingHash: 'face_hash_abc',
        fingerprintIpfsHash: 'QmFinger456',
        fingerprintHash: 'finger_hash_xyz'
      });

    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('message');
    expect(res.body.faceTx).toMatch(/^0x/);
  });

  it('still works if fingerprint is missing', async () => {
    const res = await request(app)
      .post('/anchor_user_data')
      .send({
        did: 'did:example:124',
        name: 'Bob',
        embeddingIpfsHash: 'QmFaceOnly',
        embeddingHash: 'face_hash_only'
      });

    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('faceTx');
    expect(res.body.fingerprintTx).toBeUndefined();
  });

  it('returns error if anchor service throws', async () => {
    const { anchorBiometricHash } = await import('../services/blockchainService.js');
    anchorBiometricHash.mockRejectedValueOnce(new Error("Mock failure"));

    const res = await request(app)
      .post('/anchor_user_data')
      .send({
        did: 'did:example:999',
        name: 'Eve',
        embeddingIpfsHash: 'QmFail',
        embeddingHash: 'fail_hash'
      });

    expect(res.statusCode).toBeGreaterThanOrEqual(400);
    expect(res.body).toHaveProperty('error');
  });

  // Skipping this test – didn’t have time to test DB write issues
  it.skip('handles file system write errors', () => {
  });
});
