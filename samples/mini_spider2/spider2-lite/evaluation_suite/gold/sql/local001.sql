SELECT c.first_name || ' ' || c.last_name AS full_name FROM customers AS c JOIN orders AS o ON c.customer_id = o.customer_id GROUP BY c.customer_id ORDER BY COUNT(*) DESC, full_name ASC LIMIT 1;
