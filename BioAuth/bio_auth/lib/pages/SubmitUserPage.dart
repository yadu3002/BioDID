import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../config.dart';
import '../services/api_service.dart';

class SubmitUserPage extends StatefulWidget {
  final String did;
  final String name;
  final String embeddingIpfsHash;
  final String embeddingHash;
  final String? fingerprintIpfsHash;
  final String? fingerprintHash;

  const SubmitUserPage({
    Key? key,
    required this.did,
    required this.name,
    required this.embeddingIpfsHash,
    required this.embeddingHash,
    this.fingerprintIpfsHash,
    this.fingerprintHash,
  }) : super(key: key);

  @override
  State<SubmitUserPage> createState() => _SubmitUserPageState();
}

class _SubmitUserPageState extends State<SubmitUserPage> {
  String _status = "";
  bool _isSubmitting = false;

  // Handles final submission: anchors to blockchain, then saves to backend
  Future<void> _submitUser() async {
    setState(() {
      _isSubmitting = true;
      _status = "Anchoring to blockchain...";
    });

    final userPayload = {
      "did": widget.did,
      "name": widget.name,
      "embeddingIpfsHash": widget.embeddingIpfsHash,
      "embeddingHash": widget.embeddingHash,
      "fingerprintIpfsHash": widget.fingerprintIpfsHash,
      "fingerprintHash": widget.fingerprintHash,
    };

    try {
      // Step 1: Anchor to blockchain via smart contract
      final anchorResponse = await ApiService.anchorUserOnChain(userPayload);

      if (anchorResponse['faceTx'] != null) {
        userPayload['anchoredTx'] = anchorResponse['faceTx'];
        userPayload['createdAt'] = DateTime.now().toIso8601String();
      }

      // Step 2: Save profile in backend database
      setState(() => _status = "Saving user to backend...");
      await ApiService.createUser(userPayload);

      setState(() => _status = "User successfully registered.");

      showDialog(
        context: context,
        builder: (_) => AlertDialog(
          title: const Text("Success"),
          content: Text("User created with DID: ${widget.did}"),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(context); // Close dialog
                Navigator.popUntil(context, (route) => route.isFirst); // Return to home
              },
              child: const Text("OK"),
            )
          ],
        ),
      );
    } catch (e) {
      setState(() => _status = "Exception: $e");
    } finally {
      setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Complete Registration")),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const Text("You're all set! Confirm to finish registration."),
            const SizedBox(height: 20),
            if (_isSubmitting)
              const CircularProgressIndicator(),
            if (!_isSubmitting)
              ElevatedButton(
                onPressed: _submitUser,
                child: const Text("Submit User"),
              ),
            const SizedBox(height: 20),
            Text(_status, textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }
}
