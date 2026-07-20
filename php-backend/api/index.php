<?php
/**
 * Sanitary ERP - PHP API Router for InfinityFree
 * All-in-one backend: Auth, Products, Customers, Suppliers, Sales, Purchases, etc.
 */
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(200); exit; }

require_once __DIR__ . '/config.php';
require_once __DIR__ . '/db.php';
require_once __DIR__ . '/auth.php';

$uri = $_SERVER['REQUEST_URI'];
$uri = parse_url($uri, PHP_URL_PATH);
$uri = rtrim($uri, '/');
$method = $_SERVER['REQUEST_METHOD'];
$input = getInput();

// Strip /api/v1 prefix
if (strpos($uri, '/api/v1') === 0) {
    $uri = substr($uri, 7);
}

// ─── ROUTING ──────────────────────────────────────────────────────────────────
function route($method, $pattern, $handler) {
    global $uri, $method_req;
    $regex = preg_replace('/\{(\w+)\}/', '(?P<$1>[^/]+)', $pattern);
    $regex = '#^' . $regex . '$#';
    if ($method_req === $method && preg_match($regex, $uri, $m)) {
        return ['handler' => $handler, 'params' => $m];
    }
    return null;
}

$method_req = $method;

$routes = [
    // Auth
    route('POST', '/auth/login', 'authLogin'),
    route('POST', '/auth/register', 'authRegister'),
    route('GET', '/auth/me', 'authMe'),
    route('POST', '/auth/logout', 'authLogout'),
    route('POST', '/auth/change-password', 'authChangePassword'),

    // Dashboard
    route('GET', '/dashboard/stats', 'dashboardStats'),

    // Products
    route('GET', '/products/low-stock', 'productsLowStock'),
    route('GET', '/products', 'productsList'),
    route('POST', '/products', 'productsCreate'),
    route('GET', '/products/{id}', 'productsGet'),
    route('PUT', '/products/{id}', 'productsUpdate'),
    route('DELETE', '/products/{id}', 'productsDelete'),

    // Categories
    route('GET', '/categories', 'categoriesList'),
    route('POST', '/categories', 'categoriesCreate'),
    route('GET', '/categories/{id}', 'categoriesGet'),
    route('PUT', '/categories/{id}', 'categoriesUpdate'),
    route('DELETE', '/categories/{id}', 'categoriesDelete'),

    // Customers
    route('GET', '/customers/{id}/statement', 'customerStatement'),
    route('GET', '/customers', 'customersList'),
    route('POST', '/customers', 'customersCreate'),
    route('GET', '/customers/{id}', 'customersGet'),
    route('PUT', '/customers/{id}', 'customersUpdate'),
    route('DELETE', '/customers/{id}', 'customersDelete'),

    // Suppliers
    route('GET', '/suppliers/{id}/statement', 'supplierStatement'),
    route('GET', '/suppliers', 'suppliersList'),
    route('POST', '/suppliers', 'suppliersCreate'),
    route('GET', '/suppliers/{id}', 'suppliersGet'),
    route('PUT', '/suppliers/{id}', 'suppliersUpdate'),
    route('DELETE', '/suppliers/{id}', 'suppliersDelete'),

    // Sale Orders
    route('GET', '/sale-orders', 'saleOrdersList'),
    route('POST', '/sale-orders', 'saleOrdersCreate'),
    route('GET', '/sale-orders/{id}', 'saleOrdersGet'),
    route('PUT', '/sale-orders/{id}', 'saleOrdersUpdate'),
    route('DELETE', '/sale-orders/{id}', 'saleOrdersDelete'),
    route('PUT', '/sale-orders/{id}/status', 'saleOrdersStatus'),

    // Sale Returns
    route('GET', '/sale-returns', 'saleReturnsList'),
    route('POST', '/sale-returns', 'saleReturnsCreate'),
    route('GET', '/sale-returns/{id}', 'saleReturnsGet'),

    // Purchase Orders
    route('GET', '/purchase-orders', 'purchaseOrdersList'),
    route('POST', '/purchase-orders', 'purchaseOrdersCreate'),
    route('GET', '/purchase-orders/{id}', 'purchaseOrdersGet'),
    route('PUT', '/purchase-orders/{id}', 'purchaseOrdersUpdate'),
    route('DELETE', '/purchase-orders/{id}', 'purchaseOrdersDelete'),
    route('PUT', '/purchase-orders/{id}/status', 'purchaseOrdersStatus'),

    // Purchase Returns
    route('GET', '/purchase-returns', 'purchaseReturnsList'),
    route('POST', '/purchase-returns', 'purchaseReturnsCreate'),
    route('GET', '/purchase-returns/{id}', 'purchaseReturnsGet'),

    // Accounting - Customers
    route('GET', '/accounting/customers', 'accountingCustomers'),
    route('GET', '/accounting/customers/{id}', 'accountingCustomerGet'),
    route('POST', '/accounting/customers', 'accountingCustomerCreate'),
    route('POST', '/accounting/customers/payments', 'accountingCustomerPayment'),

    // Accounting - Suppliers
    route('GET', '/accounting/suppliers', 'accountingSuppliers'),
    route('GET', '/accounting/suppliers/{id}', 'accountingSupplierGet'),
    route('POST', '/accounting/suppliers', 'accountingSupplierCreate'),
    route('POST', '/accounting/suppliers/payments', 'accountingSupplierPayment'),

    // Accounting - Cashbox
    route('GET', '/accounting/cashbox', 'cashboxList'),
    route('GET', '/accounting/cashbox/{id}', 'cashboxGet'),
    route('POST', '/accounting/cashbox/{id}/transactions', 'cashboxTransaction'),
    route('GET', '/accounting/cashbox/{id}/transactions', 'cashboxTransactions'),

    // Cashbox Transfers
    route('GET', '/cashbox-transfers', 'cashboxTransfersList'),
    route('POST', '/cashbox-transfers', 'cashboxTransfersCreate'),

    // Accounting Reports
    route('GET', '/accounting/reports/summary', 'accountingReportSummary'),
    route('GET', '/accounting/reports/transactions', 'accountingReportTransactions'),

    // Inventory
    route('GET', '/inventory/warehouses', 'warehousesList'),
    route('POST', '/inventory/warehouses', 'warehousesCreate'),
    route('PUT', '/inventory/warehouses/{id}', 'warehousesUpdate'),
    route('DELETE', '/inventory/warehouses/{id}', 'warehousesDelete'),
    route('GET', '/inventory/warehouses/{id}/stock', 'warehouseStock'),
    route('GET', '/inventory/stock-movements', 'stockMovementsList'),
    route('POST', '/inventory/stock-movements', 'stockMovementsCreate'),
    route('GET', '/inventory/stock-transfers', 'stockTransfersList'),
    route('POST', '/inventory/stock-transfers', 'stockTransfersCreate'),

    // Search
    route('GET', '/search', 'globalSearch'),

    // Settings
    route('GET', '/settings', 'settingsList'),
    route('PUT', '/settings/', 'settingsBulkUpdate'),
    route('GET', '/settings/{key}', 'settingsGet'),
    route('PUT', '/settings/{key}', 'settingsUpdate'),
    route('GET', '/settings/backup', 'settingsBackup'),
    route('GET', '/settings/export/products', 'exportProducts'),
    route('GET', '/settings/export/customers', 'exportCustomers'),
    route('GET', '/settings/export/suppliers', 'exportSuppliers'),

    // Reports
    route('GET', '/reports/sales/excel', 'reportSalesExcel'),
    route('GET', '/reports/sales/pdf', 'reportSalesPdf'),
    route('GET', '/reports/purchases/excel', 'reportPurchasesExcel'),
    route('GET', '/reports/inventory/excel', 'reportInventoryExcel'),
    route('GET', '/reports/customers/excel', 'reportCustomersExcel'),

    // Extractions (AI)
    route('GET', '/extractions', 'extractionsList'),
    route('POST', '/extractions', 'extractionsCreate'),
    route('GET', '/extractions/{id}', 'extractionsGet'),
    route('PUT', '/extractions/{id}/review', 'extractionsReview'),
];

// Health check
if ($uri === '/health' || $uri === '') {
    successResponse(['status' => 'healthy', 'hosting' => 'infinityfree']);
}

// Setup endpoint - creates all tables
if ($uri === '/setup' && $method_req === 'POST') {
    try {
        $db = getDB();
        $schema = file_get_contents(__DIR__ . '/schema.sql');
        $db->exec($schema);
        successResponse(['message' => 'Database tables created successfully']);
    } catch (Exception $e) {
        errorResponse('Setup failed: ' . $e->getMessage(), 500);
    }
}

// Match route
try {
    foreach ($routes as $r) {
        if ($r !== null) {
            $handler = $r['handler'];
            $params = $r['params'];
            $handler($params);
            exit;
        }
    }
} catch (Exception $e) {
    errorResponse('Server error: ' . $e->getMessage(), 500);
}

