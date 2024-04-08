import os
from pathlib import Path


class KomodoLocations:

    def __init__(self, path: Path, **kwargs):
        self.path = path
        self.kwargs = kwargs

    def local(self) -> Path:
        return self.path / "local"

    def shared(self) -> Path:
        return self.path / "shared"

    def cache(self) -> Path:
        return self.path / "cache"

    def cache_path(self) -> Path:
        return self.cache()

    def appliance_data(self, shortcode) -> Path:
        return self.path / "appliances" / shortcode

    def agent_data(self, shortcode) -> Path:
        return self.path / "agents" / shortcode

    def workflow_data(self, shortcode) -> Path:
        return self.path / "workflows" / shortcode

    def report_data(self, guid) -> Path:
        return self.path / "reports" / guid

    def user_data(self, email) -> Path:
        return self.path / "users" / email

    def user_uploads(self, email) -> Path:
        return self.user_data(email) / "uploads"

    def user_collections(self, email) -> Path:
        return self.user_data(email) / "collections"

    def files(self, folder) -> [Path]:
        return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

    def all_files(self, folder) -> [Path]:
        return [f for f in folder.glob("**/*") if os.path.isfile(os.path.join(folder, f))]

    def setup_appliance(self, shortcode, agents=None, workflows=None, reports=None, users=None):
        os.makedirs(self.appliance_data(shortcode), exist_ok=True)
        for agent in agents or []:
            os.makedirs(self.agent_data(agent), exist_ok=True)
        for workflow in workflows or []:
            os.makedirs(self.workflow_data(workflow), exist_ok=True)
        for report in reports or []:
            os.makedirs(self.report_data(report), exist_ok=True)
        for user in users or []:
            os.makedirs(self.user_data(user), exist_ok=True)
            os.makedirs(self.user_uploads(user), exist_ok=True)
            os.makedirs(self.user_collections(user), exist_ok=True)

    def setup_agent(self, shortcode):
        os.makedirs(self.agent_data(shortcode), exist_ok=True)


if __name__ == "__main__":
    from komodo.config import PlatformConfig

    data = KomodoLocations(PlatformConfig().data_directory)
    data.setup_appliance("test", ["test"], ["test"], ["test"], ["test"])
    print(data.shared())
    print(data.cache())
    print(data.appliance_data("test"))
    print(data.agent_data("test"))
    print(data.workflow_data("test"))
    print(data.report_data("test"))
    print(data.user_data("test"))

    print(data.user_uploads("test"))
    print(data.user_collections("test"))
