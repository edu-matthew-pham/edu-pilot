from edu.agents.base import BaseAgent
from edu.agents.response import AgentResponse, ResponseType
import logging

log = logging.getLogger(__name__)

class HumanInput(BaseAgent):
    agent_type = "human-input"
    display_name = "Human Input"

    async def run(self) -> AgentResponse:
        # This method should now handle other human input scenarios, not asking for the topic
        # You might want to remove or modify this method depending on your needs
        pass

    async def human_intervention(self, step) -> AgentResponse:
        if step is None:
            return await self.get_topic()
        
        description = step.get("human_intervention_description")
        if description is None:
            return AgentResponse.error(self, "No human intervention description provided")
        
        await self.ask_question(
            f"I need human intervention: {description}",
            buttons={"continue": "Continue"},
            default="continue",
            buttons_only=True,
        )
        self.next_state.complete_step()
        return AgentResponse.done(self)

    async def input_required(self, files: list[dict]) -> AgentResponse:
        for item in files:
            file = item["file"]
            line = item["line"]

            # FIXME: this is an ugly hack, we shouldn't need to know how to get to VFS and
            # anyways the full path is only available for local vfs, so this is doubly wrong;
            # instead, we should just send the relative path to the extension and it should
            # figure out where its local files are and how to open it.
            full_path = self.state_manager.file_system.get_full_path(file)

            await self.send_message(f"Input required on {file}:{line}")
            await self.ui.open_editor(full_path, line)
            await self.ask_question(
                f"Please open {file} and modify line {line} according to the instructions.",
                buttons={"continue": "Continue"},
                default="continue",
                buttons_only=True,
            )
        return AgentResponse.done(self)

    async def get_topic(self) -> AgentResponse:
        response = await self.ask_question(
            "What topic would you like to learn about?",
            allow_empty=False,
        )
        if response.cancelled:
            return AgentResponse.error(self, "No topic provided")

        topic = response.text.strip()
        self.next_state.specification = self.current_state.specification.clone()
        self.next_state.specification.description = topic
        print(f"Topic stored: {topic}")  # Add this line for debugging
        return AgentResponse.done(self)
