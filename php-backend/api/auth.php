<?php
require_once __DIR__ . '/config.php';

function generateToken($userId, $username, $role) {
    global $config;
    $header = base64_encode(json_encode(['alg' => 'HS256', 'typ' => 'JWT']));
    $payload = base64_encode(json_encode([
        'sub' => $userId,
        'username' => $username,
        'role' => $role,
        'iat' => time(),
        'exp' => time() + $config['jwt_expire'],
    ]));
    $signature = base64_encode(hash_hmac('sha256', "$header.$payload", $config['jwt_secret'], true));
    return "$header.$payload.$signature";
}

function verifyToken($token) {
    global $config;
    $parts = explode('.', $token);
    if (count($parts) !== 3) return null;
    [$header, $payload, $signature] = $parts;
    $expected = base64_encode(hash_hmac('sha256', "$header.$payload", $config['jwt_secret'], true));
    if (!hash_equals($expected, $signature)) return null;
    $data = json_decode(base64_decode($payload), true);
    if (!$data || !isset($data['exp']) || $data['exp'] < time()) return null;
    return $data;
}

function getCurrentUser() {
    $auth = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
    if (!$auth) {
        $headers = function_exists('apache_request_headers') ? apache_request_headers() : [];
        $auth = $headers['Authorization'] ?? $headers['authorization'] ?? '';
    }
    if (!$auth && isset($_COOKIE['access_token'])) {
        $auth = 'Bearer ' . $_COOKIE['access_token'];
    }
    if (!preg_match('/^Bearer\s+(.+)$/i', $auth, $m)) {
        errorResponse('Unauthorized', 401);
    }
    $user = verifyToken($m[1]);
    if (!$user) errorResponse('Invalid token', 401);
    return $user;
}

function requireAuth() {
    return getCurrentUser();
}

function requireRole($roles) {
    $user = getCurrentUser();
    if (!in_array($user['role'], (array)$roles)) {
        errorResponse('Forbidden: insufficient permissions', 403);
    }
    return $user;
}

function newId() {
    return sprintf('%s-%s-%s-%s-%s',
        bin2hex(random_bytes(4)),
        bin2hex(random_bytes(2)),
        bin2hex(random_bytes(2)),
        bin2hex(random_bytes(2)),
        bin2hex(random_bytes(6))
    );
}
