<?php
header('Content-Type: application/json; charset=utf-8');
echo json_encode([
    'HTTP_AUTHORIZATION' => $_SERVER['HTTP_AUTHORIZATION'] ?? 'NOT SET',
    'ALL_HEADERS' => function_exists('getallheaders') ? getallheaders() : 'N/A',
    'apache_request_headers' => function_exists('apache_request_headers') ? apache_request_headers() : 'N/A',
    'SERVER' => array_filter($_SERVER, fn($k) => strpos($k, 'HTTP') === 0 || $k === 'REQUEST_URI'),
], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
