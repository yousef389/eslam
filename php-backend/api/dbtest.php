<?php
header('Content-Type: text/plain; charset=utf-8');
echo "=== Sanitary ERP - Database Diagnostic ===\n\n";

// Try common InfinityFree MySQL hosts
$hosts = ['sql212.infinityfree.com', 'sql210.infinityfree.com', 'sql200.infinityfree.com', 'sql201.infinityfree.com', 'sql301.infinityfree.com', 'sql305.infinityfree.com', 'sql213.infinityfree.com', 'sql214.infinityfree.com', 'sql215.infinityfree.com', 'sql300.infinityfree.com'];
$username = 'if0_42446288';
$password = 't5jaS4YwJE4a4EQ';
$dbname = 'if0_42446288_rslam';

foreach ($hosts as $host) {
    echo "Trying $host ... ";
    try {
        $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8mb4", $username, $password, [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_TIMEOUT => 5,
        ]);
        echo "SUCCESS!\n";
        $tables = $pdo->query("SHOW TABLES")->fetchAll(PDO::FETCH_COLUMN);
        echo "  Tables: " . implode(', ', $tables) . "\n";
        break;
    } catch (PDOException $e) {
        $code = $e->getCode();
        echo "FAILED (code: $code) " . substr($e->getMessage(), 0, 120) . "\n";
    }
}

echo "\n=== PHP Info ===\n";
echo "PHP Version: " . phpversion() . "\n";
echo "PDO drivers: " . implode(', ', PDO::getAvailableDrivers()) . "\n";
echo "Document Root: " . ($_SERVER['DOCUMENT_ROOT'] ?? 'N/A') . "\n";
echo "SCRIPT_FILENAME: " . ($_SERVER['SCRIPT_FILENAME'] ?? 'N/A') . "\n";
