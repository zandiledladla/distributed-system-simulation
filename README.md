# distributed-system-simulation

# Distributed System Simulation (Beginner Project)

This project simulates a distributed task processing system using Python threads and queues. It randomly generates tasks (email sending, data backup, etc.) and simulates how these tasks are handled by worker threads — including automatic retries for failures.

This is a **student-level simulation project** inspired by real-world distributed systems like those used in AWS and other large-scale tech environments.

---

## 🧰 Technologies Used

- Python 3
- `threading`
- `queue`
- `random`
- `time`

---

## What It Does

- Simulates **real-time task generation** (like a server receiving jobs)
- Uses **consumer threads** to process each task
- Randomly **fails tasks**, and retries them up to 3 times
- Prints the status of each task and retry attempt in the terminal
- Automatically shuts down after 30 seconds (for demo purposes)

---

## How to Run It

1. Make sure you have Python 3 installed
2. Clone this repo or download the `.py` file
3. Open terminal and navigate to the file location
4. Run:

```bash
python distributed_simulation.py
