-- Complex E-commerce Customer Segmentation and Revenue Analysis Query
-- This query performs multi-dimensional analysis on customer behavior, product performance,
-- and revenue trends with advanced segmentation logic
WITH customer_metrics AS (
    -- Calculate customer-level metrics including lifetime value and purchase patterns
    SELECT c.customer_id,
        c.customer_name,
        c.registration_date,
        c.country,
        c.segment,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(o.total_amount) AS lifetime_value,
        AVG(o.total_amount) AS avg_order_value,
        MIN(o.order_date) AS first_order_date,
        MAX(o.order_date) AS last_order_date,
        DATEDIFF(day, MIN(o.order_date), MAX(o.order_date)) AS customer_lifetime_days,
        COUNT(
            DISTINCT EXTRACT(
                YEAR
                FROM o.order_date
            ) || '-' || EXTRACT(
                MONTH
                FROM o.order_date
            )
        ) AS active_months
    FROM customers c
        INNER JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.order_status IN ('completed', 'shipped')
        AND o.order_date >= DATEADD(year, -2, CURRENT_DATE)
    GROUP BY c.customer_id,
        c.customer_name,
        c.registration_date,
        c.country,
        c.segment
),
product_performance AS (
    -- Analyze product performance with category-level aggregations
    SELECT p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        COUNT(DISTINCT oi.order_id) AS times_ordered,
        SUM(oi.quantity) AS total_quantity_sold,
        SUM(oi.quantity * oi.unit_price) AS total_revenue,
        AVG(oi.quantity * oi.unit_price) AS avg_revenue_per_order,
        SUM(oi.quantity * (oi.unit_price - p.cost_price)) AS total_profit,
        CASE
            WHEN SUM(oi.quantity * oi.unit_price) = 0 THEN 0
            ELSE (
                SUM(oi.quantity * (oi.unit_price - p.cost_price)) / SUM(oi.quantity * oi.unit_price)
            ) * 100
        END AS profit_margin_pct
    FROM products p
        INNER JOIN order_items oi ON p.product_id = oi.product_id
        INNER JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status IN ('completed', 'shipped')
        AND o.order_date >= DATEADD(year, -2, CURRENT_DATE)
    GROUP BY p.product_id,
        p.product_name,
        p.category,
        p.subcategory,
        p.cost_price
),
customer_product_affinity AS (
    -- Calculate product category affinity for each customer
    SELECT o.customer_id,
        p.category,
        COUNT(DISTINCT o.order_id) AS category_orders,
        SUM(oi.quantity * oi.unit_price) AS category_spend,
        ROW_NUMBER() OVER (
            PARTITION BY o.customer_id
            ORDER BY SUM(oi.quantity * oi.unit_price) DESC
        ) AS category_rank
    FROM orders o
        INNER JOIN order_items oi ON o.order_id = oi.order_id
        INNER JOIN products p ON oi.product_id = p.product_id
    WHERE o.order_status IN ('completed', 'shipped')
        AND o.order_date >= DATEADD(year, -1, CURRENT_DATE)
    GROUP BY o.customer_id,
        p.category
),
rfm_analysis AS (
    -- Recency, Frequency, Monetary analysis for customer segmentation
    SELECT customer_id,
        DATEDIFF(day, MAX(order_date), CURRENT_DATE) AS recency_days,
        COUNT(DISTINCT order_id) AS frequency,
        SUM(total_amount) AS monetary,
        NTILE(5) OVER (
            ORDER BY DATEDIFF(day, MAX(order_date), CURRENT_DATE) DESC
        ) AS recency_score,
        NTILE(5) OVER (
            ORDER BY COUNT(DISTINCT order_id) ASC
        ) AS frequency_score,
        NTILE(5) OVER (
            ORDER BY SUM(total_amount) ASC
        ) AS monetary_score
    FROM orders
    WHERE order_status IN ('completed', 'shipped')
        AND order_date >= DATEADD(year, -1, CURRENT_DATE)
    GROUP BY customer_id
),
cohort_analysis AS (
    -- Monthly cohort analysis with retention metrics
    SELECT DATE_TRUNC('month', cm.first_order_date) AS cohort_month,
        DATE_TRUNC('month', o.order_date) AS order_month,
        DATEDIFF(
            month,
            DATE_TRUNC('month', cm.first_order_date),
            DATE_TRUNC('month', o.order_date)
        ) AS month_number,
        COUNT(DISTINCT o.customer_id) AS active_customers,
        SUM(o.total_amount) AS cohort_revenue
    FROM customer_metrics cm
        INNER JOIN orders o ON cm.customer_id = o.customer_id
    WHERE o.order_status IN ('completed', 'shipped')
    GROUP BY cohort_month,
        order_month,
        month_number
),
revenue_trends AS (
    -- Calculate moving averages and growth rates
    SELECT DATE_TRUNC('month', order_date) AS month,
        SUM(total_amount) AS monthly_revenue,
        COUNT(DISTINCT order_id) AS monthly_orders,
        COUNT(DISTINCT customer_id) AS monthly_customers,
        AVG(SUM(total_amount)) OVER (
            ORDER BY DATE_TRUNC('month', order_date) ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS three_month_avg_revenue,
        LAG(SUM(total_amount), 1) OVER (
            ORDER BY DATE_TRUNC('month', order_date)
        ) AS prev_month_revenue,
        CASE
            WHEN LAG(SUM(total_amount), 1) OVER (
                ORDER BY DATE_TRUNC('month', order_date)
            ) = 0 THEN NULL
            ELSE (
                (
                    SUM(total_amount) - LAG(SUM(total_amount), 1) OVER (
                        ORDER BY DATE_TRUNC('month', order_date)
                    )
                ) / LAG(SUM(total_amount), 1) OVER (
                    ORDER BY DATE_TRUNC('month', order_date)
                )
            ) * 100
        END AS month_over_month_growth_pct
    FROM orders
    WHERE order_status IN ('completed', 'shipped')
        AND order_date >= DATEADD(year, -2, CURRENT_DATE)
    GROUP BY DATE_TRUNC('month', order_date)
) -- Main query combining all CTEs with complex business logic
SELECT cm.customer_id,
    cm.customer_name,
    cm.country,
    cm.segment,
    cm.total_orders,
    cm.lifetime_value,
    cm.avg_order_value,
    cm.customer_lifetime_days,
    -- RFM Segmentation
    rfm.recency_days,
    rfm.frequency,
    rfm.monetary,
    rfm.recency_score + rfm.frequency_score + rfm.monetary_score AS rfm_total_score,
    CASE
        WHEN rfm.recency_score + rfm.frequency_score + rfm.monetary_score >= 13 THEN 'Champion'
        WHEN rfm.recency_score + rfm.frequency_score + rfm.monetary_score >= 10 THEN 'Loyal'
        WHEN rfm.recency_score >= 4
        AND rfm.frequency_score <= 2 THEN 'New Customer'
        WHEN rfm.recency_score <= 2
        AND rfm.frequency_score >= 4 THEN 'At Risk'
        WHEN rfm.recency_score <= 2
        AND rfm.frequency_score <= 2 THEN 'Lost'
        ELSE 'Regular'
    END AS customer_segment,
    -- Top product category for each customer
    cpa.category AS preferred_category,
    cpa.category_spend AS preferred_category_spend,
    -- Calculate customer percentile ranks
    PERCENT_RANK() OVER (
        ORDER BY cm.lifetime_value
    ) AS ltv_percentile,
    PERCENT_RANK() OVER (
        ORDER BY cm.total_orders
    ) AS order_frequency_percentile,
    -- Cohort information
    ca.cohort_month,
    ca.month_number AS months_since_first_order,
    ca.cohort_revenue,
    -- Product insights
    pp.product_name AS top_purchased_product,
    pp.total_revenue AS top_product_revenue,
    pp.profit_margin_pct AS top_product_margin,
    -- Revenue trends
    rt.monthly_revenue AS current_month_revenue,
    rt.three_month_avg_revenue,
    rt.month_over_month_growth_pct,
    -- Advanced calculations
    CASE
        WHEN cm.customer_lifetime_days > 0 THEN cm.lifetime_value / NULLIF(cm.customer_lifetime_days, 0) * 30
        ELSE 0
    END AS avg_monthly_value,
    CASE
        WHEN rfm.recency_days <= 30
        AND cm.lifetime_value > (
            SELECT AVG(lifetime_value)
            FROM customer_metrics
        ) THEN 1
        ELSE 0
    END AS is_high_value_active,
    ROW_NUMBER() OVER (
        PARTITION BY cm.country
        ORDER BY cm.lifetime_value DESC
    ) AS country_rank
FROM customer_metrics cm
    LEFT JOIN rfm_analysis rfm ON cm.customer_id = rfm.customer_id
    LEFT JOIN customer_product_affinity cpa ON cm.customer_id = cpa.customer_id
    AND cpa.category_rank = 1
    LEFT JOIN cohort_analysis ca ON DATE_TRUNC('month', cm.first_order_date) = ca.cohort_month
    AND DATE_TRUNC('month', cm.last_order_date) = ca.order_month
    LEFT JOIN product_performance pp ON pp.product_id = (
        SELECT oi.product_id
        FROM order_items oi
            INNER JOIN orders o ON oi.order_id = o.order_id
        WHERE o.customer_id = cm.customer_id
            AND o.order_status IN ('completed', 'shipped')
        GROUP BY oi.product_id
        ORDER BY SUM(oi.quantity * oi.unit_price) DESC
        LIMIT 1
    )
    LEFT JOIN revenue_trends rt ON DATE_TRUNC('month', cm.last_order_date) = rt.month
WHERE cm.lifetime_value > 0
    AND rfm.recency_days IS NOT NULL
ORDER BY CASE
        WHEN rfm.recency_score + rfm.frequency_score + rfm.monetary_score >= 13 THEN 1
        WHEN rfm.recency_score + rfm.frequency_score + rfm.monetary_score >= 10 THEN 2
        ELSE 3
    END,
    cm.lifetime_value DESC
LIMIT 10000;