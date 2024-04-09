from dataclasses import dataclass, field


@dataclass
class ComparisonTask:
    batch_id: int
    source_key_vals: list[dict]
    different: list[dict]


tasks = [ComparisonTask(3, [], []), ComparisonTask(1, [], []), ComparisonTask(2, [], [])]


tasks.sort(key=lambda task: task.batch_id)

print(tasks)
