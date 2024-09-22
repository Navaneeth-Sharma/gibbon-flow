import argparse
import ast
import yaml
from gibbon_flow.gibbon_schedular import (
    get_jobs_from_yaml,
    schedule_jobs,
    run_scheduler,
)

class FlowAndTaskDetector(ast.NodeVisitor):
    def __init__(self):
        self.tasks = {}  # Store tasks with their names
        self.flows = {}  # Store flows and the tasks/flows they call

    def visit_FunctionDef(self, node):
        # Check if the function has decorators
        if node.decorator_list:
            for decorator in node.decorator_list:
                # Check for the `@task(name="...")` decorator
                if isinstance(decorator, ast.Call) and isinstance(
                    decorator.func, ast.Name
                ):
                    if decorator.func.id == "task" and decorator.keywords:
                        task_name = next(
                            (
                                kw.value.s
                                for kw in decorator.keywords
                                if kw.arg == "name"
                            ),
                            None,
                        )
                        if task_name:
                            self.tasks[node.name] = task_name

                # Check for the `@flow(name="...")` decorator
                if isinstance(decorator, ast.Call) and isinstance(
                    decorator.func, ast.Name
                ):
                    if decorator.func.id == "flow" and decorator.keywords:
                        flow_name = next(
                            (
                                kw.value.s
                                for kw in decorator.keywords
                                if kw.arg == "name"
                            ),
                            None,
                        )
                        if flow_name:
                            # Track the flow and the tasks/flows it calls
                            called_tasks = self.get_called_tasks(node)
                            self.flows[flow_name] = called_tasks

        self.generic_visit(node)

    def get_called_tasks(self, node):
        """Get the list of tasks/flows called within the flow function"""
        flow_data = {
            "tasks": [],
            "flows": [],
            "cron": "* * * * *",  # Default to run once (every minute)
            "entry_point": f"{node.name}:{node.name}",  # Add entry point
        }
        for body_node in node.body:
            if isinstance(body_node, ast.Expr) and isinstance(
                body_node.value, ast.Call
            ):
                if isinstance(body_node.value.func, ast.Name):
                    func_name = body_node.value.func.id
                    if func_name in self.tasks:
                        flow_data["tasks"].append(
                            {
                                "name": self.tasks[func_name],
                                "type": "TASK",
                                "entry_point": f"{node.name}:{func_name}",
                            }
                        )
                    elif func_name in self.flows:
                        flow_data["flows"].append(
                            {
                                "name": func_name,
                                "type": "FLOW",
                                "entry_point": f"{node.name}:{func_name}",
                            }
                        )
        return flow_data


def detect_flows_and_tasks(file_path):
    with open(file_path, "r") as file:
        file_content = file.read()
        tree = ast.parse(file_content)

        detector = FlowAndTaskDetector()
        detector.visit(tree)

        flows = detector.flows
        for flow_name, flow_data in flows.items():
            flow_data["file_name"] = file_path
            flow_data["entry_point"] = f"{file_path}:{flow_name}"

        return flows


def save_to_yaml(data, output_file="flows_and_tasks.yaml"):
    with open(output_file, "w") as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False)
    print(f"Results saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Create your flows and cron jobs with ease"
    )
    parser.add_argument(
        "command",
        help="""
        \n analyze: analyze the file and save the flows and tasks to a yaml file \n
        startserver: start the server \n
        startschedular: start the schedular \n
        """,
    )
    parser.add_argument("file", help="file to analyze/")
    parser.add_argument(
        "--output", help="Output YAML file", default="flows_and_tasks.yaml"
    )

    args = parser.parse_args()

    if args.command == "analyze":
        # Detect flows and tasks
        results = detect_flows_and_tasks(args.file)

        print(f"Detected Flows and Tasks in {args.file}:")
        for flow, calls in results.items():
            print(f"Flow: {flow}, Calls: {calls}")

        # Save results to YAML
        save_to_yaml(results, args.output)

    if args.command == "startserver":
        print("Starting server")

    if args.command == "startschedular":
        jobs = get_jobs_from_yaml(args.file)
        scheduled_jobs = schedule_jobs(jobs)
        run_scheduler(scheduled_jobs)


if __name__ == "__main__":
    main()
