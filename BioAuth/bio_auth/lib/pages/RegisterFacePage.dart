import 'dart:io';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:google_mlkit_face_detection/google_mlkit_face_detection.dart';
import 'package:bio_auth/services/api_service.dart';
import 'package:bio_auth/services/face_capture.dart';
import '../config.dart';
import 'RegisterFingerprintPage.dart';

class RegisterFacePage extends StatefulWidget {
  final String name;
  final String did;

  const RegisterFacePage({Key? key, required this.name, required this.did}) : super(key: key);

  @override
  State<RegisterFacePage> createState() => _RegisterFacePageState();
}

class _RegisterFacePageState extends State<RegisterFacePage> {
  late CameraController _cameraController;
  late FaceDetector _faceDetector;

  bool _isInitialized = false;
  bool _livenessConfirmed = false;
  bool _processing = false;

  String _status = "Align face and blink/smile/turn head";

  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }

  // Setup front camera and face detector
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

  // Continuously checks for liveness gestures
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
                _status = "Liveness confirmed. Registering...";
                _livenessConfirmed = true;
              });

              await _registerFace(imageFile);
              return;
            } else {
              setState(() => _status = "Please blink, smile or turn head");
            }
          } else {
            setState(() => _status = "No face detected. Align properly.");
          }
        } catch (e) {
          debugPrint("Liveness error: $e");
        } finally {
          _processing = false;
        }
      }

      await Future.delayed(const Duration(seconds: 1));
    }
  }

  // Sends captured face image for embedding and registration
  Future<void> _registerFace(File imageFile) async {
    try {
      final data = await ApiService.registerFace(
        did: widget.did,
        image: imageFile,
      );

      if (data['embeddingIpfsHash'] != null) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => RegisterFingerprintPage(
              name: widget.name,
              did: widget.did,
              embeddingIpfsHash: data['embeddingIpfsHash'],
              embeddingHash: data['embeddingHash'],
            ),
          ),
        );
      } else {
        setState(() {
          _status = "Face registration failed: ${data['error'] ?? 'Unknown error'}";
          _livenessConfirmed = false;
        });
      }
    } catch (e) {
      setState(() {
        _status = "Exception: $e";
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
      appBar: AppBar(title: const Text("Step 2: Register Face")),
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
