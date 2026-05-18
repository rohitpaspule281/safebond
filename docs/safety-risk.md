# AI Safety and Risk Detection System

## Safety architecture

Safebond uses a hybrid safety stack designed for mental wellness support:

```text
User text
 -> lexical risk scanner
 -> zero-shot crisis classifier
 -> safety scoring and policy engine
 -> escalation decision
 -> draft response moderation
 -> safe fallback or final response
```

This avoids relying on a single brittle detector and makes the system more explainable and auditable.

## Detection layers

### 1. Lexical high-precision rules

The rule layer captures:

- explicit self-harm language
- crisis intent or immediacy
- means or method references
- hopelessness
- severe panic language
- violence cues

This gives strong recall for obvious high-risk cases and supports explanation.

### 2. Transformer-based zero-shot classifier

Model:

- `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli`

Candidate labels:

- self-harm or suicide risk
- acute crisis or imminent danger
- severe emotional distress or panic
- violence or harm to others risk
- request for general emotional support

Why this model:

- NLI-based zero-shot classification is flexible for safety categories that do not map neatly to a single benchmark dataset
- base-size DeBERTa is more realistic for student hardware than very large moderation models
- it provides a research-friendly bridge between rule-based detection and adaptable semantic classification

## Safety scoring

The policy engine computes:

- `self_harm_score`
- `crisis_intent_score`
- `distress_score`
- `violence_score`
- `risk_score`

Final risk levels:

- `low`
- `moderate`
- `high`
- `critical`

Risk is elevated not only by raw model scores, but also by plan/immediacy cues and method references.

## Response moderation pipeline

The moderation stage checks drafted AI replies for:

- harmful instructions
- coercive secrecy
- dependency-forming language
- false therapist claims
- unsupported diagnostic claims
- dismissive minimization

If the draft violates policy:

- low/moderate cases are sanitized when possible
- high/critical cases replace the normal response with a safety fallback

## Escalation workflow

### Low

- allow normal supportive response

### Moderate

- allow supportive response with stronger safety guidance

### High

- suppress normal generated response
- provide strong encouragement to reach trusted human support
- include verified mental health resources

### Critical

- override normal response entirely
- direct the user to emergency help immediately
- surface verified emergency and mental-health crisis resources

## Emergency resource handling

Verified on **May 17, 2026** for India:

- Tele-MANAS: `14416`
- Tele-MANAS toll-free: `1-800-891-4416`
- Emergency Response Support System: `112`

Official sources:

- [MOHFW Tele-MANAS operational guidelines](https://www.mohfw.gov.in/sites/default/files/Operational%20Guidelines%20-%20Tele%20Manas.pdf)
- [Government of India ERSS 112](https://112.gov.in/)

## Middleware design

The system includes a reusable pipeline middleware:

- `SafetyModerationMiddleware`

This is intended to sit between response generation and final delivery, so future multi-agent orchestration can do:

```text
input safety check -> strategy selection -> response generation -> response moderation -> output
```

## Research-oriented strengths

- hybrid symbolic + neural safety architecture
- explainable lexical and zero-shot evidence
- configurable, auditable thresholds
- explicit crisis escalation policy
- output moderation, not just input moderation
- emergency-resource grounding with verified sources
