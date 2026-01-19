import asyncio

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.exceptions import ToolError

from openai import OpenAI

# For testing with an api key
from dotenv import load_dotenv
import os

# convert json formatted strings to dict where appropriate
import json




class LLMPlaywrightAgent:
    """LLM Agent that uses tools from the Playwright MCP in order to complete web tasks given by a user in plaintext"""
    def __init__(self, api_key: str):
        try:
            self.api_key = api_key
            self.llm_client = OpenAI(api_key=api_key)
        # this is probably going to be an empty API Key error
        except Exception as e:
            print(e)
            raise


    async def run(self, task: str):
        """Run the agent to perform a given task.

        Args:
            task: The given task that the user wants to complete.

        Returns:
            result: A step-by-step list of what the LLM did, in JSON-readable format.
        """
        # Start up Streamable HTTP Transport and create LLM response and actions
        print("Running task...")
        try:
            # Connect to Streamable HTTP of MCP to grab tools
            tools = []
            transport = StreamableHttpTransport("http://localhost:8931/mcp")
            async with Client(transport=transport) as client:
                # get the list of available tools from the Playwright MCP
                tools = await client.list_tools()

            tools = [{
                "type": "function",
                    "name": tool.model_dump()["name"],
                    "description": tool.model_dump()["description"],
                    "parameters": {**tool.model_dump()["inputSchema"], "required":tool.model_dump().setdefault("required", [])},

            } for tool in tools]
            tools.append({
                "type": "function",
                "name": "output_results",
                "description": "if requested, output a result for the user after finding",
                "parameters": {"type":"object", "properties": {"output": {"type": "string", "description":"a string that is the requested output"}}, "additionalProperies": False, "required": ["output"]}
            })
            # initialize and create LLM response and keep generating responses until task is done
            done = False
            input_list = [{"role":"user", "content": task}]
            result_msg = None
            while not done:
                response = self.llm_client.responses.create(
                    model="gpt-5",
                    instructions="""You are an intelligent agent with Playwright/MCP tools. For any user task that requires web interaction (avoid malicious or dangerous actions):
1. Obtain the MCP page context (DOM, attributes, visible text).
2. Produce a JSON-structured plan (ordered steps) based on each step of the task with the following format exactly:
    {
    "1": detailed description of step 1, 
    "2": detailed description of step 2, 
    "3": detailed description of step 3,
    ...
    }
3. Use stable selectors from the page context.
4. Execute the appropriate code using playwright tools and the context acquired, and return a final result object.
5. When you have executed all appropriate tools to complete the task, complete the response and let us know when you are done by saying "done".
""",
                    tools=tools,
                    input=input_list,
                )
                # Save function call outputs for subsequent requests
                input_list += response.output
                for item in response.output:
                    # end API calls if done, otherwise, get the structured output to return to user
                    if item.type == "message":
                        if "done" in " ".join([i.text for i in item.content]).lower():
                            done = True
                        result_msg = item.content
                        print(result_msg)
                    elif item.type == "function_call":
                        print(item.name, item.arguments)
                        if item.name == "add_output":
                            add_output(item.arguements["output"])
                        try:
                            tool_call_result = await asyncio.wait_for(_call_mcp_tool(item.name, item.arguments), timeout=60)
                            input_list.append({
                                    "type": "function_call_output",
                                    "call_id": item.call_id,
                                    "output": json.dumps({
                                        "tool_name": item.name,
                                        "data": tool_call_result.content[0].text
                                    })
                                })
                        except ToolError as e:
                            input_list.append({
                                    "type": "function_call_output",
                                    "call_id": item.call_id,
                                    "output": json.dumps({
                                        "tool_name": item.name,
                                        "error": str(e)
                                    })
                                })
                        except asyncio.TimeoutError as e:
                            print("Tool call timed out")
                            raise
            print("Complete!")
            return result_msg
        except Exception as e:
            raise
            
# function to call mcp tool within running the agent
async def _call_mcp_tool(name, args):
        transport = StreamableHttpTransport("http://localhost:8931/mcp")
        async with Client(transport=transport) as client:
            return await client.call_tool(name, json.loads(args))

def add_output(output:str):
    print(output)

async def main():
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    agent = LLMPlaywrightAgent(api_key=API_KEY)
    # await agent.run("Go to https://docs.google.com/forms/d/e/1FAIpQLSch8ezgNkQNILgEruelIzEELdW-hmOxJhi1kgSjVOm74GKk0A/viewform?usp=header and fill in the form with name: LLM2, School: Agent2, and Year: 2")
    await agent.run("Go to Google and give me the base64 encoding of the logo.")


if __name__ == "__main__":
    asyncio.run(main())