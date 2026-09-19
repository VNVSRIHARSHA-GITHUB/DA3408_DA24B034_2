import os
import csv
import json
import re
import socket

shard_dir = os.environ.get("SHARD_DIR", "/shards")
email_pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_row(row):
    name = row.get("name", "").strip()
    email = row.get("email", "").strip()

    if not name or not email:
        return False

    if not email_pattern.match(email):
        return False

    return True


def main():
    completion_index = int(
        os.environ.get("JOB_COMPLETION_INDEX", "0")
    )

    pod_name = os.environ.get(
        "POD_NAME",
        socket.gethostname()
    )

    node_name = os.environ.get(
        "NODE_NAME",
        "unknown"
    )

    shard_file = f"shard_{completion_index}.csv"
    shard_path = os.path.join(shard_dir, shard_file)

    total_rows = 0
    invalid_rows = 0

    with open(shard_path, newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            total_rows += 1

            if not is_valid_row(row):
                invalid_rows += 1

    result = {
        "completion_index": completion_index,
        "shard_file": shard_file,
        "total_rows": total_rows,
        "invalid_rows": invalid_rows,
        "pod_name": pod_name,
        "node_name": node_name
    }

    print("RESULT_JSON:" + json.dumps(result))


if __name__ == "__main__":
    main()