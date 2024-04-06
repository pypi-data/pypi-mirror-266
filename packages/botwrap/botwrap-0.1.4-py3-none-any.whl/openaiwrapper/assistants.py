##Path C:\Users\jamig\OneDrive\Desktop\botwrap\openaiwrapper\assistants.py

import logging

class AssistantManager:
    def __init__(self, api_client, thread_manager=None, message_manager=None):
        self.api_client = api_client
        self.thread_manager = thread_manager
        self.message_manager = message_manager
        self.logger = logging.getLogger(__name__)

    async def _validate_tools_config(self, tools):
        if tools is not None and not all(isinstance(tool, dict) for tool in tools):
            raise ValueError("Tools configuration must be a list of dictionaries.")

    async def create(self, name, instructions, model, tools=None, **kwargs):
        """Creates a new Assistant asynchronously."""
        await self._validate_tools_config(tools)
        data = {
            "name": name,
            "instructions": instructions,
            "model": model,
            "tools": tools or [],
            **kwargs
        }
        self.logger.info(f"Creating new assistant with name: {name}")
        return await self.api_client.make_api_call("assistants", method="POST", data=data)

    async def start_conversation(self, assistant_id, initial_message=None):
        if not self.thread_manager or not self.message_manager:
            raise NotImplementedError("ThreadManager and Message Manager must be initialized.")

        thread_response = await self.thread_manager.create()
        thread_id = thread_response.get('id')
        if initial_message:
            await self.message_manager.create(thread_id, initial_message, role="user")
        return thread_response

    async def create_from_template(self, template_name, **overrides):
        templates = self._load_templates()
        if template_name not in templates:
            raise ValueError(f"Template '{template_name}' not found.")

        template_config = templates[template_name]
        template_config.update(overrides)
        return await self.create(**template_config)

    def _load_templates(self):
        templates = {
            "basic_chat": {
                "name": "Basic Chat Assistant",
                "instructions": "You are a friendly chatbot.",
                "model": "gpt-3.5-turbo",
                "tools": [],
            }
        }
        return templates

    async def retrieve(self, assistant_id):
        self.logger.info(f"Retrieving assistant with ID: {assistant_id}")
        return await self.api_client.make_api_call(f"assistants/{assistant_id}", method="GET")

    async def update(self, assistant_id, **kwargs):
        if 'tools' in kwargs:
            await self._validate_tools_config(kwargs['tools'])
        self.logger.info(f"Updating assistant with ID: {assistant_id}")
        return await self.api_client.make_api_call(f"assistants/{assistant_id}", method="PATCH", data=kwargs)

    async def delete(self, assistant_id):
        self.logger.info(f"Deleting assistant with ID: {assistant_id}")
        return await self.api_client.make_api_call(f"assistants/{assistant_id}", method="DELETE")

    async def list(self, **kwargs):
        self.logger.info("Listing assistants")
        return await self.api_client.make_api_call("assistants", method="GET", params=kwargs)
