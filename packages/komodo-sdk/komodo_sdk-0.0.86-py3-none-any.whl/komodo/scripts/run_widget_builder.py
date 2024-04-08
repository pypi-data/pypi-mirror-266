from komodo.core.agents.widget_builder_agent import WidgetBuilderAgent
from komodo.models.framework.agent_runner import AgentRunner


def sample_text_widget():
    agent = WidgetBuilderAgent(purpose="Explain the Q3 regression summary", widget_type="text")
    agent.prompt = "Provide a sample result for display purposes"
    runner = AgentRunner(agent)
    response = runner.run(agent.prompt)
    print(response.text)


def sample_chart_widget():
    agent = WidgetBuilderAgent(purpose="Explain the Q3 regression summary", widget_type="chart")
    agent.prompt = "Provide a sample result for display purposes"
    runner = AgentRunner(agent)
    response = runner.run(agent.prompt)
    print(response.text)


def sample_table_widget():
    agent = WidgetBuilderAgent(purpose="Explain the Q3 regression summary", widget_type="table")
    agent.prompt = "Provide a sample result for display purposes"
    runner = AgentRunner(agent)
    response = runner.run(agent.prompt)
    print(response.text)


def sample_overlay_widget():
    agent = WidgetBuilderAgent(purpose="Explain the Q3 regression summary", widget_type="text")
    agent.prompt = "Provide a sample result for display purposes"
    runner = AgentRunner(agent)
    response = runner.run(agent.prompt)
    print(response.text)

    agent.overlays.append("translate to Spanish")
    response = runner.run(agent.prompt)
    print(response.text)


if __name__ == "__main__":
    # sample_text_widget()
    sample_chart_widget()
    sample_table_widget()
    # sample_overlay_widget()
