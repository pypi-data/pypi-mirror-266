import json
from datetime import datetime

from dash import dcc

from komodo.core.agents.echo_agent import EchoAgent
from komodo.core.agents.groot_agent import GrootAgent
from komodo.framework.komodo_app import KomodoApp
from komodo.framework.komodo_runtime import KomodoRuntime
from komodo.framework.komodo_user import KomodoUser
from komodo.models.framework.agent_runner import AgentRunner

g_appliance: KomodoApp = KomodoApp.default()


def get_appliance() -> KomodoApp:
    return g_appliance


def set_appliance_for_dash(appliance: KomodoApp):
    global g_appliance
    g_appliance = appliance


# Simulated function to get agent names. In practice, replace this with your actual function.
def get_agents():
    appliance = get_appliance()
    agents = appliance.get_all_agents() if appliance else []
    return agents or [EchoAgent(), GrootAgent()]


def get_agent_response(agent_shortcode, prompt):
    appliance: KomodoApp = get_appliance()
    agent = next(agent for agent in get_agents() if agent.shortcode == agent_shortcode)
    runtime = KomodoRuntime(appliance=appliance, agent=agent, user=KomodoUser.default())
    runner = AgentRunner(runtime)
    print(f"Sending prompt to {agent.name}: {prompt}")
    response = runner.run(prompt)
    print(f"Response received from {agent.name}: {response}")
    save_response(appliance, agent_shortcode, prompt, response)
    return response


def save_response(appliance, agent_shortcode, prompt, response):
    folder = appliance.config.local() / "responses" / agent_shortcode
    folder.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = folder / f"response_{timestamp}.txt"
    with open(filename, "w") as f:
        f.write(prompt)
        f.write("\n\n")
        f.write(response)

    try:
        as_json = json.loads(response)
        filename = folder / f"response_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(as_json, f, indent=4)
    except:
        pass


def get_json_markup(data):
    return dcc.Markdown(f"```json\n{json.dumps(data, indent=4)}\n```", className='json-display')


def get_version():
    import importlib.metadata
    try:
        return importlib.metadata.version('komodo-sdk')
    except importlib.metadata.PackageNotFoundError:
        return "0.0.0." + str(datetime.now().strftime('%Y%m%d'))


def load_response_list(agent_shortcode):
    appliance = get_appliance()
    folder = appliance.config.local() / "responses" / agent_shortcode
    responses = []
    for file in folder.glob("*.txt"):
        with open(file, "r") as f:
            prompt = f.readline().strip()
            response = f.read().strip()
            responses.append({"prompt": prompt, "response": response})
    return responses


def save_user_preferences(preferences):
    appliance = get_appliance()
    filename = appliance.config.local() / "preferences.json"
    with open(filename, "w") as f:
        json.dump(preferences, f, indent=4)


def load_user_preferences():
    appliance = get_appliance()
    filename = appliance.config.local() / "preferences.json"
    if filename.exists():
        with open(filename, "r") as f:
            return json.load(f)
    return {}
