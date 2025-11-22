select *
from orders
where order_date > '2022-01-01'
    and order_date < '2022-02-01'
    and customer_id = '12345'
    and order_id = '12345'
group by order_id,
    order_date,
    customer_id;