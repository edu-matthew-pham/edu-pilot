from typing import Optional

from edu.agents.base import BaseAgent
from edu.agents.error_handler import ErrorHandler
from edu.agents.activity_planner import ActivityPlanner
from edu.agents.tutor import Tutor
from edu.agents.project_starter import ProjectStarter
from edu.agents.response import AgentResponse, ResponseType
from core.log import get_logger
import logging

log = get_logger(__name__)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Orchestrator(BaseAgent):
    """
    Simplified Orchestrator agent that runs a basic tutoring session.
    """

    agent_type = "orchestrator"
    display_name = "Orchestrator"

    async def run(self) -> bool:
        if not self.current_state.specification.description:
            topic_info = await self.get_topic_info()
            await self.state_manager.set_topic_info(topic_info['topic'], topic_info['is_programming'])
            self.next_state.specification = self.current_state.specification.clone()

        # Create project before activity planning
        project_starter = ProjectStarter(self.state_manager, self.ui, self.process_manager)
        project_response = await project_starter.run()
        
        # Debug logging
        logger.debug(f"Project starter response type: {project_response.type}")
        
        if project_response.type == ResponseType.ERROR:
            logger.error(f"Project creation failed")
            return False

        while True:
            agent = self.create_agent()
            logger.debug(f"Created agent: {type(agent).__name__}")
            response = await agent.run()
            logger.debug(f"Agent response type: {response.type}")

            if isinstance(agent, Tutor) and response.type == ResponseType.DONE:
                return True
            elif response.type in [ResponseType.ERROR, ResponseType.EXIT]:
                return False

        return True

    async def get_topic_info(self) -> dict:
        topic_type = await self.ui.ask_question(
            "Would you like to learn about a programming topic or a general topic?",
            buttons={"programming": "Programming", "general": "General"},
            default="programming",
            buttons_only=True,
        )

        topic = await self.ui.ask_question(
            f"Enter the {topic_type.button} topic you would like to learn about:",
        )
        if topic.cancelled:
            raise ValueError("No topic provided")
        
        return {
            'topic': topic.text.strip(),
            'is_programming': topic_type.button == "programming"
        }

    def create_agent(self) -> BaseAgent:
        if not self.current_state.specification.activity_plan:
            logger.debug("Creating ActivityPlanner agent")
            return ActivityPlanner(self.state_manager, self.ui)
        else:
            logger.debug("Creating Tutor")
            return Tutor(self.state_manager, self.ui)

    async def execute_activity_plan(self):
        activity_plan = self.current_state.specification.activity_plan
        activities = activity_plan.strip().split('\n')[2:]  # Skip the title and blank line
        
        for activity in activities:
            await self.send_message(f"Now we'll: {activity}")
            # Here you would implement the logic for each activity in the tutoring session
            # For now, we'll just ask a question related to the activity
            await self.ask_question(f"Let's work on this: {activity}")

    async def ask_question(self, topic: str):
        """
        Ask a question related to the current activity and evaluate the user's answer.
        """
        question = f"Regarding {topic}, can you explain your current understanding or approach?"
        
        user_input = await self.ui.ask_question(question)
        
        if user_input.cancelled:
            log.info("User cancelled the question")
            return
        
        user_answer = user_input.text.strip()
        
        # Here, you would typically use an LLM to evaluate the answer and provide tailored feedback
        # For simplicity, we'll just provide a generic response
        await self.ui.send_message("Thank you for your response. Let's dive deeper into this topic.")
        
        # In a real tutoring session, you'd want to provide more specific feedback and follow-up questions here

    async def run_lesson(self) -> bool:
        # Implement this method to run the actual lesson based on the activity plan
        logger.info("Running lesson (not implemented yet)")
        return True

    def create_lesson_agent(self) -> BaseAgent:
        # Implement this method to create the appropriate agent for conducting the lesson
        raise NotImplementedError("Lesson agent not implemented yet")