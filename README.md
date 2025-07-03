#  BioDID: Passwordless Biometric Authentication System

This final year project showcases a **passwordless authentication system** using biometrics, decentralized identity (DID), and blockchain. It combines mobile, backend, and decentralized technologies to provide secure login without passwords.

---

## Project Structure

| Folder               | Description                                    |
|----------------------|------------------------------------------------|
| `BioAuth/`           | Flutter mobile app (face + fingerprint login) |
| `bio_auth_backend/`  | Flask backend for biometric processing         |
| `veramo-server/`     | Node.js backend using Veramo for DID & IPFS    |

---

## Tech Stack

- **Flutter**: Mobile app (face/fingerprint capture)
- **Flask**: Biometric verification backend (face & fingerprint templates)
- **Veramo (Node.js)**: DID generation, IPFS upload, Ethereum smart contract
- **Supabase**: User data store and authentication fallback
- **IPFS**: Stores biometric templates
- **Sepolia Ethereum Testnet**: Anchors verification proofs

---

##  How to Run the Project

### 1. Veramo Server (DID + IPFS)

```bash
cd veramo-server/server
npm install
npm app.js
```
### 2. Flask backend
```
cd bio_auth_backend/backend
python app.py
```

### 3. Flutter App
```
cd BioAuth/bio_auth
flutter pub get
flutter run

```
## Pre Requisities
- Must have an existing account through Pinata IPFS Gateway account
- Must have a web wallet for Anchoring data through Sepolia (drip facuet available through https://cloud.google.com/application/web3/faucet/ethereum/sepolia)
- fingerprint dataset (available here https://www.kaggle.com/datasets/ruizgara/socofing)


