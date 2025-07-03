import { createAgent } from '@veramo/core';
import { KeyManager } from '@veramo/key-manager';
import { KeyManagementSystem, SecretBox } from '@veramo/kms-local';
import { DIDManager } from '@veramo/did-manager';
import { EthrDIDProvider } from '@veramo/did-provider-ethr';
import { DataStore, DataStoreORM, Entities } from '@veramo/data-store';
import { DIDResolverPlugin } from '@veramo/did-resolver';
import { getResolver as getEthrResolver } from 'ethr-did-resolver';
import { Resolver } from 'did-resolver';
import {
  KeyStore,
  DIDStore,
  PrivateKeyStore,
  migrations,
} from '@veramo/data-store';

import { DataSource } from 'typeorm';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

dotenv.config();

// Set up database path for SQLite
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const dbPath = path.join(__dirname, 'veramo.sqlite');

// Configure TypeORM SQLite connection
const dbConnection = new DataSource({
  type: 'sqlite',
  database: dbPath,
  synchronize: false,
  migrations,
  migrationsRun: true,
  logging: false,
  entities: Entities,
});

const secretKey = process.env.SECRET_KEY;

// Create Veramo agent with core plugins
const agent = createAgent({
  plugins: [
    // Handles key management using local KMS
    new KeyManager({
      store: new KeyStore(dbConnection),
      kms: {
        local: new KeyManagementSystem(
          new PrivateKeyStore(dbConnection, new SecretBox(secretKey))
        ),
      },
    }),

    // DID management (create/store/resolve) using Ethr provider on Sepolia
    new DIDManager({
      store: new DIDStore(dbConnection),
      defaultProvider: 'did:ethr:sepolia',
      providers: {
        'did:ethr:sepolia': new EthrDIDProvider({
          defaultKms: 'local',
          network: 'sepolia',
          rpcUrl: `https://sepolia.infura.io/v3/${process.env.INFURA_PROJECT_ID}`,
        }),
      },
    }),

    // DID resolution using did-resolver and ethr-did-resolver
    new DIDResolverPlugin({
      resolver: new Resolver({
        ...getEthrResolver({
          networks: [
            {
              name: 'sepolia',
              rpcUrl: `https://sepolia.infura.io/v3/${process.env.INFURA_PROJECT_ID}`,
            },
          ],
        }),
      }),
    }),

    // Veramo data store plugins for credentials and messaging
    new DataStore(dbConnection),
    new DataStoreORM(dbConnection),
  ],
});

export { agent, dbConnection };
