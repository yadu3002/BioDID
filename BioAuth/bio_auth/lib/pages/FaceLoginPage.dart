import 'dart:io';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:google_mlkit_face_detection/google_mlkit_face_detection.dart';
import '../config.dart';
import '../services/api_service.dart';
import '../services/face_capture.dart';
import 'ResultPage.dart';

class FaceLoginPage extends StatefulWidget {
  const FaceLoginPage({super.key});

  @override
  State<FaceLoginPage> createState() => _FaceLoginPageState();
}

class _FaceLoginPageState extends State<FaceLoginPage> {
  late CameraController _cameraController;
  late FaceDetector _faceDetector;

  bool _isInitialized = false;
  bool _processing = false;
  bool _livenessConfirmed = false;
  String _status = "Align face and blink/smile/turn head";

  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }

  Future<void> _initializeCamera() async {
    _cameraController = await initializeFrontCamera();

    _faceDetector = FaceDetector(
      options: FaceDetectorOptions(
        enableClassification: true,
        enableTracking: true,
        performanceMode: FaceDetectorMode.accurate,
      ),
    );

    setState(() => _isInitialized = true);
    _startLivenessLoop();
  }

  // Loop to detect liveness gestures like blink, smile, or head turn
  void _startLivenessLoop() async {
    while (mounted && !_livenessConfirmed) {
      if (!_processing && _cameraController.value.isInitialized) {
        _processing = true;

        try {
          final imageFile = await captureImage();
          final inputImage = InputImage.fromFile(imageFile);
          final faces = await _faceDetector.processImage(inputImage);

          if (faces.isNotEmpty) {
            final face = faces.first;

            final blink = ((face.leftEyeOpenProbability ?? 1.0) +
                    (face.rightEyeOpenProbability ?? 1.0)) /
                2 <
                0.4;
            final smile = (face.smilingProbability ?? 0.0) > 0.7;
            final headTurned = (face.headEulerAngleY?.abs() ?? 0.0) > 15;

            if (blink || smile || headTurned) {
              setState(() {
                _status = "Liveness Confirmed. Verifying...";
                _livenessConfirmed = true;
              });

              await _verifyFace(imageFile);
              return;
            } else {
              setState(() => _status = "Please blink, smile or turn head");
            }
          } else {
            setState(() => _status = "No face detected. Align properly.");
          }
        } catch (e) {
          debugPrint("Error: $e");
        } finally {
          _processing = false;
        }
      }

      await Future.delayed(const Duration(seconds: 1));
    }
  }

  // Send image to backend for verification
  Future<void> _verifyFace(File imageFile) async {
    final data = await ApiService.verifyFace(imageFile);

    if (data['user'] != null) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => ResultPage(
            did: data['user']['did'],
            name: data['user']['name'],
            faceHash: data['user']['faceTemplateHash'],
            fingerprintHash: data['user']['fingerprintHash'] ?? "N/A",
          ),
        ),
      );
    } else {
      setState(() {
        _status = "Face not recognized.";
        _livenessConfirmed = false;
      });
    }
  }

  @override
  void dispose() {
    _cameraController.dispose();
    _faceDetector.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Login via Face")),
      body: _isInitialized
          ? Stack(
              children: [
                CameraPreview(_cameraController),
                Center(
                  child: Container(
                    width: 260,
                    height: 360,
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.white, width: 2),
                      borderRadius: BorderRadius.circular(180),
                    ),
                  ),
                ),
                Positioned(
                  bottom: 40,
                  left: 0,
                  right: 0,
                  child: Center(
                    child: Text(
                      _status,
                      style: const TextStyle(
                        backgroundColor: Colors.black54,
                        color: Colors.white,
                        fontSize: 16,
                      ),
                    ),
                  ),
                )
              ],
            )
          : const Center(child: CircularProgressIndicator()),
    );
  }
}
