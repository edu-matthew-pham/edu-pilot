from edu.agents.base import EduAgent
from core.agents.response import AgentResponse, ResponseType
from core.agents.convo import AgentConvo
from core.log import get_logger
import os
from typing import List

logger = get_logger(__name__)

class Tutor(EduAgent):
    agent_type = "tutor"
    display_name = "Tutor"

    async def run(self) -> AgentResponse:
        activity_plan = self.current_state.specification.activity_plan
        if not activity_plan:
            return AgentResponse.error(self, "No activity plan found")

        activities = self.parse_activity_plan(activity_plan)
        for index, activity in enumerate(activities, start=1):
            await self.run_activity(activity, index)

        return AgentResponse.done(self)

    def parse_activity_plan(self, activity_plan: str) -> list:
        # Parse the activity plan string into a list of activities
        # This is a simple implementation and might need to be adjusted based on your activity plan format
        activities = []
        current_activity = {}
        for line in activity_plan.split('\n'):
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                if current_activity:
                    activities.append(current_activity)
                current_activity = {'step': line.strip()}
            elif 'Title:' in line:
                current_activity['title'] = line.split('Title:')[1].strip()
            elif 'Activity:' in line:
                current_activity['description'] = line.split('Activity:')[1].strip()
        if current_activity:
            activities.append(current_activity)
        return activities

    async def run_activity(self, activity: dict, index: int) -> None:
        is_programming = self.state_manager.get_is_programming()
        logger.info(f"Running activity: {activity['title']}")
        await self.send_message(f"Let's start the activity: {activity['title']}")
        await self.send_message(activity['description'])
        
        # Create a new file for the activity
        await self.create_activity_file(activity, index)
        
        # Ask for prediction
        if is_programming:
            question = "What do you think will happen when this code is run? Please explain your thinking.\nOr type AI to invoke AI research assistance."
        else:
            question = "Enter your response to the activity.\nOr type AI to invoke AI research assistance."
        
        while True:
            response = await self.ask_question(question)
            
            if response.text.strip().lower() == "ai":
                research_response = await self.handle_student_query(activity)
                await self.send_message(research_response)
                continue
            
            # Analyze the prediction
            analysis = await self.analyze_prediction(activity, response.text, is_programming)
            
            # Present the analysis to the student
            await self.send_message("Here's an analysis of your prediction:")
            await self.send_message(analysis)
            break

        # Ask follow-up questions and analyze responses
        await self.ask_and_analyze_follow_up_questions(analysis)

    async def ask_and_analyze_follow_up_questions(self, analysis: str) -> None:
        questions = self.extract_follow_up_questions(analysis)
        for question in questions:
            answer = await self.ask_question(question)
            
            # Analyze the response to the follow-up question
            response_analysis = await self.analyze_follow_up_response(question, answer.text)
            
            # Present the analysis of the follow-up response
            await self.send_message("Here's an analysis of your response:")
            await self.send_message(response_analysis)

    async def analyze_follow_up_response(self, question: str, response: str) -> str:
        llm = self.get_llm()
        convo = AgentConvo(self).template(
            "analyze_follow_up_response",
            question=question,
            response=response
        )
        
        analysis = await llm(convo)
        return analysis

    async def create_activity_file(self, activity: dict, index: int) -> None:
        is_programming = self.state_manager.get_is_programming()
        file_name = f"activity_{index}.py" if is_programming else f"activity_{index}.txt"
        
        new_content = await self.generate_new_content(activity, index)
        
        vfs = self.state_manager.file_system
        vfs.save(file_name, new_content)
        
        await self.send_message(f"I've created/updated the file '{file_name}' for this activity. Here's the content:")
        await self.send_message(f"```\n{new_content}\n```")
        
    async def generate_new_content(self, activity: dict, index: int) -> str:
        is_programming = self.state_manager.get_is_programming()
        template_name = "generate_content" if is_programming else "generate_general_content"
        topic = self.current_state.specification.description
        
        llm = self.get_llm()
        convo = AgentConvo(self).template(
            template_name,
            activity=activity,
            index=index,
            topic=topic
        )
        
        response = await llm(convo)
    
        new_content = self.extract_content(response, is_programming)
    
        return new_content

    def extract_content(self, response: str, is_programming: bool) -> str:
        if is_programming:
            start = response.find("```python")
            end = response.rfind("```")
            if start != -1 and end != -1:
                return response[start+9:end].strip()
        return response.strip()

    async def analyze_prediction(self, activity: dict, prediction: str, is_programming: bool) -> str:
        llm = self.get_llm()
        template_name = "analyze_prediction" if is_programming else "analyze_general_prediction"
        
        convo = AgentConvo(self).template(
            template_name,
            activity=activity,
            prediction=prediction
        )
        
        response = await llm(convo)
        return response

    async def ask_follow_up_questions(self, analysis: str) -> None:
        questions = self.extract_follow_up_questions(analysis)
        for question in questions:
            answer = await self.ask_question(question)
            # You can process or store the answer here if needed

    def extract_follow_up_questions(self, analysis: str) -> List[str]:
        questions = []
        follow_up_section = analysis.split("Follow-up questions:")[-1]
        for line in follow_up_section.split("\n"):
            if line.strip().startswith(("1.", "2.")):
                questions.append(line.strip()[2:].strip())
        return questions

    def format_list(self, items: List[str]) -> str:
        return "\n".join(f"- {item}" for item in items)
    
    async def handle_student_query(self, activity: dict) -> AgentResponse:
        query = await self.ask_question("Please enter your query for AI research assistance.")
        
        # Add the 'await' keyword here
        if await self.is_valid_research_query(query, activity):
            context = self.get_current_lesson_context()

            self.current_state.query = query
            self.current_state.context = context
            research_response = await self.filter_research_response(query, activity)
            
            
            
            return f"Based on AI research: {research_response}"
        else:
            return "I'm sorry, but I can't use AI to research that query. Let's focus on your own understanding."

    async def is_valid_research_query(self, query: str, activity: dict) -> bool:
        # Implement validation logic here
        is_programming = self.state_manager.get_is_programming()
        template_name = "is_valid_research_query" if is_programming else "is_valid_research_query"
        topic = self.current_state.specification.description
        
        llm = self.get_llm()
        convo = AgentConvo(self).template(
            template_name,
            activity=activity,
            topic=topic,
            query=query
        )
        
        await self.send_message(f"Checking if query is valid for research: {query}")
        
        response = await llm(convo)
        
        await self.send_message(f"Response: {response}")

        # Check if the response contains "Response: No"
        if "Response: No" in response:
            await self.send_message(f"The response is not valid for research.")
            return False
        
        return True

    def get_current_lesson_context(self) -> str:
        # Retrieve current lesson context
        pass

    async def filter_research_response(self, query: str, activity: dict) -> str:
        # Implement filtering logic here
        llm = self.get_llm()
        topic = self.current_state.specification.description
        convo = AgentConvo(self).template(
            'filter_research_query',
            activity=activity,
            query=query,
            topic=topic
        )
        
        response = await llm(convo)
        return response