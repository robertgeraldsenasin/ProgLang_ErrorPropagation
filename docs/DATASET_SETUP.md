# Dataset setup

This repo does **not** bundle the full official Spider2 dataset.

## Official source

Clone:
`https://github.com/xlang-ai/Spider2`

## Needed path for this project

We use only the **Spider2-Lite SQLite/local subset**.

Required files and folders:

```text
Spider2/
└── spider2-lite/
    ├── spider2-lite.jsonl
    ├── evaluation_suite/
    │   └── gold/
    │       ├── exec_result/
    │       └── sql/
    └── resource/
        └── databases/
            └── spider2-localdb/
                ├── sqlite-sakila.sqlite
                ├── ...
```

## Official local DB note

The official repo states that you should download the local database bundle, unzip it,
and place the `.sqlite` files into:

`spider2-lite/resource/databases/spider2-localdb`

## Validation

Run:

```bash
python scripts/02_validate_spider2_layout.py --spider2-root ./Spider2
```

## Notes

- The official repo says Spider2-Lite contains 547 tasks total across BigQuery, Snowflake, and SQLite.
- The SQLite portion contains 135 tasks.
- This repo is intentionally scoped to the local SQLite part to keep execution reproducible and inexpensive.