errorResponse('Not found: ' . $uri, 404);


// ═══════════════════════════════════════════════════════════════════════════════
// HANDLER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

// ─── AUTH ─────────────────────────────────────────────────────────────────────

function authLogin($p) {
    global $input;
    $db = getDB();
    $stmt = $db->prepare("SELECT * FROM users WHERE username = ? AND is_active = 1");
    $stmt->execute([$input['username'] ?? '']);
    $user = $stmt->fetch();
    if (!$user || !password_verify($input['password'] ?? '', $user['password_hash'])) {
        errorResponse('Invalid username or password', 401);
    }
    $db->prepare("UPDATE users SET last_login = NOW() WHERE id = ?")->execute([$user['id']]);
    $token = generateToken($user['id'], $user['username'], $user['role']);
    $refresh = generateToken($user['id'], $user['username'], $user['role']);
    setcookie('access_token', $token, time() + 86400, '/', '', false, false);
    setcookie('refresh_token', $refresh, time() + 86400 * 7, '/', '', false, false);
    successResponse([
        'access_token' => $token,
        'refresh_token' => $refresh,
        'token_type' => 'bearer',
    ]);
}

function authRegister($p) {
    global $input;
    $db = getDB();
    $stmt = $db->prepare("SELECT id FROM users WHERE username = ?");
    $stmt->execute([$input['username'] ?? '']);
    if ($stmt->fetch()) errorResponse('Username already exists');
    $id = newId();
    $hash = password_hash($input['password'] ?? '', PASSWORD_BCRYPT);
    $db->prepare("INSERT INTO users (id, username, email, full_name, password_hash, role) VALUES (?,?,?,?,?,?)")
        ->execute([$id, $input['username'], $input['email'] ?? '', $input['full_name'] ?? '', $hash, $input['role'] ?? 'staff']);
    successResponse(['id' => $id, 'username' => $input['username']], 'User registered', null);
}

function authMe($p) {
    $user = requireAuth();
    $db = getDB();
    $stmt = $db->prepare("SELECT id, username, email, full_name, role, is_active FROM users WHERE id = ?");
    $stmt->execute([$user['sub']]);
    $u = $stmt->fetch();
    if (!$u) errorResponse('User not found', 404);
    successResponse(['data' => $u]);
}

function authLogout($p) { successResponse(null, 'Logged out'); }

function authChangePassword($p) {
    global $input;
    $user = requireAuth();
    $db = getDB();
    $stmt = $db->prepare("SELECT password_hash FROM users WHERE id = ?");
    $stmt->execute([$user['sub']]);
    $u = $stmt->fetch();
    if (!password_verify($input['old_password'] ?? '', $u['password_hash'])) errorResponse('Wrong password');
    $hash = password_hash($input['new_password'] ?? '', PASSWORD_BCRYPT);
    $db->prepare("UPDATE users SET password_hash = ? WHERE id = ?")->execute([$hash, $user['sub']]);
    successResponse(null, 'Password changed');
}


// ─── DASHBOARD ────────────────────────────────────────────────────────────────

function dashboardStats($p) {
    $db = getDB();
    $today = date('Y-m-d');
    $month = date('Y-m');

    $dailySales = $db->query("SELECT COALESCE(SUM(total),0) FROM sale_orders WHERE status != 'cancelled' AND DATE(created_at) = '$today'")->fetchColumn();
    $monthlySales = $db->query("SELECT COALESCE(SUM(total),0) FROM sale_orders WHERE status != 'cancelled' AND DATE_FORMAT(created_at,'%Y-%m') = '$month'")->fetchColumn();
    $totalProducts = $db->query("SELECT COUNT(*) FROM products WHERE is_active = 1")->fetchColumn();
    $totalCustomers = $db->query("SELECT COUNT(*) FROM customers WHERE is_active = 1")->fetchColumn();
    $lowStockCount = $db->query("SELECT COUNT(*) FROM products WHERE quantity_in_stock <= minimum_stock_level AND is_active = 1")->fetchColumn();
    $pendingOrders = $db->query("SELECT COUNT(*) FROM sale_orders WHERE status = 'draft'")->fetchColumn();
    $totalPurchases = $db->query("SELECT COALESCE(SUM(total),0) FROM purchase_orders WHERE status != 'cancelled' AND DATE_FORMAT(created_at,'%Y-%m') = '$month'")->fetchColumn();
    $cashboxBalance = $db->query("SELECT COALESCE(SUM(balance),0) FROM cashboxes WHERE is_active = 1")->fetchColumn();
    $customerDebts = $db->query("SELECT COALESCE(SUM(remaining),0) FROM customer_debts WHERE status IN ('pending','partial','overdue')")->fetchColumn();
    $supplierDebts = $db->query("SELECT COALESCE(SUM(remaining),0) FROM supplier_debts WHERE status IN ('pending','partial','overdue')")->fetchColumn();
    $invoiceCount = $db->query("SELECT COUNT(*) FROM sale_orders WHERE status != 'cancelled' AND DATE_FORMAT(created_at,'%Y-%m') = '$month'")->fetchColumn();
    $netProfit = $monthlySales - $totalPurchases;

    $lowItems = [];
    $rows = $db->query("SELECT id, name, quantity_in_stock, unit FROM products WHERE quantity_in_stock <= minimum_stock_level AND is_active = 1 LIMIT 5")->fetchAll();
    foreach ($rows as $r) $lowItems[] = ['id' => $r['id'], 'name' => $r['name'], 'quantity' => (int)$r['quantity_in_stock'], 'unit' => $r['unit']];

    $activities = [];
    $rows = $db->query("SELECT order_number, customer_id, total, status, created_at FROM sale_orders ORDER BY created_at DESC LIMIT 10")->fetchAll();
    foreach ($rows as $r) $activities[] = $r;

    successResponse([
        'daily_sales' => (float)$dailySales,
        'monthly_sales' => (float)$monthlySales,
        'total_products' => (int)$totalProducts,
        'total_customers' => (int)$totalCustomers,
        'low_stock_items' => (int)$lowStockCount,
        'low_stock_items_data' => $lowItems,
        'pending_orders' => (int)$pendingOrders,
        'total_purchases' => (float)$totalPurchases,
        'net_profit' => (float)$netProfit,
        'cashbox_balance' => (float)$cashboxBalance,
        'customer_debts_total' => (float)$customerDebts,
        'supplier_debts_total' => (float)$supplierDebts,
        'invoice_count' => (int)$invoiceCount,
        'recent_activities' => $activities,
    ]);
}


// ─── PRODUCTS ─────────────────────────────────────────────────────────────────

function productsList($p) {
    $db = getDB();
    $page = max(1, (int)($_GET['page'] ?? 1));
    $per = min(100, max(1, (int)($_GET['per_page'] ?? 20)));
    $offset = ($page - 1) * $per;
    $search = $_GET['search'] ?? $_GET['q'] ?? '';

    $where = 'WHERE 1=1';
    $params = [];
    if ($search) { $where .= " AND (name LIKE ? OR sku LIKE ? OR barcode LIKE ?)"; $s = "%$search%"; $params = [$s,$s,$s]; }

    $total = $db->prepare("SELECT COUNT(*) FROM products $where");
    $total->execute($params);
    $count = $total->fetchColumn();

    $stmt = $db->prepare("SELECT * FROM products $where ORDER BY created_at DESC LIMIT $per OFFSET $offset");
    $stmt->execute($params);
    successResponse($stmt->fetchAll(), null, ['total' => (int)$count, 'page' => $page, 'per_page' => $per]);
}

function productsCreate($p) {
    global $input;
    $db = getDB();
    $id = newId();
    $db->prepare("INSERT INTO products (id,name,sku,barcode,description,category_id,supplier_id,unit_price,cost_price,quantity_in_stock,minimum_stock_level,maximum_stock_level,unit,is_active,image_url) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)")
        ->execute([$id, $input['name'], $input['sku'], $input['barcode']??null, $input['description']??null, $input['category_id']??null, $input['supplier_id']??null, $input['unit_price']??0, $input['cost_price']??0, $input['quantity_in_stock']??0, $input['minimum_stock_level']??0, $input['maximum_stock_level']??1000, $input['unit']??'piece', 1, $input['image_url']??null]);
    $stmt = $db->prepare("SELECT * FROM products WHERE id = ?");
    $stmt->execute([$id]);
    successResponse($stmt->fetch(), 'Product created');
}

function productsGet($p) {
    $db = getDB();
    $stmt = $db->prepare("SELECT * FROM products WHERE id = ?");
    $stmt->execute([$p['id']]);
    $item = $stmt->fetch();
    if (!$item) errorResponse('Product not found', 404);
    successResponse($item);
}

