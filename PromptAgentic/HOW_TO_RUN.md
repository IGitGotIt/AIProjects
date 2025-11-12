# How to Run the Triple-Judge System

## Quick Start

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Run the script
python simpePrompt.py
```

That's it! 🎉

## What You'll See

The script will automatically:

1. **Generate** output from the initial prompt
2. **Evaluate** with Minto Judge (CoT - structured thinking)
3. **Evaluate** with Feynman Judge (ReAct - scientific testing)
4. If score < threshold:
   - **Identify** what's limiting the prompt
   - **Create** 3 Feynman variants
   - **Test** all 4 candidates (Minto + 3 variants) with ALL judges
   - **Re-rank** with Taylor Swift creativity
   - **Select** winner
5. **Repeat** for up to 3 iterations
6. **Final re-ranking** of all winners

## Customize the Run

Edit these settings in `simpePrompt.py` (lines 104-107):

```python
# Your starting prompt
user_prompt = "Generate a engaging 50-word description for a wireless earbuds product."

# Maximum iterations before stopping
MAX_ITERATIONS = 3

# Number of variant prompts to test per iteration
NUM_VARIANTS = 3

# Target quality score (0-10)
SCORE_THRESHOLD = 9.0  # Higher = more refinement iterations
```

## Configuration Tips

### Want to see the full re-ranking in action?

**Set a HIGH threshold:**
```python
SCORE_THRESHOLD = 9.0  # or 9.5
```
This forces refinement iterations, so you'll see:
- Limiting factor analysis
- 3 Feynman variants created
- Taylor Swift re-ranking all 4
- Final ultimate winner selection

### Want faster results?

**Set a LOW threshold:**
```python
SCORE_THRESHOLD = 7.0
```
This may stop after 1 iteration if the initial output is good enough.

### Want more variants to test?

```python
NUM_VARIANTS = 5  # Test 5 variants per iteration
```
More variants = more API calls but potentially better results.

### Want more iterations?

```python
MAX_ITERATIONS = 5  # Try up to 5 refinement cycles
```

## Expected Output Format

### Per Iteration:

```
######################################################################
# ITERATION 1
######################################################################

Current Prompt: Generate a engaging 50-word description...
Generated Output: [text]

--- MINTO JUDGE EVALUATION ---
Score: 7.5/10
Analysis: [pyramid structure evaluation]

--- FEYNMAN JUDGE EVALUATION ---
Score: 8.0/10
Analysis: [ReAct testing results]

*** COMBINED SCORE: 7.75/10 ***

>>> Score below threshold (7.75 < 9.0)
>>> Initiating ReAct refinement...

============================================================
LIMITING FACTOR ANALYSIS:
============================================================
TOP 3 LIMITING FACTORS:
1. [specific limit]
2. [specific limit]
3. [specific limit]

--- Testing Variant 1 ---
Variant Prompt: [new prompt]
Generated Output: [text]
  → Minto Judge Score: 7.8/10
  → Feynman Judge Score: 8.2/10
  → Combined Score: 8.0/10

[Variants 2 & 3 tested...]

============================================================
🎤 TAYLOR SWIFT CREATIVITY RE-RANKING 🎤
============================================================

--- Evaluating Minto Prompt (Original) ---
Taylor Swift Score: 7.2/10

--- Evaluating Feynman Variant 1 ---
Taylor Swift Score: 8.5/10

[All variants ranked...]

🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟
TAYLOR SWIFT CREATIVITY RANKINGS:
🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟

#1 - Feynman Variant 1
  Swift Score: 8.5/10
  Minto Score: 7.8/10
  Feynman Score: 8.2/10
  Combined (M+F): 8.0/10

[All 4 ranked...]

🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆
WINNER: Feynman Variant 1
Swift Creativity: 8.5/10
🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆
```

### Final Re-Ranking:

```
🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵
🎤 FINAL TAYLOR SWIFT RE-RANKING 🎤
Evaluating ALL candidates from all iterations...
🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵🎵

======================================================================
FINAL CREATIVITY RANKINGS (All Iterations):
======================================================================

🏅 RANK #1
   Type: Feynman Variant 2
   From: Iteration 3
   🎤 Swift Creativity: 9.2/10
   📊 Minto (CoT): 8.5/10
   🔬 Feynman (ReAct): 8.8/10
   📈 Combined (M+F): 8.65/10
   💭 Output: [full output]
   📝 Prompt: [prompt]

[All winners ranked...]

🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆
🌟 ULTIMATE WINNER - MOST CREATIVE 🌟
🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆

Type: Feynman Variant 2
From: Iteration 3

🎤 Taylor Swift Creativity: 9.2/10
📊 Minto Structure: 8.5/10
🔬 Feynman Simplicity: 8.8/10
📈 Combined Quality: 8.65/10

💎 WINNING OUTPUT:
[The most creative output]

✨ WINNING PROMPT:
[The winning prompt]

🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆

======================================================================
OPTIMIZATION COMPLETE
======================================================================
```

## Troubleshooting

### Script stops immediately

If it says "THRESHOLD MET!" on iteration 1, your initial output was already good enough!

**Solution:** Increase the threshold:
```python
SCORE_THRESHOLD = 9.5  # Very high bar
```

### Too many API calls

Each iteration makes approximately:
- 2 judges for initial output (Minto + Feynman)
- 3 variants generated
- 6 variant evaluations (3 variants × 2 judges)
- 4 Taylor Swift evaluations (Minto + 3 variants)
- **Total: ~15 API calls per iteration**

**Solution to reduce:**
```python
NUM_VARIANTS = 2  # Test fewer variants
MAX_ITERATIONS = 2  # Fewer iterations
```

### Want to test a different prompt?

Change line 104:
```python
user_prompt = "Write a compelling tagline for eco-friendly shoes."
```

### Want to see more detail?

All judges provide detailed explanations in their output. The script shows:
- Minto's pyramid analysis
- Feynman's ReAct testing process
- Limiting factor analysis
- Taylor Swift's creativity assessment

## What Files Are Needed?

Required:
- `simpePrompt.py` - Main script
- `.env` - Contains your `ANTHROPIC_API_KEY`
- `venv/` - Virtual environment with dependencies

Optional (documentation):
- `TAYLOR_SWIFT_JUDGE.md` - Explains the Taylor Swift judge
- `COT_vs_REACT.md` - Explains CoT vs ReAct
- `DUAL_JUDGE_README.md` - Detailed system explanation

## Running from Scratch

If you haven't set up yet:

```bash
# 1. Create/activate venv (if not already done)
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Make sure .env has your API key
# (Already set up with ANTHROPIC_API_KEY)

# 4. Run!
python simpePrompt.py
```

## Next Steps

Once you see it working:

1. **Try different prompts** - Change the `user_prompt` variable
2. **Adjust thresholds** - See how it affects refinement
3. **Analyze winners** - See why Taylor Swift picks certain outputs
4. **Compare judges** - Notice what each judge values differently

Enjoy watching Minto, Feynman, and Taylor Swift battle it out! 🎤📊🔬
