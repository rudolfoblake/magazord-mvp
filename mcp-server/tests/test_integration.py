import unittest
import os
import decimal
import datetime
from sqlalchemy import text
from src.database.connection import db_engine
from src.repositories.orders_repository import OrdersRepository

class TestIntegration(unittest.TestCase):
    """
    Testes de integração básicos para validar a conectividade e sanidade das queries.
    Nota: Estes testes assumem que o banco de dados de desenvolvimento está acessível
    e contém dados para validação mínima.
    """
    
    def setUp(self):
        self.repo = OrdersRepository()

    def test_database_connection(self):
        """Valida se o engine consegue executar uma query simples."""
        with db_engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            self.assertEqual(result, 1)

    def test_repository_get_gmv_raw(self):
        """Valida se o repositório retorna um valor numérico (mesmo que 0)."""
        start = datetime.datetime(2000, 1, 1)
        end = datetime.datetime(2100, 1, 1)
        gmv = self.repo.get_gmv(start, end)
        self.assertIsInstance(gmv, (int, float, decimal.Decimal))

if __name__ == "__main__":
    unittest.main()
