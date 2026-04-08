import time
import logging
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import (
    Progress, SpinnerColumn, TextColumn, BarColumn, 
    TaskProgressColumn, DownloadColumn, TransferSpeedColumn, 
    TimeRemainingColumn, TimeElapsedColumn
)

# 1. Setup shared console
console = Console()

# 2. Configure logging to use the same console
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    handlers=[RichHandler(console=console)]
)
logger = logging.getLogger("rich")

def worker_task(progress, task_id):
    """Function executed by threads."""
    logger.info(f"Starting worker update for task {task_id}")
    for _ in range(10):
        logger.info(f"Migrating record {_}")
        time.sleep(0.5)  # Simulate slower work to see the ETA
        progress.update(task_id, advance=1)

def main():
    # 3. Define custom columns including TimeRemainingColumn (ETA)
    progress_columns = [
        SpinnerColumn(),            # Animated spinner (e.g., dots)
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),  # 'None' makes it expand to fill space
        TaskProgressColumn(),
        # DownloadColumn(),           # Shows "1.2/5.0 GB"
        # TransferSpeedColumn(),      # Shows "2.5 MB/s"
        TextColumn("• ETA:"),
        TimeRemainingColumn(),  # Shows estimated time remaining
        TextColumn("• Elapsed:"),
        TimeElapsedColumn(),        # Shows total time since start
    ]

    with Progress(*progress_columns, console=console) as progress:
        # Total set to 50 (5 tasks * 10 steps each)
        main_task = progress.add_task("[cyan]Processing...", total=50) 
        with ThreadPoolExecutor(max_workers=4) as executor:
            for i in range(5):
                executor.submit(worker_task, progress, main_task)

if __name__ == "__main__":
    main()
