from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from phoenix.otel import register

tracer_provider = register(
    project_name="support",
    auto_instrument=True,
)


model = ChatOpenAI(model_name="gpt-4.1", temperature=0.7, use_responses_api=True)

web_search_tool = {"type": "web_search_preview"}
agent = create_agent(model=model, tools=[web_search_tool])

message = {
    "role": "user",
    "content": [{"type": "text", "text": "could you check upcoming events in Madrid?"}],
}

response = agent.invoke({"messages": message})
print(response)
