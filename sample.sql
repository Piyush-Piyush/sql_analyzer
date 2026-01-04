SELECT o.order_id,
    o.order_date,
    c.customer_name,
    SUM(i.quantity * i.price) AS total_amount
FROM orders o
    INNER JOIN customers c ON o.customer_id = c.customer_id
    LEFT JOIN order_items i ON o.order_id = i.order_id
WHERE o.order_date >= '2023-01-01'
    AND c.segment = 'ENTERPRISE'
GROUP BY 1,
    2,
    3
HAVING SUM(i.quantity * i.price) > 500
ORDER BY total_amount DESC;