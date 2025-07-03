import 'package:bio_auth/config.dart';
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';

import 'pages/HomePage.dart';
import 'pages/WebLoginPage.dart';

void main() {
  runApp(const BioAuthApp());
}

class BioAuthApp extends StatelessWidget {
  const BioAuthApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'BioAuth',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => const HomePage(),           // Default route
        '/weblogin': (context) => const WebLoginPage(), // Web QR login page
      },
      debugShowCheckedModeBanner: false,
    );
  }
}