function productsUpdate($p) {
    global $input;
    $db = getDB();
    $fields = [];
    $params = [];
    foreach (['name','sku','barcode','description','category_id','supplier_id','unit_price','cost_price','quantity_in_stock','minimum_stock_level','maximum_stock_level','unit','is_active','image_url'] as $f) {
        if (array_key_exists($f, $input)) { $fields[] = "`$f` = ?"; $params[] = $input[$f]; }
    }
    if (empty($fields)) errorResponse('No fields to update');
    $params[] = $p['id'];
    $db->prepare("UPDATE products SET " . implode(', ', $fields) . " WHERE id = ?")->execute($params);
    $stmt = $db->prepare("SELECT * FROM products WHERE id = ?");
    $stmt->execute([$p['id']]);
    successResponse($stmt->fetch(), 'Product updated');
}

function productsDelete($p) {
    $db = getDB();
    $db->prepare("DELETE FROM products WHERE id = ?")->execute([$p['id']]);
    successResponse(null, 'Product deleted');
}

function productsLowStock($p) {
    $db = getDB();
    $stmt = $db->query("SELECT * FROM products WHERE quantity_in_stock <= minimum_stock_level AND is_active = 1 ORDER BY quantity_in_stock ASC");
    successResponse($stmt->fetchAll());
}


// ─── CATEGORIES ───────────────────────────────────────────────────────────────

function categoriesList($p) {
    $db = getDB();
    $stmt = $db->query("SELECT * FROM categories ORDER BY name");
    successResponse($stmt->fetchAll());
}

function categoriesCreate($p) {
    global $input;
    $db = getDB();
    $id = newId();
    $db->prepare("INSERT INTO categories (id,name,description,parent_id) VALUES (?,?,?,?)")
        ->execute([$id, $input['name'], $input['description']??null, $input['parent_id']??null]);
    $stmt = $db->prepare("SELECT * FROM categories WHERE id = ?");
    $stmt->execute([$id]);
    successResponse($stmt->fetch(), 'Category created');
}

function categoriesGet($p) {
    $db = getDB();
    $stmt = $db->prepare("SELECT * FROM categories WHERE id = ?");
    $stmt->execute([$p['id']]);
    $item = $stmt->fetch();
    if (!$item) errorResponse('Category not found', 404);
    successResponse($item);
}

function categoriesUpdate($p) {
    global $input;
    $db = getDB();
    $db->prepare("UPDATE categories SET name=?, description=?, parent_id=?, is_active=? WHERE id=?")
        ->execute([$input['name'], $input['description']??null, $input['parent_id']??null, $input['is_active'] ?? 1, $p['id']]);
    $stmt = $db->prepare("SELECT * FROM categories WHERE id = ?");
    $stmt->execute([$p['id']]);
    successResponse($stmt->fetch(), 'Category updated');
}

function categoriesDelete($p) {
    $db = getDB();
    $db->prepare("DELETE FROM categories WHERE id = ?")->execute([$p['id']]);
    successResponse(null, 'Category deleted');
}


// ─── CUSTOMERS ────────────────────────────────────────────────────────────────

function customersList($p) {
    $db = getDB();
    $page = max(1, (int)($_GET['page'] ?? 1));
    $per = min(100, max(1, (int)($_GET['per_page'] ?? 20)));
    $offset = ($page - 1) * $per;
    $search = $_GET['search'] ?? '';
    $where = 'WHERE 1=1';
    $params = [];
    if ($search) { $where .= " AND (name LIKE ? OR phone LIKE ?)"; $s = "%$search%"; $params = [$s,$s]; }
    $total = $db->prepare("SELECT COUNT(*) FROM customers $where");
    $total->execute($params);
    $stmt = $db->prepare("SELECT * FROM customers $where ORDER BY created_at DESC LIMIT $per OFFSET $offset");
    $stmt->execute($params);
    successResponse($stmt->fetchAll(), null, ['total' => (int)$total->fetchColumn(), 'page' => $page, 'per_page' => $per]);
}

function customersCreate($p) {
    global $input;
    $db = getDB();
    $id = newId();
    $db->prepare("INSERT INTO customers (id,name,phone,email,address,tax_number,credit_limit,notes) VALUES (?,?,?,?,?,?,?,?)")
        ->execute([$id, $input['name'], $input['phone']??'', $input['email']??null, $input['address']??null, $input['tax_number']??null, $input['credit_limit']??0, $input['notes']??null]);
    $stmt = $db->prepare("SELECT * FROM customers WHERE id = ?");
    $stmt->execute([$id]);
    successResponse($stmt->fetch(), 'Customer created');
}

function customersGet($p) {
    $db = getDB();
    $stmt = $db->prepare("SELECT * FROM customers WHERE id = ?");
    $stmt->execute([$p['id']]);
    $item = $stmt->fetch();
    if (!$item) errorResponse('Customer not found', 404);
    successResponse($item);
}

function customersUpdate($p) {
    global $input;
    $db = getDB();
    $db->prepare("UPDATE customers SET name=?,phone=?,email=?,address=?,tax_number=?,credit_limit=?,notes=?,is_active=? WHERE id=?")
        ->execute([$input['name'], $input['phone']??'', $input['email']??null, $input['address']??null, $input['tax_number']??null, $input['credit_limit']??0, $input['notes']??null, $input['is_active'] ?? 1, $p['id']]);
    $stmt = $db->prepare("SELECT * FROM customers WHERE id = ?");
    $stmt->execute([$p['id']]);
    successResponse($stmt->fetch(), 'Customer updated');
}

function customersDelete($p) {
    $db = getDB();
    $db->prepare("DELETE FROM customers WHERE id = ?")->execute([$p['id']]);
    successResponse(null, 'Customer deleted');
}

function customerStatement($p) {
    $db = getDB();
    $orders = $db->prepare("SELECT id,order_number,total,status,created_at FROM sale_orders WHERE customer_id = ? ORDER BY created_at DESC");
    $orders->execute([$p['id']]);
    $debts = $db->prepare("SELECT * FROM customer_debts WHERE customer_id = ? ORDER BY created_at DESC");
    $debts->execute([$p['id']]);
    $payments = $db->prepare("SELECT dp.* FROM debt_payments dp JOIN customer_debts cd ON dp.debt_id = cd.id WHERE cd.customer_id = ? ORDER BY dp.created_at DESC");
    $payments->execute([$p['id']]);
    successResponse(['orders' => $orders->fetchAll(), 'debts' => $debts->fetchAll(), 'payments' => $payments->fetchAll()]);
}


// ─── SUPPLIERS ────────────────────────────────────────────────────────────────

function suppliersList($p) {
    $db = getDB();
    $page = max(1, (int)($_GET['page'] ?? 1));
    $per = min(100, max(1, (int)($_GET['per_page'] ?? 20)));
    $offset = ($page - 1) * $per;
    $search = $_GET['search'] ?? '';
    $where = 'WHERE 1=1';
    $params = [];
    if ($search) { $where .= " AND (name LIKE ? OR phone LIKE ?)"; $s = "%$search%"; $params = [$s,$s]; }
    $total = $db->prepare("SELECT COUNT(*) FROM suppliers $where");
    $total->execute($params);
    $stmt = $db->prepare("SELECT * FROM suppliers $where ORDER BY created_at DESC LIMIT $per OFFSET $offset");
    $stmt->execute($params);
    successResponse($stmt->fetchAll(), null, ['total' => (int)$total->fetchColumn(), 'page' => $page, 'per_page' => $per]);
}

function suppliersCreate($p) {
    global $input;
    $db = getDB();
    $id = newId();
    $db->prepare("INSERT INTO suppliers (id,name,phone,email,address,tax_number,payment_terms_days,notes) VALUES (?,?,?,?,?,?,?,?)")
        ->execute([$id, $input['name'], $input['phone']??'', $input['email']??null, $input['address']??null, $input['tax_number']??null, $input['payment_terms_days']??30, $input['notes']??null]);
    $stmt = $db->prepare("SELECT * FROM suppliers WHERE id = ?");
    $stmt->execute([$id]);
    successResponse($stmt->fetch(), 'Supplier created');
}

function suppliersGet($p) {
    $db = getDB();
    $stmt = $db->prepare("SELECT * FROM suppliers WHERE id = ?");
    $stmt->execute([$p['id']]);
    $item = $stmt->fetch();
    if (!$item) errorResponse('Supplier not found', 404);
    successResponse($item);
}

function suppliersUpdate($p) {
    global $input;
    $db = getDB();
    $db->prepare("UPDATE suppliers SET name=?,phone=?,email=?,address=?,tax_number=?,payment_terms_days=?,notes=?,is_active=? WHERE id=?")
        ->execute([$input['name'], $input['phone']??'', $input['email']??null, $input['address']??null, $input['tax_number']??null, $input['payment_terms_days']??30, $input['notes']??null, $input['is_active'] ?? 1, $p['id']]);
    $stmt = $db->prepare("SELECT * FROM suppliers WHERE id = ?");
    $stmt->execute([$p['id']]);
    successResponse($stmt->fetch(), 'Supplier updated');
}

