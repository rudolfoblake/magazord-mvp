-- migration 001: Adição de índices de performance para consultas de BI

-- 1. Otimização para cálculos de GMV, Ticket Médio e YoY
-- Melhora drasticamente filtros que combinam data de criação e status do pedido.
CREATE INDEX IF NOT EXISTS idx_orders_created_at_status ON orders (created_at, status);

-- 2. Otimização para análise de cancelamentos e tendências temporais
-- Embora o índice acima cubra (created_at, status), ter um índice focado em created_at 
-- ajuda em consultas que não filtram por status (ex: volume total de pedidos).
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders (created_at);

-- 3. Otimização para JOINs analíticos (Top produtos/categorias)
-- Melhora a performance de junções entre pedidos e seus itens.
CREATE INDEX IF NOT EXISTS idx_order_item_order_product ON order_item (order_id, product_id);

-- JUSTIFICATIVA TÉCNICA:
-- idx_orders_created_at_status: Essencial para evitar Full Table Scans na tabela 'orders' em todas as ferramentas de vendas.
-- idx_order_item_order_product: Otimiza a busca de itens de pedidos específicos durante agregações de categorias.
