import os
from pathlib import Path


class LoaderLocations:

    def __init__(self, path, **kwargs):
        self.path = path
        self.kwargs = kwargs

    def appliances(self) -> Path:
        return self.path / "appliances"

    def available_appliances(self) -> list[str]:
        folder = self.appliances()
        return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]

    def appliance(self, shortcode) -> Path:
        return self.appliances() / shortcode

    def agents(self) -> Path:
        return self.path / "agents"

    def agent(self, shortcode) -> Path:
        return self.agents() / shortcode

    def available_agents(self) -> list[str]:
        folder = self.agents()
        return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]

    def workflows(self) -> Path:
        return self.path / "workflows"

    def workflow(self, shortcode) -> Path:
        return self.workflows() / shortcode

    def available_workflows(self) -> list[str]:
        folder = self.workflows()
        return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]

    def reports(self) -> Path:
        return self.path / "reports"

    def report(self, guid) -> Path:
        return self.reports() / guid

    def available_reports(self) -> list[str]:
        folder = self.reports()
        return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]

    def users(self) -> Path:
        return self.path / "users"

    def user(self, email) -> Path:
        return self.users() / email

    def setup_appliance(self, shortcode, skeleton=False):
        for d in [self.appliances(), self.agents(), self.users(), self.workflows()]:
            os.makedirs(d, exist_ok=True)

        os.makedirs(self.appliance(shortcode), exist_ok=True)
        if skeleton:
            self.setup_appliance_skeleton(shortcode)

    def setup_appliance_skeleton(self, shortcode):
        for file in ["appliance.yml", "context.yml", "dictionary.yml"]:
            path = self.appliance(shortcode) / file
            if not path.exists():
                path.touch()

    def setup_agent(self, shortcode, skeleton=False):
        os.makedirs(self.agent(shortcode), exist_ok=True)
        if skeleton:
            for file in ["agent.yml", "context.yml", "dictionary.yml"]:
                path = self.agent(shortcode) / file
                if not path.exists():
                    path.touch()

    def setup_workflow(self, shortcode, skeleton=False):
        os.makedirs(self.workflow(shortcode), exist_ok=True)
        if skeleton:
            for file in ["workflow.yml", "context.yml", "dictionary.yml"]:
                path = self.workflow(shortcode) / file
                if not path.exists():
                    path.touch()

    def setup_report(self, guid, skeleton=False):
        os.makedirs(self.report(guid), exist_ok=True)
        if skeleton:
            for file in ["report.yml", "context.yml", "dictionary.yml"]:
                path = self.report(guid) / file
                if not path.exists():
                    path.touch()

    def setup_user(self, email):
        os.makedirs(self.user(email), exist_ok=True)
        for file in ["user.yml"]:
            path = self.user(email) / file
            if not path.exists():
                path.touch()

    def setup(self, appliance, agents, workflows, reports, users):
        self.setup_appliance(appliance, skeleton=True)
        for agent in agents:
            self.setup_agent(agent, skeleton=True)
        for workflow in workflows:
            self.setup_workflow(workflow, skeleton=True)
        for report in reports:
            self.setup_report(report, skeleton=True)
        for user in users:
            self.setup_user(user)


if __name__ == "__main__":
    from komodo.config import PlatformConfig

    email = "ryan@kmdo.app"
    config = PlatformConfig()
    locations = LoaderLocations(config.definitions_directory)

    locations.setup("sample", ["planner", "checker"], ["analyzer"], ['r123', 'r124'],
                    ["ryan@kmdo.app", "test@example.com"])

    test_appliance = "sample"
    print(locations.appliances())
    print(locations.appliance(test_appliance))

    test_agent = "planner"
    print(locations.agents())
    print(locations.agent(test_agent))

    test_workflow = "analyzer"
    print(locations.workflows())
    print(locations.workflow(test_workflow))

    print(locations.users())
    print(locations.user(email))

    print(locations.available_appliances())
    print(locations.available_agents())
    print(locations.available_workflows())
    print(locations.available_reports())