function suppliersDelete($p) {
    $db = getDB();
    $db->prepare("DELETE FROM suppliers WHERE id = ?")->execute([$p['id']]);
    successResponse(null, 'Supplier deleted');
}

function supplierStatement($p) {
    $db = getDB();
    $orders = $db->prepare("SELECT id,order_number,total,status,created_at FROM purchase_orders WHERE supplier_id = ? ORDER BY created_at DESC");
    $orders->execute([$p['id']]);
    $debts = $db->prepare("SELECT * FROM supplier_debts WHERE supplier_id = ? ORDER BY created_at DESC");
    $debts->execute([$p['id']]);
    successResponse(['orders' => $orders->fetchAll(), 'debts' => $debts->fetchAll()]);
}


// ─── SALE ORDERS ──────────────────────────────────────────────────────────────

function saleOrdersList($p) {
    $db = getDB();
    $page = max(1, (int)($_GET['page'] ?? 1));
    $per = min(100, max(1, (int)($_GET['per_page'] ?? 20)));
    $offset = ($page - 1) * $per;
    $search = $_GET['search'] ?? '';
    $where = 'WHERE 1=1';
    $params = [];
    if ($search) { $where .= " AND (order_number LIKE ? OR customer_id IN (SELECT id FROM customers WHERE name LIKE ?))"; $s = "%$search%"; $params = [$s,$s]; }
    if (!empty($_GET['from_date'])) { $where .= " AND DATE(created_at) >= ?"; $params[] = $_GET['from_date']; }
    if (!empty($_GET['to_date'])) { $where .= " AND DATE(created_at) <= ?"; $params[] = $_GET['to_date']; }
    $total = $db->prepare("SELECT COUNT(*) FROM sale_orders $where");
    $total->execute($params);
    $stmt = $db->prepare("SELECT * FROM sale_orders $where ORDER BY created_at DESC LIMIT $per OFFSET $offset");
    $stmt->execute($params);
    successResponse($stmt->fetchAll(), null, ['total' => (int)$total->fetchColumn(), 'page' => $page, 'per_page' => $per]);
}

function saleOrdersCreate($p) {
    global $input;
    $db = getDB();
    $id = newId();
    $orderNum = 'SO-' . date('Ymd') . '-' . str_pad(mt_rand(1, 9999), 4, '0', STR_PAD_LEFT);
    $items = $input['items'] ?? [];
    $subtotal = 0;
    foreach ($items as $item) {
        $total = ($item['unit_price'] * $item['quantity']) - ($item['discount'] ?? 0);
        $subtotal += $total;
    }
    $taxRate = $input['tax_rate'] ?? 0.14;
    $tax = $subtotal * $taxRate;
    $discount = $input['discount'] ?? 0;
    $totalAll = $subtotal + $tax - $discount;

    $user = requireAuth();
    $db->prepare("INSERT INTO sale_orders (id,order_number,customer_id,user_id,status,subtotal,discount,tax_amount,total,payment_method,notes) VALUES (?,?,?,?,?,?,?,?,?,?,?)")
        ->execute([$id, $orderNum, $input['customer_id'], $user['sub'], 'draft', $subtotal, $discount, $tax, $totalAll, $input['payment_method'] ?? 'cash', $input['notes'] ?? null]);

    foreach ($items as $item) {
        $itemId = newId();
        $itemTotal = ($item['unit_price'] * $item['quantity']) - ($item['discount'] ?? 0);
        $db->prepare("INSERT INTO sale_order_items (id,order_id,product_id,quantity,unit_price,discount,total) VALUES (?,?,?,?,?,?,?)")
            ->execute([$itemId, $id, $item['product_id'], $item['quantity'], $item['unit_price'], $item['discount'] ?? 0, $itemTotal]);
        $db->prepare("UPDATE products SET quantity_in_stock = quantity_in_stock - ? WHERE id = ?")->execute([$item['quantity'], $item['product_id']]);
    }

    // Create customer debt
    $db->prepare("INSERT INTO customer_debts (id,customer_id,amount,paid_amount,remaining,status,description) VALUES (?,?,?,?,?,?,?)")
        ->execute([newId(), $input['customer_id'], $totalAll, 0, $totalAll, 'pending', "Sale: $orderNum"]);

    $stmt = $db->prepare("SELECT * FROM sale_orders WHERE id = ?");
    $stmt->execute([$id]);
    successResponse($stmt->fetch(), 'Sale order created');
}

function saleOrdersGet($p) {
    $db = getDB();
    $stmt = $db->prepare("SELECT * FROM sale_orders WHERE id = ?");
    $stmt->execute([$p['id']]);
    $order = $stmt->fetch();
    if (!$order) errorResponse('Order not found', 404);
    $items = $db->prepare("SELECT * FROM sale_order_items WHERE order_id = ?");
    $items->execute([$p['id']]);
    $order['items'] = $items->fetchAll();
    successResponse($order);
}

function saleOrdersUpdate($p) {
    global $input;
    $db = getDB();
    $db->prepare("UPDATE sale_orders SET notes=?, payment_method=? WHERE id=?")
        ->execute([$input['notes'] ?? null, $input['payment_method'] ?? 'cash', $p['id']]);
    $stmt = $db->prepare("SELECT * FROM sale_orders WHERE id = ?");
    $stmt->execute([$p['id']]);
    successResponse($stmt->fetch(), 'Order updated');
}

function saleOrdersDelete($p) {
    $db = getDB();
    $items = $db->prepare("SELECT product_id, quantity FROM sale_order_items WHERE order_id = ?");
    $items->execute([$p['id']]);
    while ($item = $items->fetch()) {
        $db->prepare("UPDATE products SET quantity_in_stock = quantity_in_stock + ? WHERE id = ?")->execute([$item['quantity'], $item['product_id']]);
    }
    $db->prepare("DELETE FROM sale_order_items WHERE order_id = ?")->execute([$p['id']]);
    $db->prepare("DELETE FROM sale_orders WHERE id = ?")->execute([$p['id']]);
    successResponse(null, 'Order deleted');
}

function saleOrdersStatus($p) {
    global $input;
    $db = getDB();
    $db->prepare("UPDATE sale_orders SET status = ? WHERE id = ?")->execute([$input['status'], $p['id']]);
    successResponse(null, 'Status updated');
}


// ─── SALE RETURNS ─────────────────────────────────────────────────────────────

function saleReturnsList($p) {
    $db = getDB();
    $page = max(1, (int)($_GET['page'] ?? 1));
    $per = min(100, max(1, (int)($_GET['per_page'] ?? 20)));
    $offset = ($page - 1) * $per;
    $total = $db->query("SELECT COUNT(*) FROM sale_returns")->fetchColumn();
    $stmt = $db->prepare("SELECT * FROM sale_returns ORDER BY created_at DESC LIMIT $per OFFSET $offset");
    $stmt->execute();
    successResponse($stmt->fetchAll(), null, ['total' => (int)$total, 'page' => $page, 'per_page' => $per]);
}

function saleReturnsCreate($p) {
    global $input;
    $db = getDB();
    $user = requireAuth();
    $id = newId();
    $returnNum = 'SR-' . date('Ymd') . '-' . str_pad(mt_rand(1, 9999), 4, '0', STR_PAD_LEFT);
    $items = $input['items'] ?? [];
    $subtotal = 0;
    foreach ($items as $item) {
        $subtotal += $item['unit_price'] * $item['quantity'];
        $db->prepare("UPDATE products SET quantity_in_stock = quantity_in_stock + ? WHERE id = ?")->execute([$item['quantity'], $item['product_id']]);
    }
    $tax = $subtotal * 0.14;
    $total = $subtotal + $tax;
    $db->prepare("INSERT INTO sale_returns (id,return_number,order_id,customer_id,user_id,status,subtotal,tax_amount,total,reason,notes) VALUES (?,?,?,?,?,?,?,?,?,?,?)")
        ->execute([$id, $returnNum, $input['order_id'], $input['customer_id'] ?? '', $user['sub'], 'completed', $subtotal, $tax, $total, $input['reason'] ?? '', $input['notes'] ?? '']);
    foreach ($items as $item) {
        $db->prepare("INSERT INTO sale_return_items (id,return_id,product_id,quantity,unit_price,total) VALUES (?,?,?,?,?,?)")
            ->execute([newId(), $id, $item['product_id'], $item['quantity'], $item['unit_price'], $item['unit_price'] * $item['quantity']]);
    }
    successResponse(['id' => $id, 'return_number' => $returnNum, 'total' => $total], 'Sale return created');
}

