import 'dart:io';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:google_mlkit_face_detection/google_mlkit_face_detection.dart';
import 'package:bio_auth/services/face_capture.dart';

class LiveFaceCapturePage extends StatefulWidget {
  final Function(File capturedImage) onCapture;

  const LiveFaceCapturePage({Key? key, required this.onCapture}) : super(key: key);

  @override
  State<LiveFaceCapturePage> createState() => _LiveFaceCapturePageState();
}

class _LiveFaceCapturePageState extends State<LiveFaceCapturePage> {
  late CameraController _cameraController;
  late FaceDetector _faceDetector;

  bool _isCameraInitialized = false;
  bool _livenessConfirmed = false;
  bool _processing = false;

  String _statusText = "Align your face, then blink or smile";

  @override
  void initState() {
    super.initState();
    _initCameraAndDetector();
  }

  // Initialize front camera and face detector
  Future<void> _initCameraAndDetector() async {
    _cameraController = await initializeFrontCamera();

    setState(() => _isCameraInitialized = true);

    _faceDetector = FaceDetector(
      options: FaceDetectorOptions(
        enableClassification: true,
        enableTracking: true,
        performanceMode: FaceDetectorMode.accurate,
      ),
    );

    _startLivenessLoop();
  }

  // Runs in background and checks for liveness gestures
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
                _statusText = "Liveness Confirmed";
                _livenessConfirmed = true;
              });

              await Future.delayed(const Duration(milliseconds: 700));
              widget.onCapture(imageFile);
              return;
            } else {
              setState(() => _statusText = "Please blink, smile, or turn head");
            }
          } else {
            setState(() => _statusText = "No face detected. Please align.");
          }
        } catch (e) {
          debugPrint("Liveness detection error: $e");
        } finally {
          _processing = false;
        }
      }

      await Future.delayed(const Duration(seconds: 1));
    }
  }

  @override
  void dispose() {
    disposeCamera();
    _faceDetector.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Liveness Detection")),
      body: _isCameraInitialized
          ? Stack(
              children: [
                CameraPreview(_cameraController),
                Center(
                  child: Container(
                    width: 260,
                    height: 360,
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.white, width: 2),
                      borderRadius: BorderRadius.circular(200),
                    ),
                  ),
                ),
                Positioned(
                  bottom: 40,
                  left: 0,
                  right: 0,
                  child: Center(
                    child: Text(
                      _statusText,
                      style: const TextStyle(
                        backgroundColor: Colors.black54,
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.w500,
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
