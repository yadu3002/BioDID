import express from 'express';
import fs from 'fs';
import { anchorBiometricHash } from '../services/blockchainService.js';

const router = express.Router();
const USERS_PATH = './users.json';

// Handles biometric anchoring and user storage
router.post('/anchor_user_data', async (req, res) => {
  const {
    did,
    name,
    embeddingIpfsHash,
    embeddingHash,
    fingerprintIpfsHash,
    fingerprintHash
  } = req.body;

  console.log("Received data for anchoring:", JSON.stringify(req.body, null, 2));

  try {
    // Call smart contract to anchor user data on-chain
    const faceTx = await anchorBiometricHash({
      did,
      faceIPFSHash: embeddingIpfsHash,
      faceTemplateHash: embeddingHash,
      fingerprintIPFSHash: fingerprintIpfsHash || "",
      fingerprintHash: fingerprintHash || ""
    });

    // Prepare new user record
    const newUser = {
      did,
      name,
      embeddingIpfsHash,
      faceTemplateHash: embeddingHash,
      fingerprintIpfsHash: fingerprintIpfsHash || null,
      fingerprintHash: fingerprintHash || null,
      anchoredTx: faceTx,
      createdAt: new Date().toISOString()
    };

    // Load existing users, append new user, and write back to file
    const users = fs.existsSync(USERS_PATH)
      ? JSON.parse(fs.readFileSync(USERS_PATH))
      : [];

    users.push(newUser);
    fs.writeFileSync(USERS_PATH, JSON.stringify(users, null, 2));

    res.json({ message: 'Anchored successfully', faceTx });
  } catch (error) {
    console.error("Anchoring failed:", error);
    res.status(500).json({ error: 'Anchoring failed' });
  }
});

export default router;