function saleReturnsGet($p) {
    $db = getDB();
    $stmt = $db->prepare("SELECT * FROM sale_returns WHERE id = ?");
    $stmt->execute([$p['id']]);
    $ret = $stmt->fetch();
    if (!$ret) errorResponse('Return not found', 404);
    $items = $db->prepare("SELECT * FROM sale_return_items WHERE return_id = ?");
    $items->execute([$p['id']]);
    $ret['items'] = $items->fetchAll();
    successResponse($ret);
}


// ─── PURCHASE ORDERS ──────────────────────────────────────────────────────────

function purchaseOrdersList($p) {
    $db = getDB();
    $page = max(1, (int)($_GET['page'] ?? 1));
    $per = min(100, max(1, (int)($_GET['per_page'] ?? 20)));
    $offset = ($page - 1) * $per;
    $search = $_GET['search'] ?? '';
    $where = 'WHERE 1=1';
    $params = [];
    if ($search) { $where .= " AND (order_number LIKE ?)"; $params = ["%$search%"]; }
    $total = $db->prepare("SELECT COUNT(*) FROM purchase_orders $where");
    $total->execute($params);
    $stmt = $db->prepare("SELECT * FROM purchase_orders $where ORDER BY created_at DESC LIMIT $per OFFSET $offset");
    $stmt->execute($params);
    successResponse($stmt->fetchAll(), null, ['total' => (int)$total->fetchColumn(), 'page' => $page, 'per_page' => $per]);
}

function purchaseOrdersCreate($p) {
    global $input;
    $db = getDB();
    $user = requireAuth();
    $id = newId();
    $orderNum = 'PO-' . date('Ymd') . '-' . str_pad(mt_rand(1, 9999), 4, '0', STR_PAD_LEFT);
    $items = $input['items'] ?? [];
    $subtotal = 0;
    foreach ($items as $item) {
        $total = ($item['unit_price'] * $item['quantity']) - ($item['discount'] ?? 0);
        $subtotal += $total;
    }
    $tax = $subtotal * ($input['tax_rate'] ?? 0.14);
    $discount = $input['discount'] ?? 0;
    $totalAll = $subtotal + $tax - $discount;
    $db->prepare("INSERT INTO purchase_orders (id,order_number,supplier_id,user_id,status,subtotal,discount,tax_amount,total,payment_method,notes) VALUES (?,?,?,?,?,?,?,?,?,?,?)")
        ->execute([$id, $orderNum, $input['supplier_id'], $user['sub'], 'draft', $subtotal, $discount, $tax, $totalAll, $input['payment_method'] ?? 'cash', $input['notes'] ?? null]);
    foreach ($items as $item) {
        $itemId = newId();
        $itemTotal = ($item['unit_price'] * $item['quantity']) - ($item['discount'] ?? 0);
        $db->prepare("INSERT INTO purchase_order_items (id,order_id,product_id,quantity,unit_price,discount,total) VALUES (?,?,?,?,?,?,?)")
            ->execute([$itemId, $id, $item['product_id'], $item['quantity'], $item['unit_price'], $item['discount'] ?? 0, $itemTotal]);
        $db->prepare("UPDATE products SET quantity_in_stock = quantity_in_stock + ? WHERE id = ?")->execute([$item['quantity'], $item['product_id']]);
    }
    $db->prepare("INSERT INTO supplier_debts (id,supplier_id,amount,paid_amount,remaining,status,description) VALUES (?,?,?,?,?,?,?)")
        ->execute([newId(), $input['supplier_id'], $totalAll, 0, $totalAll, 'pending', "Purchase: $orderNum"]);
    $stmt = $db->prepare("SELECT * FROM purchase_orders WHERE id = ?");
    $stmt->execute([$id]);
    successResponse($stmt->fetch(), 'Purchase order created');
}

function purchaseOrdersGet($p) {
    $db = getDB();
    $stmt = $db->prepare("SELECT * FROM purchase_orders WHERE id = ?");
    $stmt->execute([$p['id']]);
    $order = $stmt->fetch();
    if (!$order) errorResponse('Order not found', 404);
    $items = $db->prepare("SELECT * FROM purchase_order_items WHERE order_id = ?");
    $items->execute([$p['id']]);
    $order['items'] = $items->fetchAll();
    successResponse($order);
}

function purchaseOrdersUpdate($p) {
    global $input;
    $db = getDB();
    $db->prepare("UPDATE purchase_orders SET notes=?, payment_method=? WHERE id=?")
        ->execute([$input['notes'] ?? null, $input['payment_method'] ?? 'cash', $p['id']]);
    successResponse(null, 'Order updated');
}

function purchaseOrdersDelete($p) {
    $db = getDB();
    $items = $db->prepare("SELECT product_id, quantity FROM purchase_order_items WHERE order_id = ?");
    $items->execute([$p['id']]);
    while ($item = $items->fetch()) {
        $db->prepare("UPDATE products SET quantity_in_stock = quantity_in_stock - ? WHERE id = ?")->execute([$item['quantity'], $item['product_id']]);
    }
    $db->prepare("DELETE FROM purchase_order_items WHERE order_id = ?")->execute([$p['id']]);
    $db->prepare("DELETE FROM purchase_orders WHERE id = ?")->execute([$p['id']]);
    successResponse(null, 'Order deleted');
}

function purchaseOrdersStatus($p) {
    global $input;
    $db = getDB();
    $db->prepare("UPDATE purchase_orders SET status = ? WHERE id = ?")->execute([$input['status'], $p['id']]);
    successResponse(null, 'Status updated');
}


// ─── PURCHASE RETURNS ─────────────────────────────────────────────────────────

function purchaseReturnsList($p) {
    $db = getDB();
    $page = max(1, (int)($_GET['page'] ?? 1));
    $per = min(100, max(1, (int)($_GET['per_page'] ?? 20)));
    $offset = ($page - 1) * $per;
    $total = $db->query("SELECT COUNT(*) FROM purchase_returns")->fetchColumn();
    $stmt = $db->prepare("SELECT * FROM purchase_returns ORDER BY created_at DESC LIMIT $per OFFSET $offset");
    $stmt->execute();
    successResponse($stmt->fetchAll(), null, ['total' => (int)$total, 'page' => $page, 'per_page' => $per]);
}

function purchaseReturnsCreate($p) {
    global $input;
    $db = getDB();
    $user = requireAuth();
    $id = newId();
    $returnNum = 'PR-' . date('Ymd') . '-' . str_pad(mt_rand(1, 9999), 4, '0', STR_PAD_LEFT);
    $items = $input['items'] ?? [];
    $subtotal = 0;
    foreach ($items as $item) {
        $subtotal += $item['unit_price'] * $item['quantity'];
        $db->prepare("UPDATE products SET quantity_in_stock = quantity_in_stock - ? WHERE id = ?")->execute([$item['quantity'], $item['product_id']]);
    }
    $tax = $subtotal * 0.14;
    $total = $subtotal + $tax;
    $db->prepare("INSERT INTO purchase_returns (id,return_number,order_id,supplier_id,user_id,status,subtotal,tax_amount,total,reason,notes) VALUES (?,?,?,?,?,?,?,?,?,?,?)")
        ->execute([$id, $returnNum, $input['order_id'], $input['supplier_id'] ?? '', $user['sub'], 'completed', $subtotal, $tax, $total, $input['reason'] ?? '', $input['notes'] ?? '']);
    foreach ($items as $item) {
        $db->prepare("INSERT INTO purchase_return_items (id,return_id,product_id,quantity,unit_price,total) VALUES (?,?,?,?,?,?)")
            ->execute([newId(), $id, $item['product_id'], $item['quantity'], $item['unit_price'], $item['unit_price'] * $item['quantity']]);
    }
    successResponse(['id' => $id, 'return_number' => $returnNum, 'total' => $total], 'Purchase return created');
}

function purchaseReturnsGet($p) {
    $db = getDB();
    $stmt = $db->prepare("SELECT * FROM purchase_returns WHERE id = ?");
    $stmt->execute([$p['id']]);
    $ret = $stmt->fetch();
    if (!$ret) errorResponse('Return not found', 404);
    $items = $db->prepare("SELECT * FROM purchase_return_items WHERE return_id = ?");
    $items->execute([$p['id']]);
    $ret['items'] = $items->fetchAll();
    successResponse($ret);
}


// ─── ACCOUNTING ───────────────────────────────────────────────────────────────

function accountingCustomers($p) {
    $db = getDB();
    $page = max(1, (int)($_GET['page'] ?? 1));
    $per = min(100, max(1, (int)($_GET['per_page'] ?? 20)));
    $offset = ($page - 1) * $per;
    $total = $db->query("SELECT COUNT(*) FROM customer_debts")->fetchColumn();
    $stmt = $db->prepare("SELECT cd.*, c.name as customer_name FROM customer_debts cd LEFT JOIN customers c ON cd.customer_id = c.id ORDER BY cd.created_at DESC LIMIT $per OFFSET $offset");
    $stmt->execute();
    successResponse($stmt->fetchAll(), null, ['total' => (int)$total, 'page' => $page, 'per_page' => $per]);
}

