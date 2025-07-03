import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';
import '../config.dart';

class ApiService {
  // Sends face image to Flask for embedding and IPFS upload
  static Future<Map<String, dynamic>> registerFace({
    required String did,
    required File image,
  }) async {
    final uri = Uri.parse('${Config.flaskUrl}/register_face');

    var request = http.MultipartRequest('POST', uri)
      ..fields['did'] = did
      ..files.add(await http.MultipartFile.fromPath('image', image.path));

    final response = await request.send();
    final body = await response.stream.bytesToString();
    return jsonDecode(body);
  }

  // Requests a new DID from the Node.js backend
  static Future<Map<String, dynamic>> createDid() async {
    final response = await http.post(
      Uri.parse('${Config.veramoUrl}/create-did'),
      headers: {"Content-Type": "application/json"},
    );
    return jsonDecode(response.body);
  }

  // Sends fingerprint image to Flask for processing and IPFS upload
  static Future<Map<String, dynamic>> uploadFingerprint({
    required String did,
    required File fingerprint,
  }) async {
    final uri = Uri.parse('${Config.flaskUrl}/upload_fingerprint');

    var request = http.MultipartRequest('POST', uri)
      ..fields['did'] = did
      ..files.add(await http.MultipartFile.fromPath('fingerprint', fingerprint.path));

    final response = await request.send();
    final body = await response.stream.bytesToString();
    return jsonDecode(body);
  }

  // Saves complete user data to Flask backend
  static Future<Map<String, dynamic>> createUser(Map<String, dynamic> userData) async {
    final uri = Uri.parse("${Config.flaskUrl}/create_user");

    try {
      final response = await http.post(
        uri,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode(userData),
      );
      return jsonDecode(response.body);
    } catch (e) {
      return {"error": e.toString()};
    }
  }

  // Sends image for face verification
  static Future<Map<String, dynamic>> verifyFace(File image) async {
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('${Config.flaskUrl}/verify_face'),
    );
    request.files.add(await http.MultipartFile.fromPath('image', image.path));

    final response = await request.send();
    final body = await response.stream.bytesToString();
    return jsonDecode(body);
  }

  // Sends fingerprint image for verification
  static Future<Map<String, dynamic>> verifyFingerprint(File fingerprint) async {
  var request = http.MultipartRequest(
    'POST',
    Uri.parse('${Config.flaskUrl}/verify_fingerprint'),
  );
  request.files.add(await http.MultipartFile.fromPath('fingerprint', fingerprint.path));

  final response = await request.send();
  final body = await response.stream.bytesToString();

  try {
    final decoded = jsonDecode(body);

    if (decoded is Map<String, dynamic>) {
      return decoded;
    } else {
      debugPrint("⚠️ Unexpected response format: $decoded");
      return {"error": "Unexpected response format"};
    }
  } catch (e) {
    debugPrint("❌ Failed to decode response: $e");
    return {"error": "Invalid response format"};
  }
}


  // Deletes a user profile using DID
  static Future<Map<String, dynamic>> deleteUser(String did) async {
    final response = await http.post(
      Uri.parse('${Config.flaskUrl}/delete_user'),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"did": did}),
    );
    return jsonDecode(response.body);
  }

  // Sends data to Node backend for smart contract anchoring
  static Future<Map<String, dynamic>> anchorUserOnChain(Map<String, dynamic> data) async {
    final response = await http.post(
      Uri.parse('${Config.veramoUrl}/anchor_user_data'),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode(data),
    );
    return jsonDecode(response.body);
  }
}
