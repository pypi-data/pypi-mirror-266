from datetime import datetime

from . import database


def list_tasks(
    priority=None,
    today=None,
    week=None,
    inprogress=None,
    completed=None,
    pending=None,
    label=None,
) -> list:
    """
    List all the tasks based on the filters.
    """
    order_by = "completed ASC, status ASC, priority DESC"
    where_clause = ["parent_id ISNULL"]
    if week:
        where_clause.append(
            "(deadline >= date('now', 'weekday 0', '-7 days') AND deadline < date('now', 'weekday 1'))",
        )
    elif today:
        where_clause.append("(deadline = date('now'))")
    if inprogress or completed or pending:
        clause = []
        if inprogress:
            clause.append("'In Progress'")
        if completed:
            clause.append("'Completed'")
        if pending:
            clause.append("'Pending'")
        where_clause.append("status in (" + ",".join(clause) + ")")
    else:
        clause = ["'In Progress'", "'Pending'"]
        where_clause.append("status in (" + ",".join(clause) + ")")

    if priority:
        where_clause.append(f"priority = {priority}")

    if label:
        where_clause.append(f"label = '{label}'")
    where_clause = "WHERE " + " AND ".join(where_clause)

    results = database.list_table(
        table="tasks",
        columns=[
            "id",
            "title",
            "status",
            "deadline",
            "priority",
            "label",
            "description",
        ],
        where_clause=where_clause,
        order_by=f"ORDER BY {order_by}",
    )

    final_results = []
    for result in results:
        final_results.append(
            {
                "id": result[0],
                "title": result[1],
                "status": result[2],
                "deadline": (
                    result[3]
                    if str(result[3]) == "None"
                    else convert_to_console_date(result[3])
                ),
                "priority": result[4],
                "label": result[5] if result[5] else "None",
                "description": result[6],
            },
        )
    return final_results


def add_tasks(
    title,
    description=None,
    priority=None,
    today=False,
    week=False,
    deadline=None,
    inprogress=None,
    completed=None,
    pending=None,
    label=None,
    parent=None,
):
    """
    Add a task to the database.
    """
    columns = ["title"]
    values = [f'"{sanitize_text(title)}"' ""]
    if description:
        columns.append("description")
        values.append(f'"{sanitize_text(description)}"')
    if priority:
        columns.append("priority")
        values.append(str(priority))
    if today:
        columns.append("deadline")
        values.append("date('now')")
    elif week:
        columns.append("deadline")
        values.append("date('now', 'weekday 0')")
    elif deadline:
        columns.append("deadline")
        values.append(f"'{deadline}'")
    if inprogress:
        columns.append("status")
        values.append("'In Progress'")
    elif completed:
        columns.append("status")
        values.append("'Completed'")
    elif pending:
        columns.append("status")
        values.append("'Pending'")
    if label:
        columns.append("label")
        values.append(f'"{sanitize_text(label)}"')
    if parent:
        columns.append("parent_id")
        values.append(str(parent))
    database.insert_into_table(table="tasks", columns=columns, values=values)


def search_task(task_id) -> dict:
    """
    Search a task by its id.
    :param task_id:
    :return: task_details
    """
    task = database.list_table(
        table="tasks",
        columns=[
            "id",
            "title",
            "description",
            "status",
            "deadline",
            "priority",
            "label",
            "completed",
        ],
        where_clause=f"WHERE id = {task_id}",
    )
    task_details = {}
    if task:
        task = task[0]
        task_details = {
            "id": task[0],
            "title": task[1],
            "description": task[2],
            "status": task[3],
            "deadline": task[4],
            "priority": task[5],
            "label": task[6] if task[6] else "None",
            "completed": (task[7]),
        }
    return task_details


def get_subtasks(task_id: int):
    results = database.list_table(
        table="tasks",
        columns=[
            "id",
            "title",
            "status",
            "deadline",
            "priority",
            "label",
        ],
        where_clause=f"WHERE parent_id = {task_id}",
    )
    final_results = []
    for result in results:
        final_results.append(
            {
                "id": result[0],
                "title": result[1],
                "status": result[2],
                "deadline": (
                    result[3]
                    if str(result[3]) == "None"
                    else convert_to_console_date(result[3])
                ),
                "priority": result[4],
                "label": result[5] if result[5] else "None",
            },
        )
    return final_results


def update_task(updated_data: dict):
    """If marked as completed then set datetime as now else prev value retain"""
    updated_data["deadline"] = str(updated_data["deadline"])
    if updated_data["status"] == "Completed":
        current_date = datetime.now().strftime("%Y-%m-%d")
        updated_data["completed"] = str(current_date)
    else:
        updated_data["completed"] = updated_data["deadline"]

    for key, value in updated_data.items():

        print(type(value), value, key)
        if type(value) is str or not value:
            updated_data[key] = f'"{value}"'

    database.update_table("tasks", updated_data)


def convert_to_console_date(date_str):
    """
    Convert date from "YYYY-MM-DD" to "dd/mm/yyyy"
    """
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%d/%m/%Y")


def sanitize_text(text):
    return text.replace('"', "'")
