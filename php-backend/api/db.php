<?php
require_once __DIR__ . '/config.php';

function getDB() {
    static $pdo = null;
    if ($pdo === null) {
        $dsn = "mysql:host={$config['db_host']};dbname={$config['db_name']};charset=utf8mb4";
        $pdo = new PDO($dsn, $config['db_user'], $config['db_pass'], [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
        ]);
    }
    return $pdo;
}

function jsonResponse($data, $code = 200) {
    http_response_code($code);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($data, JSON_UNESCAPED_UNICODE);
    exit;
}

function errorResponse($message, $code = 400) {
    jsonResponse(['success' => false, 'detail' => $message], $code);
}

function successResponse($data, $message = null, $meta = null) {
    $response = ['success' => true, 'data' => $data];
    if ($message) $response['message'] = $message;
    if ($meta) $response['meta'] = $meta;
    jsonResponse($response);
}

function getInput() {
    $json = file_get_contents('php://input');
    return json_decode($json, true) ?: [];
}
