import os
from datetime import datetime

import click

import app.application as application
from app.console import print_tasks
from app.constants import path
from app.database import initialize

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def cli(ctx):
    """
    Devcord is a CLI tool for developers to help them with their daily tasks.
    """
    ctx.ensure_object(dict)
    if not path:
        click.echo(
            click.style(
                "Error: Could not find the path to the database, raise an issue with the developers.",
                fg="red",
            ),
        )
        ctx.abort()
        return

    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        initialize()


@cli.command()
@click.pass_context
@click.option("-l", "--list", is_flag=True, help="List all the tasks")
@click.option("-a", "--add", help="Add a new task", type=str)
@click.option("-d", "--desc", is_flag=True, help="Add a description to a task")
@click.option("-p", "--priority", help="Set the priority of a task", type=int)
@click.option("-t", "--today", is_flag=True, help="Perform for all the tasks for today")
@click.option(
    "-w",
    "--week",
    is_flag=True,
    help="Perform for  all the tasks for this week",
)
@click.option(
    "-dd",
    "--deadline",
    help='Set the deadline of a task, date format: "dd/mm/yyyy/"',
    type=str,
)
@click.option(
    "-i",
    "--inprogress",
    is_flag=True,
    help="Perform for all the tasks that are in progress",
)
@click.option(
    "-c",
    "--completed",
    is_flag=True,
    help="Perform for all the tasks that are completed",
)
@click.option(
    "-pd",
    "--pending",
    is_flag=True,
    help="Perform for all the tasks that are pending",
)
@click.option(
    "-lb",
    "--label",
    help="Perform for all the tasks with a specific label",
    type=str,
)
@click.option("-o", "--output", help="Specify Output Format", type=str)
@click.option("--path", help="Specify Output File", type=str)
@click.option("-pid", "--parent", help="Set the parent of a task", type=int)
def tasks(
    ctx,
    list=None,
    add=None,
    desc=None,
    priority=None,
    today=None,
    week=None,
    deadline=None,
    inprogress=None,
    completed=None,
    pending=None,
    label=None,
    output=None,
    path=None,
    parent=None,
):
    """
    Create and List tasks.
    """
    if deadline:
        try:
            deadline = convert_to_db_date(deadline)
        except ValueError:
            click.echo(
                click.style(
                    'Error: Invalid date format, please use "dd/mm/yyyy".',
                    fg="red",
                ),
            )
            click.echo('Example: "01/01/2020"')
            return

    if list:
        print_tasks(
            application.list_tasks(
                priority=priority,
                today=today,
                week=week,
                inprogress=inprogress,
                completed=completed,
                pending=pending,
                label=label,
            ),
            output,
            path,
        )
    elif add:
        description = None
        add = add
        if desc:
            description = click.edit()
        if parent:
            val = application.search_task(parent)
            if not val:
                click.echo(
                    click.style(
                        "Error: Parent task does not exist.",
                        fg="red",
                    ),
                )
                return
        application.add_tasks(
            add,
            description,
            priority,
            today,
            week,
            deadline,
            inprogress,
            completed,
            pending,
            label,
            parent,
        )


@cli.command()
@click.pass_context
@click.argument("task_id", type=int, required=True)
@click.option(
    "-d",
    "--desc",
    help="View and edit description of the task",
    is_flag=True,
)
@click.option(
    "-i",
    "--inprogress",
    is_flag=True,
    help="Mark Task As In Progress",
)
@click.option(
    "-c",
    "--completed",
    is_flag=True,
    help="Mark Task As Completed",
)
@click.option(
    "-pd",
    "--pending",
    is_flag=True,
    help="Mark Task As Pending",
)
@click.option(
    "-st",
    "--subtasks",
    is_flag=True,
    help="List All Subtask Of Task",
)
def task(
    ctx,
    task_id,
    desc=None,
    inprogress=None,
    completed=None,
    pending=None,
    subtasks=None,
):
    """
    Modify a specific task.
    """
    if subtasks:
        print_tasks(application.get_subtasks(task_id))
        return

    current_task = application.search_task(task_id)
    if not current_task:
        click.echo(
            click.style(
                "Error: Task does not exist.",
                fg="red",
            ),
        )
        return

    if desc:
        description = "No given description"
        if current_task["description"]:
            description = current_task["description"]
        current_task["description"] = click.edit(description)

    if inprogress:
        current_task["status"] = "In Progress"
    elif pending:
        current_task["status"] = "Pending"
    elif completed:
        current_task["status"] = "Completed"

    # update values in db
    application.update_task(current_task)


def convert_to_db_date(date_str):
    # Convert date from "dd/mm/yyyy" to "YYYY-MM-DD"
    date_obj = datetime.strptime(date_str, "%d/%m/%Y")
    return date_obj.strftime("%Y-%m-%d")
