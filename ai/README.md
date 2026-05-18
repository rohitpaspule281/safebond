# AI Workspace

This directory will contain the research-facing AI assets behind Safebond.

## Planned contents

- `configs/`: model settings, evaluation configs, ablation settings
- `prompts/`: agent prompts and safety templates
- `notebooks/`: exploratory analysis and error analysis

## Recommended modeling choices

- Emotion classification: `j-hartmann/emotion-english-distilroberta-base`
- Sentiment baseline: `cardiffnlp/twitter-roberta-base-sentiment`
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2`
- Optional local generation: Ollama with a compact instruct model

## Research directions

- compare single-agent vs multi-agent response quality
- measure empathy and continuity with and without memory RAG
- evaluate safety override effectiveness on risky prompts
