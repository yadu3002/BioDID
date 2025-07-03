import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:bio_auth/services/api_service.dart';
import '../config.dart';
import 'SubmitUserPage.dart';

class RegisterFingerprintPage extends StatefulWidget {
  final String name;
  final String did;
  final String embeddingIpfsHash;
  final String embeddingHash;

  const RegisterFingerprintPage({
    Key? key,
    required this.name,
    required this.did,
    required this.embeddingIpfsHash,
    required this.embeddingHash,
  }) : super(key: key);

  @override
  State<RegisterFingerprintPage> createState() => _RegisterFingerprintPageState();
}

class _RegisterFingerprintPageState extends State<RegisterFingerprintPage> {
  File? _fingerprintFile;
  bool _isLoading = false;
  String _status = "";

  // Allows user to pick a fingerprint image from the gallery
  Future<void> _pickFingerprint() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.gallery);
    if (pickedFile == null) return;

    setState(() {
      _fingerprintFile = File(pickedFile.path);
    });
  }

  // Uploads fingerprint and proceeds to final registration step
  Future<void> _uploadFingerprint() async {
    if (_fingerprintFile == null) {
      setState(() => _status = "Please select a fingerprint image.");
      return;
    }

    setState(() {
      _isLoading = true;
      _status = "Uploading fingerprint...";
    });

    try {
      final data = await ApiService.uploadFingerprint(
        did: widget.did,
        fingerprint: _fingerprintFile!,
      );

      if (data['fingerprintIpfsHash'] != null) {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => SubmitUserPage(
              name: widget.name,
              did: widget.did,
              embeddingIpfsHash: widget.embeddingIpfsHash,
              embeddingHash: widget.embeddingHash,
              fingerprintIpfsHash: data['fingerprintIpfsHash'],
              fingerprintHash: data['fingerprintHash'],
            ),
          ),
        );
      } else {
        setState(() => _status = "Upload failed: ${data['error'] ?? 'Unknown error'}");
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
      appBar: AppBar(title: const Text("Step 3: Fingerprint Upload")),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            _fingerprintFile != null
                ? Image.file(_fingerprintFile!, height: 200)
                : const Text("No fingerprint selected"),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _pickFingerprint,
              child: const Text("Pick Fingerprint from Gallery"),
            ),
            const SizedBox(height: 30),
            ElevatedButton(
              onPressed: _isLoading ? null : _uploadFingerprint,
              child: _isLoading
                  ? const CircularProgressIndicator()
                  : const Text("Upload & Continue"),
            ),
            const SizedBox(height: 16),
            Text(_status),
          ],
        ),
      ),
    );
  }
}
