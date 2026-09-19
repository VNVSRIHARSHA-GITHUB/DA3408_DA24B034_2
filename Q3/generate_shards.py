import random
import csv
import os

num_shards = 8
rows_per_shard = 50

names = [
    "Harsha",
    "Krish",
    "Rishikesh",
    "Ramana",
    "Veda",
    "Navadeep",
    "Jagadeesh",
    "Sidhartha",
    "Mithilesh"
]

domains = ["example.com", "mail.com", "test.org", "company.co"]

output_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "shards"
)

os.makedirs(output_dir, exist_ok=True)

invalid_counts = [3, 5, 8, 7, 4, 6, 9, 5]

summary = {}

for shard_idx in range(num_shards):
    random.seed(42 + shard_idx)

    rows = []
    n_invalid = invalid_counts[shard_idx]

    invalid_positions = set(
        random.sample(range(rows_per_shard), n_invalid)
    )

    for row_idx in range(rows_per_shard):
        user_id = f"u{shard_idx}_{row_idx:03d}"
        name = random.choice(names)
        domain = random.choice(domains)
        email = f"{name.lower()}{row_idx}@{domain}"
        signup_date = (
            f"2026-0{random.randint(1, 9)}-"
            f"{random.randint(10, 28):02d}"
        )

        if row_idx in invalid_positions:
            if row_idx % 2 == 0:
                email = email.replace("@", "")
            else:
                name = ""

        rows.append([user_id, name, email, signup_date])

    shard_path = os.path.join(
        output_dir,
        f"shard_{shard_idx}.csv"
    )

    with open(shard_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "user_id",
            "name",
            "email",
            "signup_date"
        ])
        writer.writerows(rows)

    summary[shard_idx] = n_invalid

    print(
        f"Wrote {shard_path}: "
        f"{rows_per_shard} rows, "
        f"{n_invalid}  invalid"
    )

print("\nExpected invalid-row counts per shard:")
print(summary)