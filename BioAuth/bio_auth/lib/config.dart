class Config {
  static const String backendBaseIP = 'http://192.168.8.46';

  // Base URLs for all services
  static const String nodeBackend = '$backendBaseIP:3000';
  static const String flaskBackend = '$backendBaseIP:5000';
  static const String verifyBackend = '$backendBaseIP:5001';

  // Defaults used by API service
  static const String flaskUrl = flaskBackend;
  static const String veramoUrl = nodeBackend;
}
