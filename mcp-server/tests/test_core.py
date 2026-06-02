import unittest
from datetime import datetime
from src.services.period_service import PeriodService
from src.business_rules.revenue_rules import is_revenue_valid
from src.services.analytics_service import calculate_variation

class TestBusinessRules(unittest.TestCase):
    def test_revenue_valid_status(self):
        self.assertTrue(is_revenue_valid("delivered"))
        self.assertTrue(is_revenue_valid("shipped"))
        self.assertTrue(is_revenue_valid("processing"))
        self.assertFalse(is_revenue_valid("cancelled"))
        self.assertFalse(is_revenue_valid("pending"))

    def test_variation_calculation(self):
        # Increase
        res = calculate_variation(120, 100)
        self.assertEqual(res["variation_percentage"], 20.0)
        self.assertEqual(res["direction"], "increase")
        
        # Decrease
        res = calculate_variation(80, 100)
        self.assertEqual(res["variation_percentage"], -20.0)
        self.assertEqual(res["direction"], "decrease")
        
        # Zero base
        res = calculate_variation(100, 0)
        self.assertIsNone(res["variation_percentage"])
        self.assertEqual(res["direction"], "undefined")

    def test_period_resolution(self):
        service = PeriodService()
        start, end, label = service.resolve_period("last_month")
        self.assertEqual(label, "last_month")
        self.assertTrue(start < end)

    def test_period_comparison_last_month(self):
        service = PeriodService()
        start = datetime(2026, 5, 1, 0, 0, 0)
        end = datetime(2026, 5, 31, 23, 59, 59)
        comp_start, comp_end, comp_label = service.get_comparison_period("last_month", start, end)
        self.assertEqual(comp_label, "month_before_last")
        self.assertEqual(comp_start, datetime(2026, 4, 1, 0, 0, 0))
        self.assertEqual(comp_end, datetime(2026, 4, 30, 23, 59, 59))

    def test_period_comparison_current_month_to_date(self):
        service = PeriodService()
        start = datetime(2026, 6, 1, 0, 0, 0)
        end = datetime(2026, 6, 10, 23, 59, 59)
        comp_start, comp_end, comp_label = service.get_comparison_period("current_month", start, end)
        self.assertEqual(comp_label, "previous_month_to_date")
        self.assertEqual(comp_start, datetime(2026, 5, 1, 0, 0, 0))
        self.assertEqual(comp_end, datetime(2026, 5, 10, 23, 59, 59))

    def test_period_resolution_today(self):
        service = PeriodService()
        start, end, label = service.resolve_period("today")
        self.assertEqual(label, "today")
        self.assertEqual(start.hour, 0)
        self.assertEqual(end.hour, 23)

    def test_period_resolution_yesterday(self):
        service = PeriodService()
        start, end, label = service.resolve_period("yesterday")
        self.assertEqual(label, "yesterday")
        self.assertTrue(start < end)

    def test_period_resolution_last_quarter(self):
        service = PeriodService()
        start, end, label = service.resolve_period("last_quarter")
        self.assertEqual(label, "last_quarter")
        self.assertTrue(start < end)

    def test_period_resolution_last_year(self):
        service = PeriodService()
        start, end, label = service.resolve_period("last_year")
        self.assertEqual(label, "last_year")
        self.assertEqual(start.month, 1)
        self.assertEqual(start.day, 1)
        self.assertEqual(end.month, 12)
        self.assertEqual(end.day, 31)

    def test_invalid_period(self):
        service = PeriodService()
        with self.assertRaises(ValueError):
            service.resolve_period("invalid_period_name")

if __name__ == "__main__":
    unittest.main()
