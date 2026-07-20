<?php
/**
 * Sanitary ERP - PHP Bridge for InfinityFree Hosting
 * 
 * This file serves the React frontend and proxies API requests
 * to the backend running on Render.com (or any other hosting).
 * 
 * SETUP:
 * 1. Deploy backend to Render.com (free tier)
 * 2. Set $API_BASE_URL below to your Render backend URL
 * 3. Upload all files to InfinityFree via FTP
 * 4. Upload the frontend/dist/* contents to the htdocs folder
 */

// ============================================
// CONFIGURATION - Change this to your backend URL
// ============================================
$API_BASE_URL = 'https://your-app.onrender.com'; // <-- CHANGE THIS

// ============================================
// API Proxy
// ============================================
$request_uri = $_SERVER['REQUEST_URI'];
$base_path = '/api/v1';

if (strpos($request_uri, $base_path) === 0) {
    header('Content-Type: application/json');
    header('Access-Control-Allow-Origin: *');
    header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
    header('Access-Control-Allow-Headers: Content-Type, Authorization');

    if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
        http_response_code(200);
        exit;
    }

    $api_path = substr($request_uri, strlen($base_path));
    $api_url = $API_BASE_URL . $base_path . $api_path;

    if (isset($_SERVER['QUERY_STRING']) && $_SERVER['QUERY_STRING']) {
        $api_url .= '?' . $_SERVER['QUERY_STRING'];
    }

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $api_url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $_SERVER['REQUEST_METHOD']);

    $headers = [];
    if (isset($_SERVER['HTTP_AUTHORIZATION'])) {
        $headers[] = 'Authorization: ' . $_SERVER['HTTP_AUTHORIZATION'];
    }
    if (isset($_SERVER['CONTENT_TYPE'])) {
        $headers[] = 'Content-Type: ' . $_SERVER['CONTENT_TYPE'];
    }
    if (!empty($headers)) {
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    }

    if ($_SERVER['REQUEST_METHOD'] !== 'GET' && $_SERVER['REQUEST_METHOD'] !== 'HEAD') {
        $body = file_get_contents('php://input');
        curl_setopt($ch, CURLOPT_POSTFIELDS, $body);
    }

    $response = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    http_response_code($http_code);
    echo $response;
    exit;
}

// ============================================
// Health check
// ============================================
if ($request_uri === '/health') {
    header('Content-Type: application/json');
    echo json_encode(['status' => 'healthy', 'hosting' => 'infinityfree']);
    exit;
}

// ============================================
// Serve static React app (SPA fallback)
// ============================================
$frontend_dir = __DIR__ . '/dist';

// Check if the requested file exists in dist
$file_path = $frontend_dir . $request_uri;
if ($request_uri !== '/' && file_exists($file_path) && is_file($file_path)) {
    // Determine content type
    $ext = pathinfo($file_path, PATHINFO_EXTENSION);
    $mime_types = [
        'html' => 'text/html',
        'css' => 'text/css',
        'js' => 'application/javascript',
        'json' => 'application/json',
        'png' => 'image/png',
        'jpg' => 'image/jpeg',
        'jpeg' => 'image/jpeg',
        'gif' => 'image/gif',
        'svg' => 'image/svg+xml',
        'ico' => 'image/x-icon',
        'woff' => 'font/woff',
        'woff2' => 'font/woff2',
        'ttf' => 'font/ttf',
    ];
    
    $mime = $mime_types[$ext] ?? 'application/octet-stream';
    header("Content-Type: $mime");
    header("Cache-Control: public, max-age=31536000");
    readfile($file_path);
    exit;
}

// For all other routes, serve index.html (React Router)
$index_file = $frontend_dir . '/index.html';
if (file_exists($index_file)) {
    header('Content-Type: text/html');
    readfile($index_file);
    exit;
}

// Fallback - show setup instructions
?>
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Sanitary ERP - Setup Required</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #1e40af; } .step { text-align: right; margin: 15px 0; padding: 15px; background: #f0f7ff; border-radius: 8px; }
        code { background: #e5e7eb; padding: 2px 8px; border-radius: 4px; direction: ltr; display: inline-block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 Sanitary ERP</h1>
        <p>يجب إعداد Backend أولاً</p>
        <div class="step"><strong>1.</strong> ارفع الباك اند على <code>Render.com</code> (مجاني)</div>
        <div class="step"><strong>2.</strong> عدّل قيمة <code>$API_BASE_URL</code> في ملف <code>index.php</code></div>
        <div class="step"><strong>3.</strong> ارفع ملفات البناء من <code>frontend/dist/*</code> هنا</div>
        <div class="step"><strong>4.</strong> افتح <code>eslam.gt.tc</code></div>
    </div>
</body>
</html>
