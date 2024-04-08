from komodo.framework.komodo_tool import KomodoTool


class AgentAsTool(KomodoTool):

    def __init__(self, agent, run_agent_as_tool):
        super().__init__(shortcode=agent.shortcode,
                         name=agent.name + " (Tool Mode)",
                         definition=self.definition(agent.shortcode, agent.purpose),
                         action=lambda args, runtime: run_agent_as_tool(agent, args, runtime))

    def definition(self, shortcode, purpose):
        return {
            "type": "function",
            "function": {
                "name": shortcode,
                "description": f'The tool is an AI agent whose purpose is: {purpose}.',
                "parameters": {
                    "type": "object",
                    "properties": {
                        "system": {
                            "type": "string",
                            "description": "Instructions to the agent. You can use it to provide context, parameters, hints and suggestions."
                        },
                        "user": {
                            "type": "string",
                            "description": "The prompt to be processed by the agent."
                        },
                    },
                    "required": ["system", "user"],
                    "notes": "Do not provide any other parameters. The agent will not understand them."
                }
            }
        }
