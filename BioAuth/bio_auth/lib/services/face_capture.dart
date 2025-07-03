import 'dart:io';
import 'package:camera/camera.dart';

CameraController? _controller;

/// Initializes the front-facing camera and returns the controller
Future<CameraController> initializeFrontCamera() async {
  final cameras = await availableCameras();
  final frontCamera = cameras.firstWhere(
    (camera) => camera.lensDirection == CameraLensDirection.front,
  );

  _controller = CameraController(frontCamera, ResolutionPreset.medium);
  await _controller!.initialize();
  return _controller!;
}

/// Captures an image and returns the file
Future<File> captureImage() async {
  if (_controller == null || !_controller!.value.isInitialized) {
    throw Exception("Camera not initialized");
  }

  final picture = await _controller!.takePicture();
  return File(picture.path);
}

/// Releases camera resources
Future<void> disposeCamera() async {
  await _controller?.dispose();
  _controller = null;
}
