from komodo.models.framework.models import OPENAI_GPT35_MODEL
from komodo.proto.generated.model_pb2 import Appliance, Agent, User, Tool
from komodo.store.agent_store import AgentStore
from komodo.store.appliance_store import ApplianceStore
from komodo.store.tool_store import ToolStore
from komodo.store.user_store import UserStore

# Define Users
user1 = User(email="ryan@komodoapp.ai", name="Ryan Oberoi")
user2 = User(email="ram@komodoapp.ai", name="Ramasamy Ramar")

# Define Agents
summarizer_agent = Agent(
    shortcode="summarizer",
    name="Summary Agent",
    purpose="Summarize text",
    model=OPENAI_GPT35_MODEL,
    provider="openai",
    instructions="Please summarize the following text in 50 words",
)

translator_agent = Agent(
    shortcode="translator",
    name="Translation Agent",
    purpose="Translate text",
    model=OPENAI_GPT35_MODEL,
    provider="openai",
    instructions="Please translate the following text into the languages requested by the user",
)

embedhelper_agent = Agent(
    shortcode="embedhelper",
    name="Embed Helper Agent",
    purpose="Transform text into Q&A json format",
    model=OPENAI_GPT35_MODEL,
    provider="openai",
    instructions="Transform the text into a Q&A json format for use in a chatbot or other application",
)

websearch_agent = Agent(
    shortcode="webguru",
    name="Web Search Agent",
    purpose="Search the web for information",
    model=OPENAI_GPT35_MODEL,
    provider="openai",
    instructions="Find the latest information on the topic of the text using web search tools",
    tool_shortcodes=["komodo_tavily_search"],
)

webscraper_agent = Agent(
    shortcode="scraper",
    name="Web Page Scraper Agent",
    purpose="Downloads web pages and acts on contents",
    model=OPENAI_GPT35_MODEL,
    provider="openai",
    instructions="Download the web page and extract the information needed as instructed.",
    tool_shortcodes=["komodo_web_content_extractor"],
)

# Define Tools
komodo_tavily_search = Tool(
    shortcode="komodo_tavily_search",
    name="Komodo Tavily Search",
    purpose="To perform advanced search operations"
)

komodo_web_content_extractor = Tool(
    shortcode="komodo_web_content_extractor",
    name="Komodo Web Content Extractor",
    purpose="To extract content from web pages"
)

# Define Appliance
appliance = Appliance(
    shortcode="sample",
    name="Sample",
    purpose="To test the Komodo Appliances SDK",
    agent_shortcodes=["summarizer", "translator", "webguru", "scraper", "embedhelper"],
    tool_shortcodes=["komodo_tavily_search", "komodo_web_content_extractor"]
)

if __name__ == "__main__":
    # Insert Users
    user_store = UserStore()
    user_store.add_user(user1)
    user_store.add_user(user2)

    # Insert Agents
    agent_store = AgentStore()
    agent_store.add_agent(summarizer_agent)
    agent_store.add_agent(translator_agent)
    agent_store.add_agent(embedhelper_agent)
    agent_store.add_agent(websearch_agent)
    agent_store.add_agent(webscraper_agent)

    # Insert Tools
    tool_store = ToolStore()
    tool_store.add_tool(komodo_tavily_search)
    tool_store.add_tool(komodo_web_content_extractor)

    # Insert Appliance
    appliance_store = ApplianceStore()
    appliance_store.add_appliance(appliance)

    print("All Protobuf objects have been added to their respective Redis stores.")
