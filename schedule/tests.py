from datetime import time
from django.test import TestCase

from schedule.models import TimeOfBell
from schedule.services import ScheduleBells


class ScheduleBellsTest(TestCase):
    def setUp(self):
        # создаём параметры звонков
        self.params = TimeOfBell.objects.create(
            start_time=time(8, 45),
            lesson=90,
            lesson_saturday=70,
            use_curator_hour=True,
            curator_hour=40,
            lunch_break=30,
            lunch_break_monday=35,
            lunch_break_saturday=25,
            first_half=40,
            second_half=30,
            break_after_1=10,
            break_after_2=10,
            break_after_3=10,
            break_after_4=10,
            break_after_5=5,
        )

    def test_schedule_without_curator(self):
        schedule_bells = ScheduleBells()
        expected = [
            [
                "08:45-10:15",
                "10:25-11:10, 11:40-12:25",
                "12:35-14:05",
                "14:15-15:45",
                "15:55-17:25",
                "17:30-19:00",
            ],
            [
                "08:45-10:15",
                "10:25-11:55",
                "12:35-14:05",
                "14:15-15:45",
                "15:55-17:25",
                "17:30-19:00",
            ],
        ]
        self.assertEqual(schedule_bells.bells, expected)

    def test_schedule_with_curator(self):
        schedule_bells = ScheduleBells()
        expected = [
            [
                "08:45-10:15",
                "11:05-11:50, 12:25-13:10",
                "13:20-14:50",
                "15:00-16:30",
                "16:40-18:10",
                "18:15-19:45",
            ],
            [
                "08:45-10:15",
                "11:05-12:35",
                "13:20-14:50",
                "15:00-16:30",
                "16:40-18:10",
                "18:15-19:45",
            ],
        ]
        self.assertEqual(schedule_bells.bells_on_monday, expected)

    def test_schedule_on_saturday(self):
        schedule_bells = ScheduleBells()
        expected = [
            [
                "08:45-09:55",
                "10:05-10:45, 11:10-11:40",
                "11:50-13:00",
                "13:10-14:20",
                "14:30-15:40",
                "15:45-16:55",
            ],
            [
                "08:45-09:55",
                "10:05-11:15",
                "11:50-13:00",
                "13:10-14:20",
                "14:30-15:40",
                "15:45-16:55",
            ],
        ]
        self.assertEqual(schedule_bells.bells_on_saturday, expected)
        
