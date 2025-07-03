import { ethers } from 'ethers';
import dotenv from 'dotenv';

dotenv.config();

const CONTRACT_ADDRESS = process.env.CONTRACT_ADDRESS;
const PRIVATE_KEY = process.env.PRIVATE_KEY;
const INFURA_PROJECT_ID = process.env.INFURA_PROJECT_ID;

// ABI containing only the method needed for anchoring biometric data
const abi = [
  "function anchorUserData(string did, string faceIPFSHash, string faceTemplateHash, string fingerprintIPFSHash, string fingerprintHash) public"
];

// Set up provider and wallet signer for Sepolia network
const provider = new ethers.JsonRpcProvider(`https://sepolia.infura.io/v3/${INFURA_PROJECT_ID}`);
const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
const contract = new ethers.Contract(CONTRACT_ADDRESS, abi, wallet);

// Calls the smart contract to anchor the user's biometric data
export async function anchorBiometricHash({
  did,
  faceIPFSHash,
  faceTemplateHash,
  fingerprintIPFSHash,
  fingerprintHash
}) {
  try {
    console.log("Anchoring user data...");
    console.log("DID:", did);
    console.log("Face IPFS Hash:", faceIPFSHash);
    console.log("Face Template Hash:", faceTemplateHash);
    console.log("Fingerprint IPFS Hash:", fingerprintIPFSHash || "");
    console.log("Fingerprint Hash:", fingerprintHash || "");

    const tx = await contract.anchorUserData(
      did,
      faceIPFSHash,
      faceTemplateHash,
      fingerprintIPFSHash || "",
      fingerprintHash || ""
    );

    await tx.wait();
    return tx.hash;
  } catch (error) {
    console.error("Smart contract error:", error);
    throw error;
  }
}