function accountingCustomerGet($p) {
    $db = getDB();
    $stmt = $db->prepare("SELECT cd.*, c.name as customer_name FROM customer_debts cd LEFT JOIN customers c ON cd.customer_id = c.id WHERE cd.id = ?");
    $stmt->execute([$p['id']]);
    $item = $stmt->fetch();
    if (!$item) errorResponse('Not found', 404);
    $payments = $db->prepare("SELECT * FROM debt_payments WHERE debt_id = ? ORDER BY created_at DESC");
    $payments->execute([$p['id']]);
    $item['payments'] = $payments->fetchAll();
    successResponse($item);
}

function accountingCustomerCreate($p) {
    global $input;
    $db = getDB();
    $id = newId();
    $db->prepare("INSERT INTO customer_debts (id,customer_id,amount,paid_amount,remaining,status,description,due_date) VALUES (?,?,?,?,?,?,?,?)")
        ->execute([$id, $input['customer_id'], $input['amount'], 0, $input['amount'], 'pending', $input['description'] ?? '', $input['due_date'] ?? null]);
    successResponse(['id' => $id], 'Debt created');
}

function accountingCustomerPayment($p) {
    global $input;
    $db = getDB();
    $user = requireAuth();
    $debtId = $input['debt_id'];
    $amount = $input['amount'];
    $stmt = $db->prepare("SELECT * FROM customer_debts WHERE id = ?");
    $stmt->execute([$debtId]);
    $debt = $stmt->fetch();
    if (!$debt) errorResponse('Debt not found', 404);
    $db->prepare("INSERT INTO debt_payments (id,debt_id,debt_type,amount,payment_method,notes,user_id) VALUES (?,?,?,?,?,?,?)")
        ->execute([newId(), $debtId, 'customer', $amount, $input['payment_method'] ?? 'cash', $input['notes'] ?? '', $user['sub']]);
    $newPaid = $debt['paid_amount'] + $amount;
    $newRemaining = $debt['amount'] - $newPaid;
    $newStatus = $newRemaining <= 0 ? 'paid' : 'partial';
    $db->prepare("UPDATE customer_debts SET paid_amount=?, remaining=?, status=? WHERE id=?")
        ->execute([$newPaid, max(0, $newRemaining), $newStatus, $debtId]);
    successResponse(null, 'Payment recorded');
}

function accountingSuppliers($p) {
    $db = getDB();
    $page = max(1, (int)($_GET['page'] ?? 1));
    $per = min(100, max(1, (int)($_GET['per_page'] ?? 20)));
    $offset = ($page - 1) * $per;
    $total = $db->query("SELECT COUNT(*) FROM supplier_debts")->fetchColumn();
    $stmt = $db->prepare("SELECT sd.*, s.name as supplier_name FROM supplier_debts sd LEFT JOIN suppliers s ON sd.supplier_id = s.id ORDER BY sd.created_at DESC LIMIT $per OFFSET $offset");
    $stmt->execute();
    successResponse($stmt->fetchAll(), null, ['total' => (int)$total, 'page' => $page, 'per_page' => $per]);
}

function accountingSupplierGet($p) {
    $db = getDB();
    $stmt = $db->prepare("SELECT sd.*, s.name as supplier_name FROM supplier_debts sd LEFT JOIN suppliers s ON sd.supplier_id = s.id WHERE sd.id = ?");
    $stmt->execute([$p['id']]);
    $item = $stmt->fetch();
    if (!$item) errorResponse('Not found', 404);
    successResponse($item);
}

function accountingSupplierCreate($p) {
    global $input;
    $db = getDB();
    $id = newId();
    $db->prepare("INSERT INTO supplier_debts (id,supplier_id,amount,paid_amount,remaining,status,description,due_date) VALUES (?,?,?,?,?,?,?,?)")
        ->execute([$id, $input['supplier_id'], $input['amount'], 0, $input['amount'], 'pending', $input['description'] ?? '', $input['due_date'] ?? null]);
    successResponse(['id' => $id], 'Debt created');
}

function accountingSupplierPayment($p) {
    global $input;
    $db = getDB();
    $user = requireAuth();
    $debtId = $input['debt_id'];
    $amount = $input['amount'];
    $stmt = $db->prepare("SELECT * FROM supplier_debts WHERE id = ?");
    $stmt->execute([$debtId]);
    $debt = $stmt->fetch();
    if (!$debt) errorResponse('Debt not found', 404);
    $db->prepare("INSERT INTO debt_payments (id,debt_id,debt_type,amount,payment_method,notes,user_id) VALUES (?,?,?,?,?,?,?)")
        ->execute([newId(), $debtId, 'supplier', $amount, $input['payment_method'] ?? 'cash', $input['notes'] ?? '', $user['sub']]);
    $newPaid = $debt['paid_amount'] + $amount;
    $newRemaining = $debt['amount'] - $newPaid;
    $newStatus = $newRemaining <= 0 ? 'paid' : 'partial';
    $db->prepare("UPDATE supplier_debts SET paid_amount=?, remaining=?, status=? WHERE id=?")
        ->execute([$newPaid, max(0, $newRemaining), $newStatus, $debtId]);
    successResponse(null, 'Payment recorded');
}


// ─── CASHBOX ──────────────────────────────────────────────────────────────────

function cashboxList($p) {
    $db = getDB();
    $stmt = $db->query("SELECT * FROM cashboxes WHERE is_active = 1");
    successResponse($stmt->fetchAll());
}

function cashboxGet($p) {
    $db = getDB();
    $stmt = $db->prepare("SELECT * FROM cashboxes WHERE id = ?");
    $stmt->execute([$p['id']]);
    $item = $stmt->fetch();
    if (!$item) errorResponse('Cashbox not found', 404);
    successResponse($item);
}

function cashboxTransaction($p) {
    global $input;
    $db = getDB();
    $user = requireAuth();
    $id = newId();
    $amount = $input['amount'];
    $type = $input['transaction_type'];
    $db->prepare("INSERT INTO cashbox_transactions (id,cashbox_id,transaction_type,amount,description,reference_id,user_id) VALUES (?,?,?,?,?,?,?)")
        ->execute([$id, $p['id'], $type, $amount, $input['description'] ?? '', $input['reference_id'] ?? null, $user['sub']]);
    if ($type === 'income') {
        $db->prepare("UPDATE cashboxes SET balance = balance + ? WHERE id = ?")->execute([$amount, $p['id']]);
    } else {
        $db->prepare("UPDATE cashboxes SET balance = balance - ? WHERE id = ?")->execute([$amount, $p['id']]);
    }
    successResponse(['id' => $id], 'Transaction recorded');
}

function cashboxTransactions($p) {
    $db = getDB();
    $page = max(1, (int)($_GET['page'] ?? 1));
    $per = min(100, max(1, (int)($_GET['per_page'] ?? 20)));
    $offset = ($page - 1) * $per;
    $total = $db->prepare("SELECT COUNT(*) FROM cashbox_transactions WHERE cashbox_id = ?");
    $total->execute([$p['id']]);
    $stmt = $db->prepare("SELECT * FROM cashbox_transactions WHERE cashbox_id = ? ORDER BY created_at DESC LIMIT $per OFFSET $offset");
    $stmt->execute([$p['id']]);
    successResponse($stmt->fetchAll(), null, ['total' => (int)$total->fetchColumn(), 'page' => $page, 'per_page' => $per]);
}


// ─── CASHBOX TRANSFERS ────────────────────────────────────────────────────────

function cashboxTransfersList($p) {
    $db = getDB();
    $page = max(1, (int)($_GET['page'] ?? 1));
    $per = min(100, max(1, (int)($_GET['per_page'] ?? 20)));
    $offset = ($page - 1) * $per;
    $total = $db->query("SELECT COUNT(*) FROM cashbox_transfers")->fetchColumn();
    $stmt = $db->prepare("SELECT * FROM cashbox_transfers ORDER BY created_at DESC LIMIT $per OFFSET $offset");
    $stmt->execute();
    successResponse($stmt->fetchAll(), null, ['total' => (int)$total, 'page' => $page, 'per_page' => $per]);
}

