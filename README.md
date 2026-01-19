# PLAYWRIGHT FIXED PROGRAM AND AI API WITH PLAYWRIGHT MCP AND {AI model here}

 ---

## Fixed Google Form Auto Filler with Playwright

A Python automation script that dynamically fills out a Google Form based on the visible question labels and submits the responses.  
Supports **short answer** and **multiple choice** questions, with error handling.

### Requirements

- Python 3.8+
- [Playwright](https://playwright.dev/python/)

Install dependencies:

pip install playwright
playwright install

  ---

## AI-INTEGRATED WEB TASK AUTOMATION TOOL WITH AI AND PLAYWRIGHT MCP

Start up playwright MCP

npx @playwright/mcp@latest --port 8931

===

Run api

uvicorn api:app

Request Format:
{
"api_key": YOUR_API_KEY,
"task": YOUR_TASK
}

===

Or run client.py to run in main rather than API

python client.py


The tool will attempt to solve your task through a prompt and return its results as steps it took, or as an error if there was an error with completing the task.

