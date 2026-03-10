# Model selection for this project

Use **stable model IDs** for the main results table whenever you can.  
Use **web/manual labels** only when the budget or access pattern forces manual testing.

## Main paper trio

### 1) OpenAI
Use `gpt-5.1` for the main GPT-family comparison.

Why:
- It is described by OpenAI as the flagship model for coding and agentic tasks.
- It supports 400,000 context and 128,000 max output tokens.
- It is more reproducible than a browser-only ChatGPT label.

### 2) Google
Use `gemini-2.5-pro` for the main Gemini comparison.

Why:
- It is Google’s stable advanced model for complex tasks, reasoning, and coding.
- It supports long-context workflows and PDFs.
- It supports structured outputs and search grounding.

### 3) DeepSeek
Use `deepseek-reasoner` for the main DeepSeek comparison.

Why:
- It is the reasoning mode in the current DeepSeek API lineup.
- It maps to the V3.2 reasoning model in the API docs.
- It is the cleanest DeepSeek choice for multi-turn SQL revision.

## Budget / ablation trio

- OpenAI: `gpt-5-mini`
- Google: `gemini-2.5-flash-lite`
- DeepSeek: `deepseek-chat`

Use these when you need:
- more replicates,
- faster sweeps,
- lower cost per trajectory.

## What to avoid in the main paper

- Preview models as the primary headline result, unless you freeze the exact version and state clearly that it is preview-only.
- Unlabeled “ChatGPT”, “Gemini”, or “DeepSeek” web runs without recording the visible UI label.
- Treating app/web model names as equivalent to API snapshots when the provider docs warn they are different.

## Logging rule

For every run, record all of:
- provider
- model_id
- model_snapshot (if known)
- reasoning mode
- temperature
- date tested
- whether the run was web/manual or API-based

## Reference links

OpenAI:
- https://developers.openai.com/api/docs/models/gpt-5.1
- https://developers.openai.com/api/docs/models/gpt-5-mini
- https://developers.openai.com/api/docs/models/gpt-5.1-chat-latest

Google:
- https://ai.google.dev/gemini-api/docs/models/gemini-2.5-pro
- https://ai.google.dev/gemini-api/docs/models
- https://ai.google.dev/gemini-api/docs/google-search

DeepSeek:
- https://api-docs.deepseek.com/quick_start/pricing
- https://api-docs.deepseek.com/guides/reasoning_model
- https://api-docs.deepseek.com/api/list-models
