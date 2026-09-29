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
-- 7. Выручка по месяцам

SELECT
    substr(o.order_date, 1, 7) AS month,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
WHERE o.status = 'Completed'
GROUP BY month
ORDER BY month;


-- 8. Выручка по категориям

SELECT
    p.category,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
FROM order_items oi
JOIN orders o
    ON oi.order_id = o.order_id
JOIN products p
    ON oi.product_id = p.product_id
WHERE o.status = 'Completed'
GROUP BY p.category
ORDER BY revenue DESC;


-- 9. Средний чек

SELECT
    ROUND(AVG(order_total), 2) AS average_order_value
FROM (
    SELECT
        o.order_id,
        SUM(oi.quantity * oi.unit_price) AS order_total
    FROM orders o
    JOIN order_items oi
        ON o.order_id = oi.order_id
    WHERE o.status = 'Completed'
    GROUP BY o.order_id
);


-- 10. Топ-10 клиентов по выручке

SELECT
    o.customer_id,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
WHERE o.status = 'Completed'
GROUP BY o.customer_id
ORDER BY revenue DESC
LIMIT 10;


-- 11. Продажи по каналам

SELECT
    o.channel,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
WHERE o.status = 'Completed'
GROUP BY o.channel
ORDER BY revenue DESC;


-- 12. Возвраты и отмены

SELECT
    status,
    COUNT(DISTINCT order_id) AS orders
FROM orders
GROUP BY status
ORDER BY orders DESC;