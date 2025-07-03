import express from 'express';
import dotenv from 'dotenv';
import cors from 'cors';

import didRoutes from './routes/didRoutes.js';
import anchorRoutes from './routes/anchorRoutes.js';

dotenv.config();

const app = express();
const port = 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Route handlers
app.use(didRoutes);
app.use(anchorRoutes);

// Root endpoint
app.get('/', (req, res) => {
  res.send('Veramo DID Server is running');
});

// Start server
app.listen(port, () => {
  console.log(`Veramo backend running at http://localhost:${port}`);
});
