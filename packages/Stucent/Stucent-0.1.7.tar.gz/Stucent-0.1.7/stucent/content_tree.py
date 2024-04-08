import uuid
import jinja2
from typing import Dict, Optional, List


class Node:
    def __init__(
        self,
        title: str,
        type: str,
        description: str,
        node_id: Optional[str] = None,
        prompt_template: str = "",
        prompt_arguments: Dict = {},
        schema: Dict = {},
        **kwargs
    ):
        self.node_id = node_id if node_id else str(uuid.uuid4())
        self.title = title
        self.type = type
        self.description = description
        self.children = []
        self.prompt_template = prompt_template
        self.schema = schema
        self.metadata = {}

    def render_prompt(self) -> str:
        template = jinja2.Template(self.prompt_template) 
        return template.render(node=self)

    def call_llm(self, messages: List[str], **kwargs):
        # Placeholder for LLM call. Assume this function is implemented elsewhere.
        # This function should return a structured response based on `self.schema`.
        pass

    def parse_llm_response(self, response):
        # Placeholder for response parsing logic.
        # This should update the current node and create children nodes as needed.
        pass

    def run(self):
        # Generate the prompt from the template
        prompt = self.render_prompt()

        # Call the LLM with the generated prompt and any additional parameters
        response = self.call_llm([prompt], schema=self.schema)

        # Parse the LLM's response to update the current node's metadata and create child nodes
        self.parse_llm_response(response)

    def add_child(self, child):
        self.children.append(child)


class Activity(Node):
    def __init__(self, title: str, description: str, activity_type: str, **kwargs):
        super().__init__(title, "activity", description, **kwargs)
        self.activity_type = activity_type

    def run(self):
        # Custom logic for activities
        super().run()
        # Additional activity-specific operations can be added here


# Example usage:
if __name__ == "__main__":
    # Define a module node
    module_node = Node(
        "Module 1",
        "module",
        "This is the description of Module 1.",
        prompt_template="Generate an overview for {{ node.title }}",
        schema={
            "type": "module",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
            },
        },
    )

    # Define an activity node
    activity_node = Activity("Quiz 1", "This is a quiz activity.", "quiz")

    # Add the activity node as a child of the module node
    module_node.add_child(activity_node)

    # Run the module node to generate content and potentially more child nodes
    module_node.run()
