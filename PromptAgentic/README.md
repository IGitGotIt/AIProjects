# PromptAgentic - CrewAI with Claude

A multi-agent system using CrewAI and Claude API for automated prompt optimization and evaluation. This project uses AI agents to iteratively improve prompts for generating product descriptions, evaluating them with both LLM judges and semantic metrics (BERTScore).

## What Does This Code Do?

This project implements an **iterative prompt optimization system** that:

1. **Generates** product descriptions from a given prompt using Claude
2. **Evaluates** the quality of generated text using:
   - LLM-based judging with Chain of Thought reasoning (Claude)
   - BERTScore semantic similarity metric
3. **Refines** the prompt based on evaluation feedback using ReAct (Reason + Act) methodology
4. **Iterates** until reaching a quality threshold or maximum iterations

### Example Use Case

Given an initial prompt like:
```
"Generate a 50-word description for wireless earbuds"
```

The system will:
- Generate a description using Claude
- Score it against a reference output (0-10 scale)
- If the score is low, create better prompt variants
- Re-evaluate and select the best performing prompt
- Repeat until achieving high-quality output

## Architecture Overview

The system uses **three specialized AI agents** working together:

### 1. **Prompt Generator Agent** 🎨
- **Role:** Creative content writer
- **Goal:** Generate high-quality, engaging product descriptions
- **Tools:**
  - `generate_output_tool()` - Uses Claude 3 Haiku to generate text from prompts
- **Behavior:** Takes a prompt and produces compelling 50-word product descriptions
- **Specialization:** Creative writing with focus on concise, engaging language

### 2. **Quality Evaluator Agent** 📊
- **Role:** Quality critic and metrics expert
- **Goal:** Score generated outputs using both LLM reasoning and semantic metrics
- **Tools:**
  - `judge_output_tool()` - Uses Claude with Chain of Thought to score quality (0-10)
  - `compute_bertscore_tool()` - Calculates BERTScore F1 semantic similarity (0-10)
- **Behavior:**
  - Evaluates relevance, fluency, and similarity to reference
  - Provides detailed feedback with reasoning
  - Combines LLM judgment with quantitative metrics
- **Specialization:** NLP metrics and critical evaluation

### 3. **Prompt Refiner Agent** 🔧
- **Role:** Optimization expert
- **Goal:** Improve underperforming prompts using ReAct methodology
- **Tools:**
  - All tools from Generator and Evaluator agents
- **Behavior:**
  - **Reason:** Analyzes why current prompts score poorly
  - **Act:** Creates multiple refined prompt variants (more specific, feature-focused)
  - **Evaluate:** Tests each variant and selects the best performer
  - **Re-rank:** Chooses highest-scoring variant as new prompt
- **Specialization:** Iterative optimization and strategic prompt engineering
- **Delegation:** Can delegate tasks to other agents when needed

## How The Agents Work Together

```
┌─────────────────────────────────────────────────────┐
│  Iteration Loop (Max 3 iterations)                  │
│                                                      │
│  1. Generator Agent                                 │
│     ↓ [generate_output_tool]                        │
│     • Takes current prompt                          │
│     • Generates 50-word description                 │
│                                                      │
│  2. Evaluator Agent                                 │
│     ↓ [judge_output_tool + compute_bertscore_tool]  │
│     • Scores output vs reference                    │
│     • LLM Judge: 0-10 (relevance, fluency, etc.)    │
│     • BERTScore: 0-10 (semantic similarity)         │
│     • Combined Score = (Judge + BERT) / 2           │
│                                                      │
│  3. Refiner Agent (if score < 7.0)                  │
│     ↓ [all tools]                                   │
│     • Analyzes evaluation feedback                  │
│     • Creates 3 improved prompt variants            │
│     • Tests each variant                            │
│     • Selects best performing prompt                │
│                                                      │
│  4. Check: Score improved? Continue or Stop         │
│     ↓                                                │
│     Loop back to step 1 with refined prompt         │
└─────────────────────────────────────────────────────┘
```

## Configuration

You can adjust these parameters in `promptAgent.py`:

```python
MAX_ITERATIONS = 3        # Maximum optimization loops
NUM_VARIANTS = 3          # Number of prompt variants to test
SCORE_THRESHOLD = 7.0     # Stop if score reaches this (0-10)
```

## Setup

### 1. Virtual Environment

The project uses Python 3.9 with a virtual environment located in `venv/`.

**Activate the virtual environment:**
```bash
source venv/bin/activate
```

**Deactivate when done:**
```bash
deactivate
```

### 2. Environment Variables

Your API key is stored in `.env` file (already configured and gitignored):
```
ANTHROPIC_API_KEY=your_key_here
```

**Important:** The `.env` file is already in `.gitignore` so your API key won't be committed to GitHub.

### 3. Dependencies

