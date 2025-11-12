# Dual-Judge Prompt Optimization

Enhanced prompt optimization using **Minto Pyramid Principle** and **Feynman Scientific Method** for more rigorous evaluation and tighter prompts.

## Key Improvements Over Standard Approach

### 1. **Two Complementary Evaluation Methods**

Instead of a single generic CoT judge, you get TWO specialized judges:

#### **Minto Judge** (Barbara Minto's Pyramid Principle)
- **Philosophy:** Top-down structured thinking
- **Structure:** Main Conclusion → Key Arguments → Supporting Details
- **Evaluates:**
  - Fluency & Clarity (0-10)
  - Relevance to Intent (0-10)
  - Engagement & Impact (0-10)
- **Why it works:** Forces evaluation to start with the "answer" and justify it with logic

#### **Feynman Judge** (Richard Feynman's Scientific Method)
- **Philosophy:** Simplicity, truth, and clarity from first principles
- **Tests:**
  - Simplicity: Can a 12-year-old understand it?
  - Truth & Accuracy: Every claim defensible?
  - Elegance: Simplest way to convey the idea?
- **Why it works:** Eliminates jargon, fluff, and complexity; ensures honest communication

### 2. **"What is Limiting?" Analysis**

Instead of generic "improve this," the system asks:

**CRITICAL QUESTION: What is LIMITING this prompt from achieving excellence?**

Analyzes three categories:
1. **STRUCTURAL LIMITS:** Vague, too complex, missing constraints?
2. **CONTENT LIMITS:** Lacks features, benefits, emotional hooks?
3. **CLARITY LIMITS:** Confusing, ambiguous, unclear language?

### 3. **Rigorous Variant Testing**

Each of the 3 generated variants is tested with **BOTH judges separately**:

```
Variant 1:
  → Minto Judge: 7.5/10
  → Feynman Judge: 8.2/10
  → Combined: 7.85/10

Variant 2:
  → Minto Judge: 8.1/10
  → Feynman Judge: 7.9/10
  → Combined: 8.0/10  ← BEST

Variant 3:
  → Minto Judge: 7.3/10
  → Feynman Judge: 8.0/10
  → Combined: 7.65/10
```

Best variant is selected based on **combined score** (average of both judges).

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  ITERATION LOOP                                             │
│                                                             │
│  1. Generate output from current prompt                    │
│     ↓                                                       │
│                                                             │
│  2. Evaluate with MINTO JUDGE                              │
│     • Pyramid structure analysis                           │
│     • Score: X.X/10                                        │
│     ↓                                                       │
│                                                             │
│  3. Evaluate with FEYNMAN JUDGE                            │
│     • Scientific method analysis                           │
│     • Score: Y.Y/10                                        │
│     ↓                                                       │
│                                                             │
│  4. Combined Score = (Minto + Feynman) / 2                 │
│     ↓                                                       │
│                                                             │
│  5. If below threshold:                                    │
│     a) Ask "WHAT IS LIMITING?"                            │
│        - Identify TOP 3 limiting factors                   │
│        - Structural, Content, Clarity                      │
│     ↓                                                       │
│                                                             │
│     b) Generate 3 TARGETED variants                        │
│        - Each addresses identified limits                  │
│     ↓                                                       │
│                                                             │
│     c) Test EACH variant with BOTH judges                  │
│        Variant 1: Minto + Feynman → Combined              │
│        Variant 2: Minto + Feynman → Combined              │
│        Variant 3: Minto + Feynman → Combined              │
│     ↓                                                       │
│                                                             │
│     d) Select BEST variant (highest combined score)        │
│     ↓                                                       │
│                                                             │
│  6. Use best variant as new prompt → LOOP                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Run the dual-judge optimizer
python simpePrompt.py
```

## Configuration

Customize in `simpePrompt.py`:

```python
# Starting prompt to optimize
user_prompt = "Generate a engaging 50-word description for a wireless earbuds product."

# Optimization parameters
MAX_ITERATIONS = 3        # Maximum refinement cycles
NUM_VARIANTS = 3          # Variants to test per iteration
SCORE_THRESHOLD = 8.0     # Target quality (0-10)
```

## Example Output

```
======================================================================
DUAL-JUDGE PROMPT OPTIMIZATION
Minto Judge: Pyramid Principle (Top-down structured thinking)
Feynman Judge: Scientific Method (Simplicity & clarity)
======================================================================

######################################################################
# ITERATION 1
######################################################################

Current Prompt: Generate a engaging 50-word description for...
Generated Output: Experience premium audio with our wireless...

--- MINTO JUDGE EVALUATION ---
Score: 6.5/10
Analysis:
1. MAIN CONCLUSION: Moderate quality (6.5/10) - lacks specific value proposition

2. KEY SUPPORTING ARGUMENTS:
   - Argument A: Fluency & Clarity (7/10) - readable but generic
   - Argument B: Relevance to Intent (6/10) - meets basic requirements
   - Argument C: Engagement & Impact (6/10) - limited emotional appeal

3. SUPPORTING DETAILS:
   - Generic phrases like "premium audio" don't differentiate
   - Missing concrete features (battery life, noise cancellation)

--- FEYNMAN JUDGE EVALUATION ---
Score: 7.0/10
Analysis:

