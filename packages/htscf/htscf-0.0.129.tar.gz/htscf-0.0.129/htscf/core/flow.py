import json
import os
import subprocess
import uuid
from pathlib import Path
import yaml

from htscf.utils.logging import Logger
from htscf.utils.tools import del_nested_attr


class Workflow:
    def __init__(self, workflow_definition):
        self.workflow = workflow_definition
        self.flow_id = f"{self.workflow['name']}_{uuid.uuid4()}"
        self.flow_path = Path(self.flow_id)
        self.flow_path.mkdir(exist_ok=True, parents=True)
        self.logger = Logger()

    def set_global_env(self):
        for var, value in self.workflow.get("env", {}).items():
            os.environ[var] = str(value)

    def run(self):
        self.set_global_env()
        prev_step_info = {}
        for step in self.workflow['steps']:
            for step_name, step_details in step.items():
                current_step_info = self.prepare_step(step_name, step_details)
                if not self.run_step(step_name, current_step_info, prev_step_info):
                    return  # Stop the flow if any step fails
                prev_step_info = current_step_info

    def prepare_step(self, step_name, step_details):
        step_id = f"{step_name}_{uuid.uuid4()}"
        step_path = self.flow_path / step_id
        step_path.mkdir(exist_ok=True, parents=True)
        return {
            "flow_id": self.flow_id,
            "flow_path": self.flow_path.absolute().as_posix(),
            "step_id": step_id,
            "step_path": step_path.absolute().as_posix(),
            "step_details": step_details
        }

    def run_step(self, step_name, current_step_info, prev_step_info):
        self.logger.info(f"Running step: {step_name}")
        self.set_env(current_step_info)
        self.create_step_files(current_step_info)
        try:
            self.exec_script(current_step_info, prev_step_info)
        except Exception as e:
            self.logger.error({
                "content": f"Step '{step_name}' interrupted: {e}",
                "current_step_info": current_step_info
            })
            return False
        return True

    @staticmethod
    def set_env(current_step_info):
        for var, value in current_step_info["step_details"].get("env", {}).items():
            os.environ[var] = str(value)

    @staticmethod
    def create_step_files(current_step_info):
        step_path = Path(current_step_info["step_path"])
        for fileName, content in current_step_info["step_details"].get("files", {}).items():
            (step_path / fileName).write_text(content, encoding="utf-8")

        run = current_step_info["step_details"].get("run", "")
        (step_path / "run").write_text(run, encoding="utf-8")

    def exec_script(self, current_step_info, prev_step_info):
        context = self.get_context_before_run(current_step_info, prev_step_info)
        with open(context["stdoutPath"], "a+", encoding="utf-8") as stdout, \
                open(context["stderrPath"], "a+", encoding="utf-8") as stderr:
            env = os.environ.copy()
            env.update(context["info"])
            subprocess.Popen([context['shell'], context["scriptPath"]],
                             stdout=stdout, stderr=stderr, env=env, cwd=context["step_path"]).communicate()
            if stderr.tell():
                stdout.seek(0)
                stderr.seek(0)
                raise Exception(json.dumps({"stdout": stdout.read(), "stderr": stderr.read()}))

    @staticmethod
    def get_context_before_run(current_step_info, prev_step_info):
        del_nested_attr(current_step_info, "step_details.files")
        del_nested_attr(prev_step_info, "step_details.files")
        step_path = Path(current_step_info["step_path"])
        return {
            "scriptPath": step_path / "run",
            "stdoutPath": step_path / "stdout",
            "stderrPath": step_path / "stderr",
            "step_path": step_path,
            "shell": current_step_info["step_details"].get("shell", ""),
            "info": {
                "current_step_info": json.dumps(current_step_info),
                "prev_step_info": json.dumps(prev_step_info)
            }
        }
