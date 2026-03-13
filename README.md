# Heisenrun

**Heisenrun** is a small CLI tool for reproducing **heisenbugs** by running many instances of a command in parallel.

Heisenbugs are bugs that appear only under certain timing or concurrency conditions and disappear when you try to debug them. Heisenrun increases the chance of triggering such bugs by repeatedly executing a command concurrently.

Typical use cases:
- Reproducing flaky tests
- Triggering race conditions
- Stress-testing CLI programs
- Detecting nondeterministic behavior


## Getting Started

### Run instantly (recommended)

Using [uv](https://docs.astral.sh/uv/):

```sh
uv tool run heisenrun --help
```

Example:
```sh
uv tool run heisenrun -n 10 -m 2 -- sleep {#}
```

This downloads and installs heisenrun into an isolated environment.
If you wish more control please consider the next command.

### Install tool via UV (also recommended)

You can explicitly also heisenrun with [uv](https://docs.astral.sh/uv/):

```sh
uv tool install heisenrun
```

Then run:

```
heisenrun --help
```

The `uv tool install` command gives you more control. You can specify the tool's version, manually upgrade it, remove it, and etc.

### Install with pipx

[pipx](https://pipx.pypa.io/stable/) also installs CLI tools in isolated environments:

```sh
pipx install heisenrun
```

Then run:

```sh
heisenrun --help
```

### Install with pip (not recommended)

Global installation via pip works but is generally discouraged for CLI tools:

```sh
pip install heisenrun
```

## Examples


### Run a command 10 times

All 10 processes are created instantly.
They run in parallel.

```sh
heisenrun -n 10 -- sleep 1
```

### Use run index `{#}`

Use `{#}` in command to insert the index of the current run:

```
heisenrun -n 10 -- sleep {#}
```

Example expansion:
```
sleep 0
sleep 1
sleep 2
...
sleep 9
```

### Limit parallelism

The `-m` option allows you to specify the maximum number of commands running in parallel.
This will take about 5 seconds.

```sh
heisenrun -n 10 -m 2 -- sleep 1
```

### Set timeouts

Abort runs that take too long:

```
heisenrun -n 10 -t 5s -- sleep {#}
```

Example report:
```
   Execution Report
┏━━━━━━━━━━┳━━━━━━━━━┓
┃ Instance ┃ Status  ┃
┡━━━━━━━━━━╇━━━━━━━━━┩
│        0 │ SUCCESS │
│        1 │ SUCCESS │
│        2 │ SUCCESS │
│        3 │ SUCCESS │
│        4 │ SUCCESS │
│        5 │ SUCCESS │
│        6 │ TIMEOUT │
│        7 │ TIMEOUT │
│        8 │ TIMEOUT │
│        9 │ TIMEOUT │
└──────────┴─────────┘
```

### Capture outputs

Store outputs (stdout and stderr) of each run in a directory:

```sh
heisenrun -n 50 -o outputs -- ./program
```

Example directory structure:

```
outputs/
  0_output.txt
  1_output.txt
  ...
```
