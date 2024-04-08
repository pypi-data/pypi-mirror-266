import copy
from pathlib import Path

from komodo.framework.komodo_agent import KomodoAgent
from komodo.framework.komodo_app import KomodoApp
from komodo.framework.komodo_collection import KomodoCollection
from komodo.framework.komodo_config import KomodoConfig
from komodo.framework.komodo_user import KomodoUser
from komodo.framework.komodo_workflow import KomodoWorkflow


class KomodoRuntime():
    def __init__(self, **kwargs):
        self.appliance: KomodoApp = kwargs.get("appliance")
        self.config: KomodoConfig = kwargs.get("config", self.appliance.config if self.appliance else None)
        self.workflow: KomodoWorkflow = kwargs.get("workflow")
        self.tools_invocation_callback = None
        self.tools_response_callback = None
        self.kwargs = kwargs

        self.set_agent(kwargs.get("agent"))
        self.set_selected_collection(kwargs.get("selected_collection"))
        self.set_user(kwargs.get("user"))

    def set_agent(self, agent: KomodoAgent):
        self.agent = agent
        if self.agent:
            self.model = self.agent.model
            self.temperature = self.agent.temperature
            self.top_p = self.agent.top_p
            self.seed = self.agent.seed
            self.max_tokens = self.agent.max_tokens

    def set_selected_collection(self, selected_collection: KomodoCollection):
        self.selected_collection = selected_collection
        if self.selected_collection:
            self.selected_collection.cache = self.config.cache()
            if self.selected_collection.get_total_tokens() > 10000:
                print("Collection is large, upgrading to GPT-4")
                self.model = 'gpt-4-turbo-preview'

    def set_user(self, user: KomodoUser):
        self.user = user
        # ensure user's home and downloads collections are created
        if self.user:
            self.home_folder = next(self.get_user_home())
            self.downloads_folder = next(self.get_user_downloads())

    def get_user_home(self):
        path = self.config.locations().user_collections(self.user.email) / self.user.home_shortcode
        collection = KomodoCollection(shortcode=self.user.home_shortcode, name="Home", path=path,
                                      description=f"{self.user.name}'s Home collection", user=self.user,
                                      cache=self.config.cache())
        yield collection

    def get_user_downloads(self):
        path = self.config.locations().user_collections(self.user.email) / self.user.downloads_shortcode
        collection = KomodoCollection(shortcode=self.user.downloads_shortcode, name="Downloads", path=path,
                                      description=f"{self.user.name}'s Downloads collection", user=self.user,
                                      cache=self.config.cache())
        yield collection

    def get_shared_collections(self):
        if not self.config.shared().exists():
            return

        for item in self.config.shared().iterdir():
            if item.is_dir():
                collection = KomodoCollection(path=item, name=f"Shared: {Path(item).stem}",
                                              description=f"Shared: {item.name}", cache=self.config.cache())
                yield collection

    def get_user_collections(self):
        if not self.user or not self.config.locations().user_collections(self.user.email).exists():
            return

        for item in self.config.locations().user_collections(self.user.email).iterdir():
            if item.is_dir() and item.name not in [self.user.home_shortcode, self.user.downloads_shortcode]:
                collection = KomodoCollection(path=item, name=Path(item).stem,
                                              description=f"User: {item.name}", cache=self.config.cache())
                yield collection

    def get_available_collections(self):
        return list(self.get_user_home()) + list(self.get_user_downloads()) + list(
            self.get_shared_collections()) + list(self.get_user_collections())

    def get_collection(self, shortcode):
        for collection in self.get_available_collections():
            if collection.shortcode == shortcode:
                return collection

    def __str__(self):
        template = "From: {} To: {} Name: {} (provider: {}, model: {})"
        return template.format(self.user.email if self.user else "Anon",
                               self.agent.email,
                               self.agent.name,
                               self.agent.provider,
                               self.agent.model)

    def basecopy(self):
        return KomodoRuntime(config=self.config, appliance=self.appliance, user=self.user)

    def copy(self):
        return copy.copy(self)

    def deepcopy(self):
        return copy.deepcopy(self)


if __name__ == "__main__":
    from komodo.config import PlatformConfig

    appliance = KomodoApp.default()
    agent = KomodoAgent.default()
    user = KomodoUser.default()
    config = PlatformConfig()

    runtime = KomodoRuntime(appliance=appliance, agent=agent, user=user, config=config)
    print(runtime)

    nr = copy.copy(runtime)
    nr.agent = KomodoAgent(shortcode="new_agent", name="New Agent", instructions="New instructions")
    print(nr)

    print(runtime)
    for collection in runtime.get_available_collections():
        print(collection.name)
