from .base import BobEndpoint
from .models.Tasks import Task
from typing import Optional


class Tasks(BobEndpoint):
    def read(self):
        """
        Returns a list of all open tasks

        References:
            https://apidocs.hibob.com/reference/get_tasks
        """
        response = self.client.get("tasks")

        tasks = [
            Task(
                id=task["id"],
                owner=task["owner"],
                title=task["title"],
                requestedFor=task["requestedFor"],
                due=task["due"],
                linkInBob=task["linkInBob"],
                set=task["set"],
                workflow=task["workflow"],
                ordinalInWorkflow=task["ordinalInWorkflow"],
                description=task["description"],
                status=task["status"],
                completionDate=task["completionDate"],
                employeeGroupId=task["employeeGroupId"],
                companyId=task["companyId"],
            )
            for task in response["tasks"]
        ]

        return tasks

    def read_specific_employee(self, employeeId: str, taskStatus: Optional[str] = None):
        """
        Returns a list of all tasks for a specific employee

        Args:
            employeeId (str): The ID of the employee to get tasks for
            taskStatus (Optional[str]): The status of the tasks to filter by. Options are "open" and "closed"

        References:
            https://apidocs.hibob.com/reference/get_tasks-people-id
        """
        query = {}

        if taskStatus:
            query["taskStatus"] = taskStatus

        response = self.client.get(f"tasks/people/{employeeId}", query=query)

        tasks = [
            Task(
                id=task["id"],
                owner=task["owner"],
                title=task["title"],
                requestedFor=task["requestedFor"],
                due=task["due"],
                linkInBob=task["linkInBob"],
                set=task["set"],
                workflow=task["workflow"],
                ordinalInWorkflow=task["ordinalInWorkflow"],
                description=task["description"],
                status=task["status"],
                completionDate=task["completionDate"],
                employeeGroupId=task["employeeGroupId"],
                companyId=task["companyId"],
            )
            for task in response["tasks"]
        ]

        return tasks

    def mark_task_complete(self, task_id: str):
        """
        Marks a task as complete

        Args:
            task_id (str): The ID of the task to mark as complete

        References:
            https://apidocs.hibob.com/reference/post_tasks-taskid-complete
        """
        return self.client.post(f"tasks/{task_id}/complete")
