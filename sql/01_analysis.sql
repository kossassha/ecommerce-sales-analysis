-- 1. Общее количество заказов

SELECT
    COUNT(*) AS orders_count
FROM orders;


-- 2. Количество уникальных клиентов

SELECT
    COUNT(DISTINCT customer_id) AS unique_customers
FROM orders;


-- 3. Заказы по статусу

SELECT
    status,
    COUNT(*) AS orders_count
FROM orders
GROUP BY status
ORDER BY orders_count DESC;


-- 4. Заказы по каналам продаж

SELECT
    channel,
    COUNT(*) AS orders_count
FROM orders
GROUP BY channel
ORDER BY orders_count DESC;


-- 5. Количество товаров

SELECT
    COUNT(*) AS products_count
FROM products;


-- 6. Количество клиентов в таблице customers

SELECT
    COUNT(*) AS customers_count
FROM customers;