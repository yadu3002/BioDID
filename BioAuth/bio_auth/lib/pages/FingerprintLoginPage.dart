import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';
import '../config.dart';
import 'ResultPage.dart';

class FingerprintLoginPage extends StatefulWidget {
  const FingerprintLoginPage({super.key});

  @override
  State<FingerprintLoginPage> createState() => _FingerprintLoginPageState();
}

class _FingerprintLoginPageState extends State<FingerprintLoginPage> {
  File? _fingerprintFile;
  String _status = "";
  bool _isLoading = false;

  // Allow user to pick a fingerprint image from the gallery
  Future<void> _pickFingerprint() async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(source: ImageSource.gallery);

    if (picked != null) {
      setState(() {
        _fingerprintFile = File(picked.path);
        _status = "";
      });
    }
  }

  // Send fingerprint image to backend for verification
  Future<void> _verifyFingerprint() async {
    if (_fingerprintFile == null) {
      setState(() => _status = "Please select a fingerprint first.");
      return;
    }

    setState(() {
      _isLoading = true;
      _status = "Verifying fingerprint...";
    });

    try {
      final data = await ApiService.verifyFingerprint(_fingerprintFile!);
      print("📦 Received response: ${data.toString()}");

      if (data['user'] != null) {
        final user = data['user'];

        Navigator.push(
          context,
          MaterialPageRoute(
            
            builder: (_) => ResultPage(
              did: user['did'],
              name: user['name'],
              faceHash: user['faceTemplateHash'],
              fingerprintHash: user['fingerprintHash'] ?? "N/A",
            ),
          ),
        );
      } else {
        setState(() => _status = "Not recognized: ${data['error'] ?? 'Unknown error'}");
      }
    } catch (e) {
      setState(() => _status = "Exception: $e");
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Login via Fingerprint")),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            _fingerprintFile != null
                ? Image.file(_fingerprintFile!, height: 200)
                : const Text("No fingerprint selected"),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _pickFingerprint,
              child: const Text("Pick Fingerprint Image"),
            ),
            const SizedBox(height: 30),
            ElevatedButton(
              onPressed: _isLoading ? null : _verifyFingerprint,
              child: _isLoading
                  ? const CircularProgressIndicator()
                  : const Text("Verify & Login"),
            ),
            const SizedBox(height: 20),
            Text(_status),
          ],
        ),
      ),
    );
  }
}
