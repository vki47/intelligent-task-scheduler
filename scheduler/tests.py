from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from .core_classes import Scheduler


class StrategyOrderingTests(TestCase):
    def setUp(self):
        self.scheduler = Scheduler()
        now = timezone.now()
        self.t1 = self.scheduler.add_task(title='Old task', created_at=now - timedelta(hours=3), importance=4)
        self.t2 = self.scheduler.add_task(title='Mid task', created_at=now - timedelta(hours=2), importance=6)
        self.t3 = self.scheduler.add_task(title='New task', created_at=now - timedelta(hours=1), importance=9)

    def test_fifo_order(self):
        self.scheduler.set_strategy('fifo')
        ids = [t.id for t in self.scheduler.get_all_tasks()[:3]]
        self.assertEqual(ids[0], self.t1.id)

    def test_lifo_order(self):
        self.scheduler.set_strategy('lifo')
        ids = [t.id for t in self.scheduler.get_all_tasks()[:3]]
        self.assertEqual(ids[0], self.t3.id)

    def test_priority_order(self):
        self.scheduler.set_strategy('priority')
        ordered = self.scheduler.get_all_tasks()
        self.assertLessEqual(ordered[0].priority_score, ordered[-1].priority_score)