All dependencies are listed in `requirements.txt` and already installed:
- `crewai<0.2.0` (Python 3.9 compatible version)
- `anthropic` (Claude API)
- `python-dotenv` (Environment variable management)
- `evaluate` (Evaluation metrics)
- `datasets` (Dataset handling)
- `transformers` (NLP models)
- `torch` (Deep learning framework)
- `bert-score` (BERTScore metric)

To reinstall dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Files

- `promptAgent.py` - Main script with CrewAI agents using Claude API
- `test_claude.py` - Simple test script to verify Claude API connection
- `.env` - API keys (gitignored)
- `.gitignore` - Git ignore rules
- `requirements.txt` - Python dependencies

## Usage

### Test Claude API Connection
```bash
source venv/bin/activate
python test_claude.py
```

### Run Main Script
```bash
source venv/bin/activate
python promptAgent.py
```

## Technical Details

### AI Models Used

**Claude 3 Haiku** (`claude-3-haiku-20240307`):
- **Used for:** All custom tools (generation, evaluation)
- **Why Haiku:** Fast, efficient, cost-effective for iterative operations
- **API:** Anthropic Python SDK

**BERTScore:**
- **Used for:** Semantic similarity evaluation
- **Metric:** F1 score normalized to 0-10 scale
- **Purpose:** Provides quantitative measure of text similarity

### Framework

**CrewAI (v0.1.32):**
- Multi-agent orchestration framework
- Sequential task processing
- Agent delegation and collaboration
- Python 3.9 compatible version

### How Custom Tools Work

All the actual AI work uses **Claude API** (not OpenAI):

1. **generate_output_tool(prompt: str) → str**
   - Calls Claude 3 Haiku via Anthropic API
   - Returns generated text
   - Max tokens: 100, Temperature: 0.7

2. **judge_output_tool(output: str, reference: str) → float**
   - Uses Claude with Chain of Thought prompting
   - Evaluates on: relevance, fluency, similarity (1-10 each)
   - Returns average score (0-10)
   - Max tokens: 50, Temperature: 0.1 (for consistency)

3. **compute_bertscore_tool(output: str, reference: str) → float**
   - Calculates BERTScore F1 using Hugging Face `evaluate` library
   - Returns score scaled to 0-10

**Note:** A dummy OpenAI API key is set in the code to satisfy CrewAI's requirements, but it's never actually used. All AI operations use Claude.

## Git Safety

The following are gitignored to keep your credentials safe:
- `.env` (API keys)
- `venv/` (virtual environment)
- `__pycache__/` (Python cache)
- `.DS_Store` (macOS files)

You can safely commit your code to GitHub without exposing your API key.

## Expected Output

When you run the script, you'll see:

1. **Agent verbose logs** showing the reasoning and actions of each agent
2. **Task execution details** for each iteration
3. **Scores** for each generated output (LLM Judge + BERTScore)
4. **Prompt evolution** as the refiner agent creates better variants
5. **Final results:**
   - Best prompt found
   - Final output generated
   - Final combined score

Example console output:
```
--- CrewAI Iteration 1 ---
[Generator Agent] Generating output from prompt...
[Evaluator Agent] Evaluating output...
Judge Score: 6.5
BERT F1: 7.2
Combined Score: 6.85

[Refiner Agent] Score below threshold, creating variants...
Analyzing issues: Output lacks specific features...
Generated 3 prompt variants, testing each...
Best variant selected: Score 7.8

--- CrewAI Iteration 2 ---
...
```

## Troubleshooting

**bert_score ModuleNotFoundError:**
- Solution: `pip install bert-score` (already in requirements.txt)
- Make sure you're in the activated virtual environment

**Import Error with CrewAI:**
- Solution: We're using `crewai<0.2.0` which is compatible with Python 3.9
- The newer versions require Python 3.10+

**OPENAI_API_KEY Error:**
- Solution: Already handled in code (line 16 of `promptAgent.py`)
- A dummy key is set automatically - no action needed

**Model Not Found Error:**
- Make sure you're using `claude-3-haiku-20240307`
- Your API key must have access to Claude models
- Check that your `.env` file has the correct `ANTHROPIC_API_KEY`

**Slow Execution:**
- BERTScore downloads models on first run (one-time setup)
- Each iteration makes multiple Claude API calls
- Expected: 30-60 seconds per iteration

## Extending the System

Want to customize the system? Here are some ideas:

1. **Different Tasks:**
   - Change `task_prompt` and `reference_output` for different content types
   - Adjust word count requirements in prompts

2. **More Agents:**
   - Add a "Fact Checker" agent
   - Add a "Style Enforcer" agent for brand voice

3. **Different Models:**
   - Try Claude 3 Sonnet for higher quality (more expensive)
   - Replace in tool functions: `model="claude-3-sonnet-20240229"`

4. **Additional Metrics:**
   - Add BLEU score, ROUGE score
   - Custom evaluation criteria

5. **Dynamic References:**
   - Load reference outputs from a dataset
   - Generate multiple variants and pick the best
