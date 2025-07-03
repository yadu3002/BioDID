import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../config.dart';
import 'ResultPage.dart';

class WebLoginPage extends StatefulWidget {
  const WebLoginPage({super.key});

  @override
  State<WebLoginPage> createState() => _WebLoginPageState();
}

class _WebLoginPageState extends State<WebLoginPage> {
  String? sessionId;
  String? qrCodeData;
  String status = "Scan this QR with your BioAuth mobile app";

  @override
  void initState() {
    super.initState();
    _generateQR();
  }

  Future<void> _generateQR() async {
    final res = await http.get(Uri.parse('${Config.flaskUrl}/generate-login-qr'));
    final data = jsonDecode(res.body);
    setState(() {
      sessionId = data['sessionId'];
      qrCodeData = data['qrCode'];
    });

    _pollLoginStatus();
  }

  Future<void> _pollLoginStatus() async {
    while (mounted) {
      await Future.delayed(const Duration(seconds: 2));
      final res = await http.get(Uri.parse('${Config.flaskUrl}/check-session/$sessionId'));
      final result = jsonDecode(res.body);
      if (result['status'] == 'authenticated') {
        setState(() => status = "✅ Login confirmed!");
        await Future.delayed(const Duration(seconds: 1));
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => ResultPage(
              did: result['did'],
              name: "Web User",
              faceHash: "Hidden on web",
              fingerprintHash: null,
            ),
          ),
        );
        break;
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Web QR Login")),
      body: Center(
        child: qrCodeData == null
            ? const CircularProgressIndicator()
            : Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Image.memory(base64Decode(qrCodeData!.split(',').last), height: 250),
                  const SizedBox(height: 20),
                  Text(status, style: const TextStyle(fontSize: 18)),
                ],
              ),
      ),
    );
  }
}
