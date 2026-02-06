# PA Bench SDK

This repository hosts a minimal SDK (plus CLI) for loading the new
PA Bench scenarios directly into the Vibrant Labs worlds and running the
verifier that ships with each scenario.


## Installing

Use the supplied `pyproject.toml` when installing:

```bash
python -m pip install -e .
```

This exposes the CLI entry point `pa-bench`, which delegates to the
SDK's `pa_bench_sdk.cli` module.

## Loading scenarios

Each scenario folder already bundles the clone state under `gmail-clone`
and `calendar-clone`. Load one with:

```bash
python -m pa_bench_sdk.cli load-scenario scenario_001_multi_meeting_coordination
```

Or use the `pa-bench` script installed via pip:

```bash
pa-bench load-scenario scenario_005_conflict_detection
```

Pass `--data-path` if your scenarios live elsewhere, or `--gmail-url`
/ `--calendar-url` to override environment variables.

## Verifying

After loading, run the verifier against the live clones:

```bash
python -m pa_bench_sdk.cli verify scenario_001_multi_meeting_coordination
```

The CLI fetches the current state for each clone, imports the scenario's
`verifier.py`, and prints the reward plus each `TaskVerifier`'s verdict.
It exits with a non-zero status if any check fails.



## Directory layout

- `data/`: Scenario folders as provided by the recent data batch. Each
  folder contains `task.json`, `data.json`, and `verifier.py`.
- `pa_bench_sdk/`: SDK modules (`scenario`, `worlds`, `verifier`, `cli`).
- `gordon/`: Local stand-in for the original `gordon.TaskVerifier`.
- `tests/`: Pytest test cases verifying loader, verifier, and CLI.


## Preparing Vibrant Labs worlds

If you already have clone URLs in environment variables or `.env`, the CLI
will reuse them. If they are missing, the SDK automatically creates clones
on Worlds Vibrant Labs by POSTing to `/envs/<type>/create` (same flow as
`/datasets-anthropic/pa-bench/create_instances.py`) and persists the new URLs
to `.env`.

```bash
GMAIL_INSTANCE_URL=http://xxx.worlds.vibrantlabs.com
CALENDAR_INSTANCE_URL=http://yyy.worlds.vibrantlabs.com
```

