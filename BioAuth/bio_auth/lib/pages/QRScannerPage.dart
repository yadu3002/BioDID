import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:permission_handler/permission_handler.dart';
import '../../config.dart';

class QRScannerPage extends StatefulWidget {
  final String did;

  const QRScannerPage({super.key, required this.did});

  @override
  State<QRScannerPage> createState() => _QRScannerPageState();
}

class _QRScannerPageState extends State<QRScannerPage> {
  bool _scanned = false;
  bool _permissionGranted = false;
  final MobileScannerController _controller = MobileScannerController();

  @override
  void initState() {
    super.initState();
    _requestCameraPermission();
  }

  // Ask for camera permission before starting the scanner
  Future<void> _requestCameraPermission() async {
    var status = await Permission.camera.status;
    if (!status.isGranted) {
      status = await Permission.camera.request();
    }

    if (status.isGranted) {
      setState(() => _permissionGranted = true);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Camera permission denied")),
      );
      Navigator.pop(context);
    }
  }

  // Confirm login session with the scanned session ID and user DID
  Future<void> _completeLogin(String sessionId) async {
    final res = await http.post(
      Uri.parse('${Config.flaskUrl}/api/confirm-session'),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: jsonEncode({
        'sessionId': sessionId,
        'did': widget.did,
      }),
    );

    final result = jsonDecode(res.body);

    if (res.statusCode == 200) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Web login confirmed")),
      );
      Navigator.pop(context);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result['error'] ?? 'Login failed')),
      );
    }
  }

  // Called when QR is detected
  void _onDetect(BarcodeCapture capture) {
    if (_scanned) return;
    final code = capture.barcodes.first.rawValue;

    if (code != null) {
      setState(() => _scanned = true);
      _controller.stop();
      _completeLogin(code);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Scan QR Code")),
      body: _permissionGranted
          ? Stack(
              children: [
                MobileScanner(
                  controller: _controller,
                  onDetect: _onDetect,
                ),
                if (_scanned)
                  const Center(child: CircularProgressIndicator()),
              ],
            )
          : const Center(child: CircularProgressIndicator()),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}
