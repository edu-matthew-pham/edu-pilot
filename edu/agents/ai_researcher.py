from edu.agents.base import BaseAgent, AgentResponse

class AIResearcher(BaseAgent):
    agent_type = "ai-researcher"
    display_name = "AI Researcher"

    async def run(self) -> AgentResponse:
        # This method will be called by the Tutor agent
        query = self.current_state.query
        context = self.current_state.context
        return await self.research(query, context)

    async def research(self, query: str, context: str) -> AgentResponse:
        # Implement the AI research logic here
        # This could involve calling an external API or using a local model
        response = f"Research results for query: {query}\nContext: {context}\n"
        # Add actual research logic here
        return AgentResponse(content=response)