# AI Cheatsheet

[![Netlify Status](https://api.netlify.com/api/v1/badges/16ba51ea-8715-4701-8119-fc21bcee84c0/deploy-status)](https://app.netlify.com/projects/timeline-agent/deploys)

A curated reference of tools, platforms, courses, papers, and protocols for working with AI and Large Language Models.

## Table of Contents

- [LLM Providers](#llm-providers)
- [Run Locally](#run-locally)
- [Analysis](#analysis)
- [Gateway](#gateway)
- [Courses](#courses)
- [Books](#books)
- [Blog](#blog)
- [Papers](#papers)
- [Protocols](#protocols)
- [Agents](#agents)
- [Tool Calling](#tool-calling)
- [Tools](#tools)
- [Others](#others)

## LLM Providers

| Provider                                   |
| ------------------------------------------ |
| [OpenAI](https://openai.com)               |
| [Anthropic](https://anthropic.com)         |
| [Google Gemini](https://gemini.google.com) |
| [Mistral AI](https://mistral.ai)           |
| [DeepSeek](https://www.deepseek.com)       |

## Run Locally

| Tool                                                   |
| ------------------------------------------------------ |
| [LM Studio](https://lmstudio.ai)                       |
| [Open WebUI](https://github.com/open-webui/open-webui) |
| [Ollama](https://ollama.com)                           |

## Analysis

| Tool                                                 |
| ---------------------------------------------------- |
| [Artificial Analysis](https://artificialanalysis.ai) |
| [Arena AI](https://arena.ai)                         |

## Gateway

| Platform                                                                     |
| ---------------------------------------------------------------------------- |
| [OpenRouter](https://openrouter.ai)                                          |
| [LiteLLM](https://www.litellm.ai)                                            |
| [Kong](https://konghq.com)                                                   |
| [Portkey](https://portkey.ai)                                                |
| [AWS Bedrock](https://aws.amazon.com/bedrock)                                |
| [Google Generative AI Studio](https://cloud.google.com/generative-ai-studio) |

## Courses

| Course                                                                                              | Provider        |
| --------------------------------------------------------------------------------------------------- | --------------- |
| [Anthropic Courses](https://anthropic.skilljar.com/)                                                | Anthropic       |
| [AI Learning Path](https://skillsbuild.org/adult-learners/explore-learning/artificial-intelligence) | IBM SkillsBuild |
| [AWS Certified AI Practitioner](https://aws.amazon.com/certification/certified-ai-practitioner/)    | AWS             |
| [Training for AI Engineers](https://learn.microsoft.com/en-us/training/career-paths/ai-engineer)    | Microsoft       |
| [The AI Engineer Path](https://scrimba.com/the-ai-engineer-path-c02v)                               | Scrimba         |
| [AI & ML Catalog](https://www.databricks.com/training/catalog?search=ai&costs=free)                 | Databricks      |
| [Machine Learning Crash Course](https://developers.google.com/machine-learning/crash-course)        | Google          |

## Books

| Title                                                                                                                                                                                                                                                       |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [AI Engineering Book](https://github.com/chiphuyen/aie-book)                                                                                                                                                                                                |
| [HBR's 10 Must Reads on AI](https://store.hbr.org/product/hbr-s-10-must-reads-on-ai-with-bonus-article-how-to-win-with-machine-learning-by-ajay-agrawal-joshua-gans-and-avi-goldfarb/10666?srsltid=AfmBOoobOoS7EnF0zyGSOZrQGW1rtTAWDgbGlGZR9UvT6BgA66yWvkH) |

## Blog

| Title                                                                                                                                 |
| ------------------------------------------------------------------------------------------------------------------------------------- |
| [Introduction to Large Language Models: Everything You Need to Know for 2025](https://www.lakera.ai/blog/large-language-models-guide) |

## Papers

| Title                                                                                                               |
| ------------------------------------------------------------------------------------------------------------------- |
| [Artificial Hivemind: The Open-Ended Homogeneity of Language Models (and Beyond)](https://arxiv.org/abs/2510.22954) |
| [The Illusion of Thinking: Strengths and Limitations of Reasoning Models](https://arxiv.org/abs/2506.06941)         |
| [Agents of Chaos](https://arxiv.org/abs/2602.20021)                                                                 |
| [Does Prompt Formatting Have Any Impact on LLM Performance?](https://arxiv.org/abs/2411.10541)                      |
| [Helpful Agent Meets Deceptive Judge: Vulnerabilities in Agentic Workflows](https://arxiv.org/abs/2506.03332)       |
| [Toolformer: Language Models Can Teach Themselves to Use Tools](https://arxiv.org/abs/2302.04761)                   |
| [Can LLMs Ask Good Questions?](https://arxiv.org/abs/2501.03491)                                                    |
| [Toolshed: Scale Tool-Equipped Agents with Advanced RAG-Tool Fusion](https://arxiv.org/abs/2410.14594)              |

## Protocols

Agent interoperability and communication standards.

| Protocol                     | Description                                                    | Link                                                                                          |
| ---------------------------- | -------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Agent2Agent (A2A)            | Google's protocol for agent interoperability                   | [Blog](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)         |
| Model Context Protocol (MCP) | Open protocol for model-tool context (introduced by Anthropic) | [Docs](https://modelcontextprotocol.io/docs/getting-started/intro)                            |
| Agent Network Protocol (ANP) | Open protocol for agent-to-agent networking                    | [Site](https://www.agent-network-protocol.com/)                                               |
| AG-UI Protocol               | Agent–User interaction protocol                                | [Docs](https://docs.ag-ui.com/introduction#the-agent%E2%80%93user-interaction-ag-ui-protocol) |
| Agora Protocol               | Decentralized agent communication protocol                     | [Site](https://agoraprotocol.org/)                                                            |
| LMOS Protocol                | Eclipse LMOS agent protocol                                    | [Docs](https://eclipse.dev/lmos/docs/lmos_protocol/introduction/)                             |

## Agents

### Guides

| Title                                | Link                                                                                                          |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| A Practical Guide to Building Agents | [OpenAI (PDF)](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) |
| Building Effective Agents            | [Anthropic](https://www.anthropic.com/engineering/building-effective-agents)                                  |
| How to Build an Agent                | [LangChain](https://blog.langchain.com/how-to-build-an-agent/)                                                |

| Type     | Platform                                                                                              |
| -------- | ----------------------------------------------------------------------------------------------------- |
| No Code  | [n8n](https://n8n.io)                                                                                 |
| Low Code | [Azure AI Foundry Agent Service](https://azure.microsoft.com/en-us/products/ai-foundry/agent-service) |
| Low Code | [Google Agent Builder](https://cloud.google.com/products/agent-builder)                               |
| Code     | [CrewAI](https://crewai.com)                                                                          |
| Code     | [LangGraph](https://www.langchain.com/langgraph)                                                      |
| Code     | [Pi.dev](https://pi.dev)                                                                              |

## Tool Calling

| Resource                                                                     |
| ---------------------------------------------------------------------------- |
| [Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use) |

## Tools

| Tool                                                 |
| ---------------------------------------------------- |
| [Google Stitch](https://stitch.withgoogle.com)       |
| [Agent Zero](https://github.com/agent0ai/agent-zero) |
| [Remotion Prompts](https://www.remotion.dev/prompts) |
| [Pencil](https://www.pencil.dev)                     |
| [Quiver AI](https://quiver.ai)                       |
| [AnythingLLM](https://anythingllm.com)               |
| [Recall AI](https://app.getrecall.ai)                |
| [AgenticSeek](https://github.com/Fosowl/agenticSeek) |
| [OpenClaw](https://openclaw.ai/)                     |

## Memory

https://github.com/milla-jovovich/mempalace

## Others

| Resource                             |
| ------------------------------------ |
| [Moltbook](https://www.moltbook.com) |
