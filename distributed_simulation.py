import threading
import queue
import random
import time

# Create a queue where tasks will be added and consumed
task_queue = queue.Queue()

# Set the maximum number of retries allowed for a task if it fails
MAX_RETRIES = 3

# A list of fake tasks to simulate work
TASKS = ["email", "data_backup", "report_gen", "image_resize", "log_rotation"]

# Define a Task class to represent each unit of work
class Task:
    def __init__(self, name):
        self.name = name            # Task name (e.g., "email")
        self.retries = 0            # How many times this task has failed so far

    def process(self):
        """
        Simulates doing the task with a 50% chance of failure.
        Returns True if successful, False otherwise.
        """
        print(f"Processing task: {self.name} | Attempt: {self.retries + 1}")
        success = random.choice([True, False])  # Randomly succeed or fail
        time.sleep(0.5)  # Simulate time taken to process
        return success

# The producer keeps creating tasks and adds them to the queue
def producer():
    while True:
        task_name = random.choice(TASKS)   # Pick a random task from the list
        task = Task(task_name)             # Create a new Task object
        print(f"[Producer] Created task: {task.name}")
        task_queue.put(task)               # Add the task to the queue
        time.sleep(random.uniform(0.5, 1.5))  # Random delay between tasks

# The consumer takes tasks from the queue and tries to process them
def consumer():
    while True:
        task = task_queue.get()  # Get a task from the queue (waits if empty)

        if task:
            success = task.process()  # Try to process the task

            if success:
                print(f"[Consumer] Task '{task.name}' completed ✅\n")
            else:
                task.retries += 1  # Increase the retry count

                if task.retries < MAX_RETRIES:
                    # If the task hasn't reached the retry limit, try again later
                    print(f"[Consumer] Task '{task.name}' failed ❌ - Retrying ({task.retries})\n")
                    task_queue.put(task)
                else:
                    # Task failed too many times — give up
                    print(f"[Consumer] Task '{task.name}' permanently failed after {MAX_RETRIES} retries ❌\n")

        task_queue.task_done()  # Mark this task as "done" in the queue

# This part runs when we execute the script directly
if __name__ == "__main__":
    # Create one producer thread and one consumer thread
    producer_thread = threading.Thread(target=producer, daemon=True)
    consumer_thread = threading.Thread(target=consumer, daemon=True)

    # Start both threads
    producer_thread.start()
    consumer_thread.start()

    # Let the simulation run for 30 seconds, then exit
    time.sleep(30)
    print("\n[System] Shutting down after 30 seconds.")
