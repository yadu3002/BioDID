import 'package:flutter/material.dart';
import 'package:bio_auth/services/api_service.dart';
import 'package:bio_auth/pages/QRScannerPage.dart';

class ResultPage extends StatelessWidget {
  final String did;
  final String name;
  final String faceHash;
  final String? fingerprintHash;

  const ResultPage({
    Key? key,
    required this.did,
    required this.name,
    required this.faceHash,
    this.fingerprintHash,
  }) : super(key: key);

  // Deletes user data from the system
  Future<void> _deleteUser(BuildContext context) async {
    final result = await ApiService.deleteUser(did);

    if (result.containsKey('message')) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result['message'])),
      );
      Navigator.of(context).popUntil((route) => route.isFirst);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Error: ${result['error'] ?? 'Unknown'}")),
      );
    }
  }

  // Return to first screen
  void _signOut(BuildContext context) {
    Navigator.of(context).popUntil((route) => route.isFirst);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Registration Complete')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text("Name: $name", style: const TextStyle(fontSize: 18)),
            const SizedBox(height: 10),
            Text("DID: $did", style: const TextStyle(fontSize: 16)),
            const SizedBox(height: 10),
            const Text("Face Hash:", style: TextStyle(fontWeight: FontWeight.bold)),
            Text(faceHash),
            const SizedBox(height: 10),
            if (fingerprintHash != null) ...[
              const Text("Fingerprint Hash:", style: TextStyle(fontWeight: FontWeight.bold)),
              Text(fingerprintHash!),
            ],
            const Spacer(),
            ElevatedButton.icon(
              onPressed: () => _deleteUser(context),
              icon: const Icon(Icons.delete),
              label: const Text("Delete My Data"),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            ),
            const SizedBox(height: 10),
            ElevatedButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => QRScannerPage(did: did),
                  ),
                );
              },
              child: const Text("Login via QR"),
            ),
            const SizedBox(height: 10),
            OutlinedButton.icon(
              onPressed: () => _signOut(context),
              icon: const Icon(Icons.logout),
              label: const Text("Sign Out"),
            ),
          ],
        ),
      ),
    );
  }
}
