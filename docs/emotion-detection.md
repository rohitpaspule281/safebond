# Emotion Detection Module

## Purpose

This module performs emotion-aware inference for Safebond using two Hugging Face transformer models:

- `j-hartmann/emotion-english-distilroberta-base`
- `cardiffnlp/twitter-roberta-base-sentiment`

## Why these models were chosen

### `j-hartmann/emotion-english-distilroberta-base`

- compact enough for student hardware compared with larger encoder models
- strong general-purpose English emotion classification baseline
- transformer encoder architecture is well-suited for short to medium reflective text
- provides robust raw affect labels such as sadness, anger, fear, joy, and neutral

### `cardiffnlp/twitter-roberta-base-sentiment`

- lightweight sentiment backbone for negative/neutral/positive polarity
- complements the emotion classifier by adding stable polarity signals
- useful for confidence calibration and emotional intensity estimation

## Important design note

The target Safebond emotions include `anxiety`, `stress`, `loneliness`, and `burnout`, which do not map one-to-one to standard base emotion labels. Because of that, the module uses a **post-processing wellness taxonomy layer** that combines:

- transformer emotion probabilities
- sentiment probabilities
- lexical cue support
- label-agreement heuristics

This makes the output better aligned with a mental wellness product than a raw benchmark classifier alone.

## Inference flow

1. Normalize incoming text
2. Run emotion classifier
3. Run sentiment classifier
4. Map raw labels into Safebond wellness emotions
5. Compute confidence score and emotional intensity
6. Build explainability payload using:
   - raw model distributions
   - lexical cues
   - clause-level highlighted segments
7. Cache repeated results

## Optimization strategies

- lazy-load transformer models on first use
- keep model instances singleton-scoped inside the process
- prefer GPU automatically when available
- fall back to CPU if CUDA is unavailable or model transfer fails
- cap sequence length to reduce inference cost
- run blocking inference in worker threads so FastAPI’s event loop stays responsive
- cache identical requests with TTL-based memoization
- batch clause scoring for explanation instead of loading extra explainers

## API endpoints

- `POST /api/v1/emotions/analyze`
- `POST /api/v1/emotions/batch-analyze`
- `GET /api/v1/emotions/models`

## Interview talking points

- The module uses **dual-model inference** rather than a single classifier.
- Wellness emotions are derived through **taxonomy mapping**, which is more product-relevant than raw academic labels alone.
- Confidence is not just softmax max-probability; it blends margin, sentiment support, cue support, and label agreement.
- Explainability is implemented with both **distribution-level transparency** and **clause-level evidence extraction**.
- The design is optimized for local or low-cost deployment with CPU fallback and result caching.
