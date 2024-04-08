# Devcord

Devcord is a CLI tool designed to help you quickly manage your tasks as well as
help you monitor your time usage. Along with all the essential to-do list functionalities, Devcord allows you to select a task and start a session on it.

During a session, your time-spent on each of your activity is monitored for you to view later. This is useful for people who want to find out where their time is spent.

None of the data is stored on any server, it is all stored locally on your machine.

# Installation

With pip:

pip install devcord

# Usage

## For adding tasks

Simple add task:

```bash
$ devcord tasks -a "task name"
$ devcord tasks --add "task name"
```

With description:

```bash
$ devcord tasks -a "task name" -d
$ devcord tasks --add "task name" --desc
```

_Opens scrollable text box to enter description_

With due date:

```bash
$ devcord tasks -a "task name" -dd "dd/mm/yyyy"
$ devcord tasks --add "task name" --due "dd/mm/yyyy"
```

Complete by today:

```bash
$ devcord tasks -a "task name" -t
$ devcord tasks --add "task name" --today
```

Complete in current week:

```bash
$ devcord tasks -a "task name" -w
$ devcord tasks --add "task name" --week
```

With priority (1-5):

```bash
$ devcord tasks -a "task name" -p 3
$ devcord tasks --add "task name" --priority 3
```

With labels:

```bash
$ devcord tasks -a "task name" -lb "label"
$ devcord tasks --add "task name" --label "label"
```

Add subtask:

```bash
$ devcord tasks -a "task name" -pid task_id
$ devcord tasks --add "task name" --parent task_id
```

## For listing tasks

By default, in-progress and pending tasks are listed, with in-progress first followed by pending tasks and completed tasks are skipped.

Simple List tasks:

```bash
$ devcord tasks -l
$ devcord tasks --list
```

List tasks by priority:

```bash
$ devcord tasks -l -p 3
$ devcord tasks --list --priority 3
```

List tasks by label:

```bash
$ devcord tasks -l -lb "label"
$ devcord tasks --list --label "label"
```

List today's tasks:

```bash
$ devcord tasks -l -t
$ devcord tasks --list --today
```

List tasks due in current week:

```bash
$ devcord tasks -l -w
$ devcord tasks --list --week
```

List tasks by status:

```bash
$ devcord tasks -l -i
$ devcord tasks --list --completed
$ devcord tasks -l --pending
```

Specify Output Format:

```bash
$ devcord tasks -l -o json
$ devcord tasks --list --output text
```

Specify Output File:

```bash
$ devcord tasks -l --path "path/to/file"
```
## For managing tasks

Pass the task ID after the **"task"** keyword to perform any action on the task.

Viewing description:

```bash
$ devcord task 1 -d
$ devcord task 1 --desc
```

_Opens a scrollable text box with description_

Show substasks:

```bash
$ devcord task 4 -st
$ devcord task 4 --subtasks
```

Mark as inprogress:

```bash
$ devcord task 3 -i
$ devcord task 3 --inprogress
```

Mark as complete:

```bash
$ devcord task 2 -c
$ devcord task 2 --completed
```

Mark as pending:

```bash
$ devcord task 10 -pd
$ devcord task 10 --pending
```
