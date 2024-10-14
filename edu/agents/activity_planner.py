from edu.agents.base import EduAgent
from core.agents.convo import AgentConvo
from core.agents.response import AgentResponse
from core.llm.parser import StringParser
from core.log import get_logger

ACTIVITY_PLANNER_AGENT_NAME = "activity_planner"

logger = get_logger(__name__)

class ActivityPlanner(EduAgent):
    agent_type = "activity-planner"
    display_name = "Activity Planner"

    async def run(self) -> AgentResponse:
        topic = self.current_state.specification.description
        is_programming = self.state_manager.get_is_programming()
        logger.debug(f"Creating activity plan for topic: {topic}, Is Programming: {is_programming}")
        return await self.create_activity_plan(topic, is_programming)

    async def create_activity_plan(self, topic: str, is_programming: bool) -> AgentResponse:
        await self.send_message(f"Planning self-paced activities for: {topic}")

        template_name = "create_activity_plan" if is_programming else "create_general_activity_plan"
        
        llm = self.get_llm(ACTIVITY_PLANNER_AGENT_NAME, stream_output=True)
        convo = AgentConvo(self).template(template_name, topic=topic)
        logger.debug(f"Conversation template created with topic: {topic}, Template: {template_name}")
        
        activity_plan: str = await llm(convo, temperature=0, parser=StringParser())
        logger.debug(f"Activity plan generated: {activity_plan[:100]}...")  # Log first 100 chars

        if "Please provide the specific topic" in activity_plan:
            logger.error(f"LLM failed to use the provided topic: {topic}")
            return AgentResponse.error(self, f"Failed to create activity plan for topic: {topic}")

        self.next_state.specification = self.current_state.specification.clone()
        self.next_state.specification.activity_plan = activity_plan
        
        await self.send_message("Activity plan created. Moving to the next step.")
        return AgentResponse.done(self)
