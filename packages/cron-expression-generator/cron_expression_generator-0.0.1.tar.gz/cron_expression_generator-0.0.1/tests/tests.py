import unittest
from croniter import croniter

from src.cron_expression_generator.generator import CronExpressionGenerator


class TestCronExpressionGenerator(unittest.TestCase):
    def test_valid_cron_expressions(self):
        expression = (
            CronExpressionGenerator().seconds(5).minutes(5, every=True).cron_expression
        )
        self.assertTrue(croniter.is_valid(expression))
        self.assertEqual(expression, "5 */5 * * * *")

    def test_invalid_cron_expressions(self):
        with self.assertRaises(ValueError):
            CronExpressionGenerator().seconds(60).cron_expression
