An agent is a program that can perceive its environment, make decisions, and take actions to achieve a goal — on its own, without you manually doing each step.

Tools are how an agent reaches out and does things in the real world. Without tools, an agent is just thinking — it can reason and generate text, but it's trapped inside its own knowledge. Tools give it hands.
When the agent calls a tool, it's essentially saying, "I need something I can't figure out on my own — let me go get it." The tool runs, returns data, and the agent uses that data to continue working toward its goal.

Let's talk about a news agent.

1. **Collection** — Claude uses the web search tool to go out and find today's AI news. This is the "agentic" part where the model decides what to search for and reads the results.
2. **Filtering** — Claude reads the raw news and picks the single most notable event from three specific categories. This is still AI-driven but heavily constrained by the prompt — it's making a judgment call but within tight rules.
3. **Summarising into a specific format** — Claude outputs a structured JSON object with fixed fields (event, description, source, date). The code then strips any formatting noise and validates that it parses correctly.
4. **Deterministic delivery via GitHub Action** — No AI involved here at all. It's pure automation: run the script, check if the file changed, commit to a new branch, and open a PR. You stay in the loop by reviewing the PR before anything merges.
The clean insight here is that only steps 1 and 2 involve AI judgment — everything else is just reliable, predictable code doing mechanical work. That's actually good agent design: use AI where you need reasoning, use deterministic code everywhere else.
