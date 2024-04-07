from komodo.framework.komodo_tool import KomodoTool


class WorkflowAsTool(KomodoTool):

    def __init__(self, workflow, run_workflow_as_tool):
        super().__init__(shortcode=workflow.shortcode,
                         name=workflow.name + " (Tool Mode)",
                         definition=self.definition(workflow.shortcode, workflow.purpose),
                         action=lambda args, runtime: run_workflow_as_tool(workflow, args, runtime))

    def definition(self, shortcode, purpose):
        return {
            "type": "function",
            "function": {
                "name": shortcode,
                "description": f'The tool is an AI workflow whose purpose is: {purpose}.',
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Parameters to the workflow."
                        },
                    },
                    "required": ["command"],
                    "notes": "Do not provide any other parameters. The workflow will not understand them."
                }
            }
        }
