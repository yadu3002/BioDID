// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

contract BiometricAnchor {
    struct BiometricData {
        string faceIPFSHash;
        string faceTemplateHash;
        string fingerprintIPFSHash;
        string fingerprintHash;
        uint256 timestamp;
    }

    mapping(string => BiometricData) private anchoredData;

    event Anchored(
        string did,
        string faceIPFSHash,
        string faceTemplateHash,
        string fingerprintIPFSHash,
        string fingerprintHash,
        uint256 timestamp
    );

    function anchorUserData(
        string memory did,
        string memory faceIPFSHash,
        string memory faceTemplateHash,
        string memory fingerprintIPFSHash,
        string memory fingerprintHash
    ) public {
        require(bytes(did).length > 0, "DID required");
        require(bytes(faceIPFSHash).length > 0, "Face IPFS hash required");
        require(bytes(faceTemplateHash).length > 0, "Face hash required");

        BiometricData memory data = BiometricData({
            faceIPFSHash: faceIPFSHash,
            faceTemplateHash: faceTemplateHash,
            fingerprintIPFSHash: fingerprintIPFSHash,
            fingerprintHash: fingerprintHash,
            timestamp: block.timestamp
        });

        anchoredData[did] = data;

        emit Anchored(
            did,
            faceIPFSHash,
            faceTemplateHash,
            fingerprintIPFSHash,
            fingerprintHash,
            block.timestamp
        );
    }

    function getUserData(string memory did) public view returns (
        string memory faceIPFSHash,
        string memory faceTemplateHash,
        string memory fingerprintIPFSHash,
        string memory fingerprintHash,
        uint256 timestamp
    ) {
        BiometricData memory data = anchoredData[did];
        return (
            data.faceIPFSHash,
            data.faceTemplateHash,
            data.fingerprintIPFSHash,
            data.fingerprintHash,
            data.timestamp
        );
    }
}