function cashboxTransfersCreate($p) {
    global $input;
    $db = getDB();
    $user = requireAuth();
    $fromId = $input['from_cashbox_id'];
    $toId = $input['to_cashbox_id'];
    $amount = $input['amount'];
    if ($fromId === $toId) errorResponse('Source and destination must be different');
    $from = $db->prepare("SELECT balance FROM cashboxes WHERE id = ?");
    $from->execute([$fromId]);
    $box = $from->fetch();
    if (!$box || $box['balance'] < $amount) errorResponse('Insufficient balance');
    $id = newId();
    $transferNum = 'CT-' . date('YmdHis') . '-' . substr(md5($id), 0, 6);
    $db->prepare("INSERT INTO cashbox_transfers (id,transfer_number,from_cashbox_id,to_cashbox_id,amount,description,user_id) VALUES (?,?,?,?,?,?,?)")
        ->execute([$id, $transferNum, $fromId, $toId, $amount, $input['description'] ?? '', $user['sub']]);
    $db->prepare("UPDATE cashboxes SET balance = balance - ? WHERE id = ?")->execute([$amount, $fromId]);
    $db->prepare("UPDATE cashboxes SET balance = balance + ? WHERE id = ?")->execute([$amount, $toId]);
    successResponse(['id' => $id, 'transfer_number' => $transferNum], 'Transfer completed');
}


// ─── ACCOUNTING REPORTS ───────────────────────────────────────────────────────

function accountingReportSummary($p) {
    $db = getDB();
    $totalSales = $db->query("SELECT COALESCE(SUM(total),0) FROM sale_orders WHERE status != 'cancelled'")->fetchColumn();
    $totalPurchases = $db->query("SELECT COALESCE(SUM(total),0) FROM purchase_orders WHERE status != 'cancelled'")->fetchColumn();
    $totalReceivable = $db->query("SELECT COALESCE(SUM(remaining),0) FROM customer_debts WHERE status IN ('pending','partial','overdue')")->fetchColumn();
    $totalPayable = $db->query("SELECT COALESCE(SUM(remaining),0) FROM supplier_debts WHERE status IN ('pending','partial','overdue')")->fetchColumn();
    $txCount = $db->query("SELECT COUNT(*) FROM cashbox_transactions")->fetchColumn();
    successResponse([
        'total_sales' => (float)$totalSales, 'total_purchases' => (float)$totalPurchases,
        'net_profit' => (float)($totalSales - $totalPurchases),
        'total_receivable' => (float)$totalReceivable, 'total_payable' => (float)$totalPayable,
        'transaction_count' => (int)$txCount,
    ]);
}

function accountingReportTransactions($p) {
    $db = getDB();
    $page = max(1, (int)($_GET['page'] ?? 1));
    $per = min(100, max(1, (int)($_GET['per_page'] ?? 20)));
    $offset = ($page - 1) * $per;
    $total = $db->query("SELECT COUNT(*) FROM cashbox_transactions")->fetchColumn();
    $stmt = $db->prepare("SELECT * FROM cashbox_transactions ORDER BY created_at DESC LIMIT $per OFFSET $offset");
    $stmt->execute();
    successResponse($stmt->fetchAll(), null, ['total' => (int)$total, 'page' => $page, 'per_page' => $per]);
}


// ─── INVENTORY ────────────────────────────────────────────────────────────────

function warehousesList($p) {
    $db = getDB();
    $stmt = $db->query("SELECT * FROM warehouses ORDER BY name");
    successResponse($stmt->fetchAll());
}

function warehousesCreate($p) {
    global $input;
    $db = getDB();
    $id = newId();
    $db->prepare("INSERT INTO warehouses (id,name,location) VALUES (?,?,?)")
        ->execute([$id, $input['name'], $input['location'] ?? '']);
    $stmt = $db->prepare("SELECT * FROM warehouses WHERE id = ?");
    $stmt->execute([$id]);
    successResponse($stmt->fetch(), 'Warehouse created');
}

function warehousesUpdate($p) {
    global $input;
    $db = getDB();
    $db->prepare("UPDATE warehouses SET name=?, location=? WHERE id=?")
        ->execute([$input['name'], $input['location'] ?? '', $p['id']]);
    $stmt = $db->prepare("SELECT * FROM warehouses WHERE id = ?");
    $stmt->execute([$p['id']]);
    successResponse($stmt->fetch(), 'Warehouse updated');
}

function warehousesDelete($p) {
    $db = getDB();
    $db->prepare("DELETE FROM warehouses WHERE id = ?")->execute([$p['id']]);
    successResponse(null, 'Warehouse deleted');
}

function warehouseStock($p) {
    $db = getDB();
    $stmt = $db->prepare("SELECT ws.*, p.name as product_name, p.sku as product_sku FROM warehouse_stocks ws LEFT JOIN products p ON ws.product_id = p.id WHERE ws.warehouse_id = ?");
    $stmt->execute([$p['id']]);
    successResponse($stmt->fetchAll());
}

function stockMovementsList($p) {
    $db = getDB();
    $page = max(1, (int)($_GET['page'] ?? 1));
    $per = min(100, max(1, (int)($_GET['per_page'] ?? 20)));
    $offset = ($page - 1) * $per;
    $total = $db->query("SELECT COUNT(*) FROM stock_movements")->fetchColumn();
    $stmt = $db->prepare("SELECT * FROM stock_movements ORDER BY created_at DESC LIMIT $per OFFSET $offset");
    $stmt->execute();
    successResponse($stmt->fetchAll(), null, ['total' => (int)$total, 'page' => $page, 'per_page' => $per]);
}

function stockMovementsCreate($p) {
    global $input;
    $db = getDB();
    $user = requireAuth();
    $id = newId();
    $moveNum = 'SM-' . date('YmdHis') . '-' . substr(md5($id), 0, 6);
    $db->prepare("INSERT INTO stock_movements (id,movement_number,product_id,warehouse_id,movement_type,quantity,reference_id,notes,user_id) VALUES (?,?,?,?,?,?,?,?,?)")
        ->execute([$id, $moveNum, $input['product_id'], $input['warehouse_id'], $input['movement_type'], $input['quantity'], $input['reference_id'] ?? null, $input['notes'] ?? '', $user['sub']]);
    // Update warehouse stock
    $ws = $db->prepare("SELECT * FROM warehouse_stocks WHERE warehouse_id = ? AND product_id = ?");
    $ws->execute([$input['warehouse_id'], $input['product_id']]);
    $existing = $ws->fetch();
    if ($existing) {
        $newQty = $existing['quantity'] + $input['quantity'];
        if (in_array($input['movement_type'], ['sale', 'transfer', 'damage'])) $newQty = $existing['quantity'] - $input['quantity'];
        $db->prepare("UPDATE warehouse_stocks SET quantity = ? WHERE id = ?")->execute([max(0, $newQty), $existing['id']]);
    } else {
        $db->prepare("INSERT INTO warehouse_stocks (id,warehouse_id,product_id,quantity) VALUES (?,?,?,?)")
            ->execute([newId(), $input['warehouse_id'], $input['product_id'], $input['quantity']]);
    }
    successResponse(['id' => $id], 'Stock movement recorded');
}

function stockTransfersList($p) {
    $db = getDB();
    $page = max(1, (int)($_GET['page'] ?? 1));
    $per = min(100, max(1, (int)($_GET['per_page'] ?? 20)));
    $offset = ($page - 1) * $per;
    $total = $db->query("SELECT COUNT(*) FROM stock_transfers")->fetchColumn();
    $stmt = $db->prepare("SELECT * FROM stock_transfers ORDER BY created_at DESC LIMIT $per OFFSET $offset");
    $stmt->execute();
    successResponse($stmt->fetchAll(), null, ['total' => (int)$total, 'page' => $page, 'per_page' => $per]);
}

function stockTransfersCreate($p) {
    global $input;
    $db = getDB();
    $user = requireAuth();
    if ($input['from_warehouse_id'] === $input['to_warehouse_id']) errorResponse('Source and destination must be different');
    $id = newId();
    $transferNum = 'ST-' . date('YmdHis') . '-' . substr(md5($id), 0, 6);
    $db->prepare("INSERT INTO stock_transfers (id,transfer_number,product_id,from_warehouse_id,to_warehouse_id,quantity,status,notes,user_id) VALUES (?,?,?,?,?,?,?,?,?)")
        ->execute([$id, $transferNum, $input['product_id'], $input['from_warehouse_id'], $input['to_warehouse_id'], $input['quantity'], 'completed', $input['notes'] ?? '', $user['sub']]);
    // Update source warehouse stock
    $fromWs = $db->prepare("SELECT * FROM warehouse_stocks WHERE warehouse_id = ? AND product_id = ?");
    $fromWs->execute([$input['from_warehouse_id'], $input['product_id']]);
    $fs = $fromWs->fetch();
    if ($fs) $db->prepare("UPDATE warehouse_stocks SET quantity = quantity - ? WHERE id = ?")->execute([$input['quantity'], $fs['id']]);
    // Update destination warehouse stock
    $toWs = $db->prepare("SELECT * FROM warehouse_stocks WHERE warehouse_id = ? AND product_id = ?");
    $toWs->execute([$input['to_warehouse_id'], $input['product_id']]);
    $ts = $toWs->fetch();
    if ($ts) {
        $db->prepare("UPDATE warehouse_stocks SET quantity = quantity + ? WHERE id = ?")->execute([$input['quantity'], $ts['id']]);
    } else {
        $db->prepare("INSERT INTO warehouse_stocks (id,warehouse_id,product_id,quantity) VALUES (?,?,?,?)")
            ->execute([newId(), $input['to_warehouse_id'], $input['product_id'], $input['quantity']]);
    }
    successResponse(['id' => $id, 'transfer_number' => $transferNum], 'Transfer completed');
}


