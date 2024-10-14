
from core.state.state_manager import StateManager

class EduStateManager(StateManager):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_programming = False  # Add this line
        self.activity_plan = None
        self.topic = None
        
    async def set_topic_info(self, topic: str, is_programming: bool):
        self.topic = topic
        self.is_programming = is_programming

    def get_is_programming(self) -> bool:
        return self.is_programming

    def set_activity_plan(self, activity_plan: str):
        self.activity_plan = activity_plan

    def get_activity_plan(self) -> str:
        return self.activity_plan

