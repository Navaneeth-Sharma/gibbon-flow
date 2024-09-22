# Gibbon Flow

Gibbon Flow is a powerful and flexible workflow management system that allows you to easily define, schedule, and execute complex workflows and tasks.
![image](https://github.com/user-attachments/assets/0bd148eb-2a86-4862-bac1-4752b034910d)


## Features

- Define workflows and tasks using simple Python decorators
- Automatically analyze Python files to extract workflow and task definitions
- Schedule workflows using cron expressions
- Distributed execution of tasks using Dask
- Persistent storage of job execution details in SQLite database

## Installation

To install Gibbon Flow, clone the repository and install it in editable mode:

```bash
git clone https://github.com/gibbon-flow/gibbon-flow.git
cd gibbon-flow
pip install -e .
```

## Usage

### 1. Define your workflows and tasks

Create a Python file (e.g., `test.py`) with your workflow and task definitions:

### 2. Analyze your workflow file

Use the `flow_gibbon analyze` command to analyze your workflow file and generate a YAML configuration:

```bash
flow_gibbon analyze test.py
```

This will create a `flows_and_tasks.yaml` file with the extracted workflow and task information.

### 3. Start the scheduler

To start executing your workflows based on the generated YAML file, use the `startschedular` command:

```bash
flow_gibbon startschedular
```

### 4. Check the database 

The database will be created in the current working directory and named `flow_gibbon.db`. 
