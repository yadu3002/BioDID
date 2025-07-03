import express from 'express';
import { agent, dbConnection } from '../veramo-setup.js';

const router = express.Router();

// Route to create a new Decentralized Identifier (DID)
router.post('/create-did', async (req, res) => {
  try {
    // Ensure the database is initialized
    if (!dbConnection.isInitialized) {
      console.log("Initializing Veramo database connection...");
      await dbConnection.initialize();
    }

    // Generate a new DID using Veramo agent
    const identifier = await agent.didManagerCreate();
    console.log("DID created:", identifier.did);

    res.json({ did: identifier.did });

  } catch (err) {
    console.error("Error creating DID:", err);
    res.status(500).json({
      message: 'DID creation failed',
      error: err.message,
    });
  }
});

export default router;
