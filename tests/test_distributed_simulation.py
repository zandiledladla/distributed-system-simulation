import random
import unittest

from distributed_simulation import Task, TaskProcessor


class TaskProcessorTests(unittest.TestCase):
    def test_successful_task_completes_without_retry(self):
        processor = TaskProcessor(process_delay=0)
        task = Task("email")
        result = processor.handle_task(task, processor=lambda _: True)
        self.assertEqual(result, "completed")
        self.assertEqual(task.retries, 0)
        self.assertTrue(processor.tasks.empty())

    def test_failed_task_is_requeued_before_retry_limit(self):
        processor = TaskProcessor(max_retries=3, process_delay=0)
        task = Task("data_backup")
        result = processor.handle_task(task, processor=lambda _: False)
        self.assertEqual(result, "retried")
        self.assertEqual(task.retries, 1)
        self.assertIs(processor.tasks.get_nowait(), task)

    def test_task_permanently_fails_at_retry_limit(self):
        processor = TaskProcessor(max_retries=2, process_delay=0)
        task = Task("report_gen", retries=1)
        result = processor.handle_task(task, processor=lambda _: False)
        self.assertEqual(result, "failed")
        self.assertEqual(task.retries, 2)
        self.assertTrue(processor.tasks.empty())

    def test_invalid_configuration_is_rejected(self):
        for arguments in (
            {"workers": 0},
            {"max_retries": 0},
            {"failure_rate": -0.1},
            {"failure_rate": 1.1},
        ):
            with self.subTest(arguments=arguments):
                with self.assertRaises(ValueError):
                    TaskProcessor(**arguments)

    def test_seeded_random_source_makes_processing_repeatable(self):
        first = TaskProcessor(process_delay=0, random_source=random.Random(7))
        second = TaskProcessor(process_delay=0, random_source=random.Random(7))
        self.assertEqual(
            first.process_task(Task("email")),
            second.process_task(Task("email")),
        )


if __name__ == "__main__":
    unittest.main()
