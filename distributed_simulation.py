"""Threaded producer-consumer task processing simulation."""

from __future__ import annotations

import argparse
import logging
import queue
import random
import threading
import time
from dataclasses import dataclass
from typing import Callable


LOGGER = logging.getLogger("task_simulation")
TASK_NAMES = ("email", "data_backup", "report_gen", "image_resize", "log_rotation")


@dataclass
class Task:
    """A unit of work and its current retry count."""

    name: str
    retries: int = 0


class TaskProcessor:
    """Coordinate task producers and consumers through a thread-safe queue."""

    def __init__(
        self,
        workers: int = 3,
        max_retries: int = 3,
        failure_rate: float = 0.5,
        process_delay: float = 0.5,
        random_source: random.Random | None = None,
    ) -> None:
        if workers < 1:
            raise ValueError("workers must be at least 1")
        if max_retries < 1:
            raise ValueError("max_retries must be at least 1")
        if not 0 <= failure_rate <= 1:
            raise ValueError("failure_rate must be between 0 and 1")

        self.workers = workers
        self.max_retries = max_retries
        self.failure_rate = failure_rate
        self.process_delay = process_delay
        self.random = random_source or random.Random()
        self.tasks: queue.Queue[Task] = queue.Queue()
        self.stop_event = threading.Event()
        self._threads: list[threading.Thread] = []

    def process_task(self, task: Task) -> bool:
        """Simulate work and return whether the attempt succeeded."""
        LOGGER.info(
            "task_attempt",
            extra={"task_name": task.name, "attempt": task.retries + 1},
        )
        time.sleep(self.process_delay)
        return self.random.random() >= self.failure_rate

    def handle_task(self, task: Task, processor: Callable[[Task], bool] | None = None) -> str:
        """Process once and either complete, retry, or permanently fail the task."""
        succeeded = (processor or self.process_task)(task)
        if succeeded:
            LOGGER.info("task_completed", extra={"task_name": task.name})
            return "completed"

        task.retries += 1
        if task.retries < self.max_retries:
            self.tasks.put(task)
            LOGGER.warning(
                "task_retry_scheduled",
                extra={"task_name": task.name, "retry": task.retries},
            )
            return "retried"

        LOGGER.error(
            "task_permanently_failed",
            extra={"task_name": task.name, "attempts": self.max_retries},
        )
        return "failed"

    def producer(self, interval: float = 1.0) -> None:
        """Generate tasks until shutdown is requested."""
        while not self.stop_event.is_set():
            task = Task(self.random.choice(TASK_NAMES))
            self.tasks.put(task)
            LOGGER.info("task_created", extra={"task_name": task.name})
            self.stop_event.wait(interval)

    def consumer(self) -> None:
        """Consume queued tasks while the simulation is active."""
        while not self.stop_event.is_set() or not self.tasks.empty():
            try:
                task = self.tasks.get(timeout=0.2)
            except queue.Empty:
                continue
            try:
                self.handle_task(task)
            finally:
                self.tasks.task_done()

    def run(self, duration: float = 30.0, production_interval: float = 1.0) -> None:
        """Start the simulation, run for a fixed duration, then shut down cleanly."""
        producer = threading.Thread(
            target=self.producer,
            args=(production_interval,),
            name="producer",
            daemon=True,
        )
        consumers = [
            threading.Thread(target=self.consumer, name=f"worker-{number}", daemon=True)
            for number in range(1, self.workers + 1)
        ]
        self._threads = [producer, *consumers]

        LOGGER.info(
            "simulation_started",
            extra={"workers": self.workers, "duration_seconds": duration},
        )
        for thread in self._threads:
            thread.start()

        self.stop_event.wait(duration)
        self.stop_event.set()
        producer.join(timeout=2)
        self.tasks.join()
        for consumer in consumers:
            consumer.join(timeout=2)
        LOGGER.info("simulation_stopped")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--duration", type=float, default=30.0)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--failure-rate", type=float, default=0.5)
    parser.add_argument("--production-interval", type=float, default=1.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(threadName)s %(message)s",
    )
    TaskProcessor(
        workers=args.workers,
        max_retries=args.max_retries,
        failure_rate=args.failure_rate,
    ).run(duration=args.duration, production_interval=args.production_interval)


if __name__ == "__main__":
    main()
