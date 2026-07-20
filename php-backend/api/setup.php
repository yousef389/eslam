<?php
header('Content-Type: text/html; charset=utf-8');
?>
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head><title>إعداد قاعدة البيانات</title></head>
<body>
<h2>Sanitary ERP - Database Setup</h2>
<pre>
<?php
$host = 'sql212.infinityfree.com';
$user = 'if0_42446288';
$pass = 't5jaS4YwJE4a4EQ';
$dbname = 'if0_42446288_rslam';

echo "Connecting to $host as $user ...\n\n";

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8mb4", $user, $pass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    ]);
    echo "✅ Connected!\n\n";
    
    $sql = file_get_contents(__DIR__ . '/schema.sql');
    if (!$sql) {
        echo "❌ Could not read schema.sql\n";
        exit;
    }
    
    // Remove comment-only lines and empty lines
    $lines = explode("\n", $sql);
    $cleanSql = '';
    foreach ($lines as $line) {
        $trimmed = trim($line);
        if ($trimmed === '' || strpos($trimmed, '--') === 0) continue;
        $cleanSql .= $line . "\n";
    }
    
    $statements = array_filter(array_map('trim', explode(';', $cleanSql)));
    
    $ok = 0;
    $fail = 0;
    foreach ($statements as $stmt) {
        $stmt = trim($stmt);
        if (empty($stmt)) continue;
        try {
            $pdo->exec($stmt);
            $ok++;
        } catch (PDOException $e) {
            $fail++;
            $msg = $e->getMessage();
            if (strpos($msg, 'Duplicate') === false && strpos($msg, 'already exists') === false) {
                echo "⚠️ " . substr($msg, 0, 150) . "\n";
                echo "   → " . substr($stmt, 0, 80) . "\n\n";
            }
        }
    }
    
    echo "✅ Created: $ok statements\n";
    echo "⚠️ Skipped/errors: $fail\n\n";
    
    $tables = $pdo->query("SHOW TABLES")->fetchAll(PDO::FETCH_COLUMN);
    echo "📋 Tables (" . count($tables) . "):\n";
    foreach ($tables as $t) {
        $cnt = $pdo->query("SELECT COUNT(*) FROM `$t`")->fetchColumn();
        echo "  - $t ($cnt rows)\n";
    }
    
} catch (Exception $e) {
    echo "❌ Error: " . $e->getMessage() . "\n";
}
?>
</pre>
</body>
</html>
