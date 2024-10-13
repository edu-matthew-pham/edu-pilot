from pydantic import BaseModel
from core.projects.base import BaseProjectTemplate

class PythonTurtleOptions(BaseModel):
    project_name: str
    # Add any other options you want to include for your Python Turtle projects
    # For example:
    # screen_size: tuple = (800, 600)
    # background_color: str = "white"

class PythonTurtleTemplate(BaseProjectTemplate):
    name = "python_turtle"
    path = "python_turtle_template"  # This should match the folder name where your template files are stored
    description = "A template for Python turtle graphics projects"
    options_class = PythonTurtleOptions
    options_description = "Options for Python turtle projects"
    file_descriptions = {
        "main.py": "Main Python file with turtle graphics setup",
        "requirements.txt": "Python dependencies",
        "README.md": "Project documentation"
    }

    async def install_hook(self):
        # Run pip install if there's a requirements.txt
        if await self.state_manager.file_exists("requirements.txt"):
            await self.process_manager.run_command("pip install -r requirements.txt")

    def filter(self, path: str):
        # You can implement custom filtering logic here if needed
        return path