// ─── SEARCH ───────────────────────────────────────────────────────────────────

function globalSearch($p) {
    $db = getDB();
    $q = $_GET['q'] ?? '';
    if (strlen($q) < 2) successResponse([]);
    $results = [];
    $s = "%$q%";
    $rows = $db->prepare("SELECT id, name, sku FROM products WHERE name LIKE ? OR sku LIKE ? LIMIT 5");
    $rows->execute([$s, $s]);
    foreach ($rows->fetch() as $r) $results[] = ['type' => 'product', 'id' => $r['id'], 'name' => $r['name'], 'subtitle' => $r['sku'], 'link' => "/products/{$r['id']}"];
    $rows = $db->prepare("SELECT id, name, phone FROM customers WHERE name LIKE ? OR phone LIKE ? LIMIT 5");
    $rows->execute([$s, $s]);
    foreach ($rows->fetchAll() as $r) $results[] = ['type' => 'customer', 'id' => $r['id'], 'name' => $r['name'], 'subtitle' => $r['phone'], 'link' => "/customers/{$r['id']}"];
    $rows = $db->prepare("SELECT id, name, phone FROM suppliers WHERE name LIKE ? OR phone LIKE ? LIMIT 5");
    $rows->execute([$s, $s]);
    foreach ($rows->fetchAll() as $r) $results[] = ['type' => 'supplier', 'id' => $r['id'], 'name' => $r['name'], 'subtitle' => $r['phone'], 'link' => "/suppliers/{$r['id']}"];
    $rows = $db->prepare("SELECT id, order_number, total FROM sale_orders WHERE order_number LIKE ? LIMIT 5");
    $rows->execute([$s]);
    foreach ($rows->fetchAll() as $r) $results[] = ['type' => 'sale_order', 'id' => $r['id'], 'name' => $r['order_number'], 'subtitle' => $r['total'], 'link' => "/sales/{$r['id']}"];
    $rows = $db->prepare("SELECT id, order_number, total FROM purchase_orders WHERE order_number LIKE ? LIMIT 5");
    $rows->execute([$s]);
    foreach ($rows->fetchAll() as $r) $results[] = ['type' => 'purchase_order', 'id' => $r['id'], 'name' => $r['order_number'], 'subtitle' => $r['total'], 'link' => "/purchases/{$r['id']}"];
    successResponse($results);
}


// ─── SETTINGS ─────────────────────────────────────────────────────────────────

function settingsList($p) {
    $db = getDB();
    $stmt = $db->query("SELECT * FROM system_settings ORDER BY `group`, `key`");
    successResponse($stmt->fetchAll());
}

function settingsGet($p) {
    $db = getDB();
    $stmt = $db->prepare("SELECT * FROM system_settings WHERE `key` = ?");
    $stmt->execute([$p['key']]);
    $item = $stmt->fetch();
    if (!$item) errorResponse('Setting not found', 404);
    successResponse($item);
}

function settingsUpdate($p) {
    global $input;
    $db = getDB();
    $db->prepare("UPDATE system_settings SET `value` = ? WHERE `key` = ?")->execute([$input['value'] ?? '', $p['key']]);
    successResponse(null, 'Setting updated');
}

function settingsBulkUpdate($p) {
    global $input;
    $db = getDB();
    $settings = $input['settings'] ?? $input;
    foreach ($settings as $key => $value) {
        $db->prepare("UPDATE system_settings SET `value` = ? WHERE `key` = ?")->execute([$value, $key]);
    }
    successResponse(null, 'Settings updated');
}

function settingsBackup($p) {
    $db = getDB();
    $backup = ['version' => '1.0', 'created_at' => date('c')];
    $backup['products'] = $db->query("SELECT name,sku,barcode,category_id,supplier_id,unit_price,cost_price,quantity_in_stock,unit FROM products")->fetchAll();
    $backup['customers'] = $db->query("SELECT name,phone,email,address FROM customers")->fetchAll();
    $backup['suppliers'] = $db->query("SELECT name,phone,email,address FROM suppliers")->fetchAll();
    $backup['settings'] = $db->query("SELECT `key`,`value`,`group` FROM system_settings")->fetchAll();
    header('Content-Disposition: attachment; filename=backup_' . date('Ymd_His') . '.json');
    echo json_encode($backup, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    exit;
}

function exportProducts($p) {
    $db = getDB();
    $data = $db->query("SELECT id,name,sku,barcode,category_id,supplier_id,unit_price,cost_price,quantity_in_stock,unit,is_active FROM products")->fetchAll();
    outputCsv($data, 'products');
}

function exportCustomers($p) {
    $db = getDB();
    $data = $db->query("SELECT id,name,phone,email FROM customers")->fetchAll();
    outputCsv($data, 'customers');
}

function exportSuppliers($p) {
    $db = getDB();
    $data = $db->query("SELECT id,name,phone,email FROM suppliers")->fetchAll();
    outputCsv($data, 'suppliers');
}

function outputCsv($data, $name) {
    header('Content-Type: text/csv; charset=utf-8');
    header("Content-Disposition: attachment; filename={$name}_export.csv");
    $output = fopen('php://output', 'w');
    if (!empty($data)) {
        fputcsv($output, array_keys($data[0]));
        foreach ($data as $row) fputcsv($output, $row);
    }
    fclose($output);
    exit;
}


// ─── REPORTS ──────────────────────────────────────────────────────────────────

function reportSalesExcel($p) {
    $db = getDB();
    $data = $db->query("SELECT order_number,customer_id,total,status,payment_method,created_at FROM sale_orders ORDER BY created_at DESC")->fetchAll();
    outputCsv($data, 'sales_report');
}

function reportSalesPdf($p) {
    $db = getDB();
    $data = $db->query("SELECT order_number,total,status,created_at FROM sale_orders ORDER BY created_at DESC")->fetchAll();
    header('Content-Type: application/json');
    echo json_encode(['success' => true, 'data' => $data, 'message' => 'PDF generation requires server-side library. Use Excel export instead.'], JSON_UNESCAPED_UNICODE);
    exit;
}

function reportPurchasesExcel($p) {
    $db = getDB();
    $data = $db->query("SELECT order_number,supplier_id,total,status,payment_method,created_at FROM purchase_orders ORDER BY created_at DESC")->fetchAll();
    outputCsv($data, 'purchases_report');
}

function reportInventoryExcel($p) {
    $db = getDB();
    $data = $db->query("SELECT name,sku,barcode,quantity_in_stock,minimum_stock_level,unit_price,cost_price FROM products ORDER BY name")->fetchAll();
    outputCsv($data, 'inventory_report');
}

function reportCustomersExcel($p) {
    $db = getDB();
    $data = $db->query("SELECT name,phone,email,current_balance FROM customers ORDER BY name")->fetchAll();
    outputCsv($data, 'customers_report');
}


// ─── EXTRACTIONS (AI) ─────────────────────────────────────────────────────────

function extractionsList($p) {
    $db = getDB();
    $stmt = $db->query("SELECT * FROM extractions ORDER BY created_at DESC LIMIT 50");
    successResponse($stmt->fetchAll());
}

function extractionsCreate($p) {
    global $input;
    $db = getDB();
    $id = newId();
    $db->prepare("INSERT INTO extractions (id,image_url,source,status,raw_text) VALUES (?,?,?,?,?)")
        ->execute([$id, $input['image_url'] ?? null, $input['source'] ?? 'api', 'pending', $input['raw_text'] ?? '']);
    successResponse(['id' => $id], 'Extraction created');
}

function extractionsGet($p) {
    $db = getDB();
    $stmt = $db->prepare("SELECT * FROM extractions WHERE id = ?");
    $stmt->execute([$p['id']]);
    $item = $stmt->fetch();
    if (!$item) errorResponse('Not found', 404);
    successResponse($item);
}

function extractionsReview($p) {
    global $input;
    $db = getDB();
    $user = requireAuth();
    $db->prepare("UPDATE extractions SET status=?, review_notes=?, reviewed_by=? WHERE id=?")
        ->execute([$input['status'], $input['review_notes'] ?? '', $user['sub'], $p['id']]);
    successResponse(null, 'Extraction reviewed');
}
