---
name: frontend
description: Instructions on how to call multiple LLMs for frontend work.
agent: agent
---

You are given a product requirement document for an application you have to develop. You must generate 3 seperate versions of the frontend of the app for each llm by calling subagents.

Call Frontend-Engineer-subagent-Gemini.agent.md, Frontend-Engineer-subagent-GPT.agent.md, Frontend-Engineer-subagent-Opus.agent.md in parallel as subagents for seperate versions of the task given below. Each subagent must work in a seperate folder i.e gemini/, opus/, gpt/ 

