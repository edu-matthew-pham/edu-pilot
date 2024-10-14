from edu.agents.base import EduAgent
from core.agents.response import AgentResponse, ResponseType
from edu.projects.python_turtle import PythonTurtleTemplate, PythonTurtleOptions
from core.log import get_logger

import logging

logger = get_logger(__name__)

class ProjectStarter(EduAgent):
    agent_type = "project_starter"
    display_name = "Project Starter"

    def __init__(self, state_manager, ui, process_manager):
        super().__init__(state_manager, ui)
        self.process_manager = process_manager

    async def run(self) -> AgentResponse:
        await self.send_message("Starting the project setup process...")
        
        await self.send_message("Creating a Python Turtle project for our activities.")

        await self.send_message("Creating initial Python files...")
        await self.create_initial_files()

        await self.send_message("Project setup complete. Ready for activities!")
        
        return AgentResponse(self, ResponseType.DONE)

    async def create_initial_files(self):
        vfs = self.state_manager.file_system
        
        await self.send_message("Creating main.py with basic Turtle setup...")
        main_py_content = """
import turtle

screen = turtle.Screen()
t = turtle.Turtle()

# Your turtle commands here

screen.exitonclick()
"""
        vfs.save("main.py", main_py_content)
        
        await self.send_message("Creating README.md with project instructions...")
        readme_content = """
# Python Turtle Learning Project

This project is set up to help you learn Python programming using the Turtle graphics library.

## Getting Started

1. Activate your virtual environment
2. Run `python main.py` to see the turtle in action
3. Modify `main.py` to create your own turtle graphics!

Happy coding!
"""
        vfs.save("README.md", readme_content)
        
        await self.send_message("Initial files created in the workspace.")