1. SIMPLICITY TEST: 8/10 - Clear language, no jargon
2. TRUTH & ACCURACY: 6/10 - "Premium" is vague and unsubstantiated
3. ELEGANCE: 7/10 - Could be more concise

*** COMBINED SCORE: 6.75/10 ***

>>> Score below threshold (6.75 < 8.0)
>>> Initiating ReAct refinement with limiting factor analysis...

============================================================
LIMITING FACTOR ANALYSIS:
============================================================

TOP 3 LIMITING FACTORS:
1. STRUCTURAL: Prompt lacks specific feature requirements (battery, noise cancellation)
2. CONTENT: No emotional hooks or user benefits specified
3. CLARITY: "Engaging" is too vague - needs definition of target audience

--- Testing Variant 1 ---
Variant Prompt: Generate a 50-word description for wireless earbuds...
  → Minto Judge Score: 7.8/10
  → Feynman Judge Score: 8.1/10
  → Combined Score: 7.95/10

--- Testing Variant 2 ---
Variant Prompt: Create a compelling 50-word description...
  → Minto Judge Score: 8.2/10
  → Feynman Judge Score: 8.0/10
  → Combined Score: 8.1/10

--- Testing Variant 3 ---
Variant Prompt: Write an engaging 50-word product description...
  → Minto Judge Score: 7.6/10
  → Feynman Judge Score: 7.9/10
  → Combined Score: 7.75/10

============================================================
BEST VARIANT SELECTED: Combined Score 8.1/10
============================================================

✓ IMPROVED! New best combined score: 8.1/10

======================================================================
FINAL RESULTS
======================================================================

Final Prompt:
Create a compelling 50-word description highlighting...

Final Output:
[Optimized output]

Final Scores:
  • Minto Judge: 8.2/10
  • Feynman Judge: 8.0/10
  • Combined: 8.1/10

======================================================================
```

## Why This Approach Works Better

### **Minto + Feynman = Comprehensive Evaluation**

| Aspect | Minto Judge | Feynman Judge | Combined Benefit |
|--------|-------------|---------------|------------------|
| **Structure** | Ensures logical flow | Ensures simplicity | Clear AND structured |
| **Truth** | Checks relevance | Checks honesty | Relevant AND honest |
| **Impact** | Engagement metrics | Elegance test | Engaging AND elegant |
| **Complexity** | Pyramid clarity | First principles | Simple but complete |

### **"What is Limiting?" > "Make it better"**

Generic refinement: "Improve this prompt"
- Vague direction
- Random improvements
- Hit-or-miss results

Limiting factor analysis: "What prevents excellence?"
- Specific diagnosis
- Targeted solutions
- Systematic improvement

### **Dual-Judge Validation**

Single judge can be biased toward one style. Two judges ensure:
- **Minto catches:** Poor structure, weak arguments, missing logic
- **Feynman catches:** Unnecessary complexity, vague claims, inefficiency
- **Together:** Only prompts that pass BOTH tests advance

## Comparison with Original

| Feature | Original CoT | Dual-Judge System |
|---------|--------------|-------------------|
| Evaluation Method | Generic CoT | Minto + Feynman |
| Scoring | Single score | Two independent scores |
| Refinement Trigger | "Improve quality" | "What is limiting?" |
| Variant Testing | Basic scoring | Dual-judge per variant |
| Focus | General quality | Structure + Simplicity |
| Rigor | Moderate | High (two methods) |

## When to Use This

**Use Dual-Judge when:**
- You need high-quality, production-ready prompts
- Clarity and truth are critical (marketing, documentation)
- You want systematic, explainable improvements
- You're willing to run more API calls for better results

**Use Original when:**
- Quick iteration is more important than perfection
- You have a reference output to compare against
- You need faster, cheaper optimization

## Cost Considerations

Each iteration makes approximately:
- 2 evaluations (Minto + Feynman)
- 3 variant generations
- 6 variant evaluations (3 variants × 2 judges)

**Total per iteration:** ~11 API calls to Claude

Trade-off: More thorough evaluation = more API usage, but **tighter, better prompts** in fewer iterations.

## Extending the System

### Add More Judges

```python
def aristotle_judge_output(output, prompt):
    """Uses Aristotelian rhetoric: Ethos, Pathos, Logos"""
    # Implementation...
```

### Customize Limiting Factor Categories

```python
# In react_refine_prompt()
"""
1. STRUCTURAL LIMITS: ...
2. CONTENT LIMITS: ...
3. CLARITY LIMITS: ...
4. EMOTIONAL LIMITS: Lacks urgency/desire?  # NEW
5. TECHNICAL LIMITS: Missing specificity?   # NEW
"""
```

### Weight Judges Differently

```python
# Instead of simple average
combined_score = (minto_score * 0.6) + (feynman_score * 0.4)
# Favors structured thinking over simplicity
```

## Philosophy

> "If you can't explain it simply, you don't understand it well enough."
> — Richard Feynman

> "Thinking is the process of organizing ideas into a pyramid."
> — Barbara Minto

This system combines both philosophies: **organized clarity** from Minto with **simple truth** from Feynman, producing prompts that are both well-structured AND easily understood.
