"""
TRIPLE-JUDGE PROMPT OPTIMIZATION SYSTEM
Minto (CoT) + Feynman (ReAct) + Cohere Rerank (Semantic Re-Ranking)

METHODOLOGY:
============

1. MINTO JUDGE → Uses CoT (Chain of Thought)
   - Pyramid Principle (Barbara Minto): Conclusion → Arguments → Details
   - Method: CoT - Structured reasoning from top-down
   - Evaluates: Fluency & Clarity, Relevance to Intent, Engagement & Impact
   - Scoring: 0-10 based on pyramid structure strength
   - Why CoT: Forces logical, structured thinking with clear conclusions first

2. FEYNMAN JUDGE → Uses ReAct (Reason + Act + Observe)
   - Scientific Method (Richard Feynman): Test everything, simplify ruthlessly
   - Method: ReAct - Form hypothesis, test it, observe results
   - Tests:
     * Reason: What's the core message? Hypothesis about clarity/truth
     * Act: Test simplicity (explain to 12-year-old)
     * Act: Test truth (verify each claim is specific/defensible)
     * Act: Test elegance (remove fluff, check if meaning changes)
     * Observe: Draw conclusion from test results
   - Scoring: 0-10 based on scientific test results
   - Why ReAct: Scientific method requires testing, not just reasoning

3. COHERE RERANK → Semantic Re-Ranking
   - Method: State-of-the-art semantic similarity (rerank-english-v3.0)
   - Model: Cohere's production reranking model with multilingual support
   - Evaluates: Semantic relevance between query and generated outputs
   - Scoring: Relevance score 0-1 (higher = more relevant to original prompt)
   - Purpose: Re-ranks ALL candidates based on query alignment
   - Why: Reliable API, generous free tier, fast, production-ready

4. REACT WITH "WHAT IS LIMITING?" ANALYSIS
   - Uses ReAct at refinement stage
   - Reason: Analyze WHY current prompt underperforms
   - Act: Generate 3 targeted variants addressing specific limits
   - Observe: Test all variants with ALL THREE judges
   - Categories of limits: Structural, Content, Clarity

5. DUAL-JUDGE VARIANT TESTING
   - Each iteration generates: 3 Feynman variants addressing limitations
   - All 3 evaluated by BOTH Minto Judge and Feynman Judge
   - Best variant selected by combined score (Minto + Feynman)
   - Both Minto original AND best Feynman variant added to Re-Rank Queue

6. FINAL RE-RANKING
   - All candidates from all iterations collected (2 per iteration)
   - Final Cohere Rerank based on semantic relevance to original query
   - Ultimate winner = highest relevance score to original user prompt

WORKFLOW:
=========
Generate →
  Minto Judge (CoT) →
  Feynman Judge (ReAct) →
  Identify Limits (ReAct) →
  Create 3 Feynman Variants →
  Test ALL 3 variants with BOTH judges →
  Select Best Feynman Variant (by combined score) →
  Add Minto + Best Feynman to Re-Rank Queue →
  Iterate →
  FINAL COHERE RERANK RE-RANKING of ALL candidates

PRINTED SECTIONS:
=================
Per Iteration:
  📊 Minto Result (original prompt + output)
  🔬 Best Feynman Variant (refined prompt + output)

Final:
  🔄 FINAL COHERE RERANK RE-RANKING (all iterations)
  🏅 Ranked list of all candidates (by semantic relevance)
  🌟 ULTIMATE WINNER (most relevant to original query)

KEY INSIGHT:
============
Minto (CoT) ensures STRUCTURED REASONING
Feynman (ReAct) ensures TESTED SIMPLICITY
Cohere Rerank ensures SEMANTIC RELEVANCE
Together = Structure + Truth + Query Alignment = Maximum Impact Prompts
"""

import os
from anthropic import Anthropic
import cohere
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Initialize Cohere client for reranking
co = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))

# User input: The prompt to refine (no reference needed)
user_prompt = "Generate a engaging 50-word description for a wireless earbuds product."  # Your starting point
MAX_ITERATIONS = 3
NUM_VARIANTS = 3
SCORE_THRESHOLD = 9.0  # Intrinsic quality target (0-10) - High bar to see refinement in action!

# Step 1: Minto Judge - Uses Minto Pyramid Principle (Conclusion → Supporting Arguments)
def minto_judge_output(generated_output, original_prompt):
    """
    Minto Pyramid Principle: Start with the answer, then provide supporting logic.
    Structure: Main Point → Key Arguments → Supporting Details
    """
    minto_prompt = f"""
    You are the "Minto Judge" using the Minto Pyramid Principle for evaluation.

    EVALUATE THIS OUTPUT USING PYRAMID STRUCTURE:

    Original Prompt: {original_prompt}
    Generated Output: {generated_output}

    FORMAT YOUR RESPONSE AS:

    1. MAIN CONCLUSION (Top of Pyramid): Overall quality score (0-10) and verdict in ONE sentence.

    2. KEY SUPPORTING ARGUMENTS (Middle Layer):
       - Argument A: Fluency & Clarity (0-10)
       - Argument B: Relevance to Intent (0-10)
       - Argument C: Engagement & Impact (0-10)

    3. SUPPORTING DETAILS (Base Layer):
       - Specific evidence from the text supporting each argument

    IMPORTANT: Start your response with ONLY the numeric score on the first line (e.g., 8.5).
    Then provide the pyramid structure explanation.
    """

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=300,
        temperature=0.1,
        messages=[{"role": "user", "content": minto_prompt}]
    )
    content = response.content[0].text.strip()

    try:
        lines = content.split('\n')
        score = float(lines[0].strip())
        explanation = '\n'.join(lines[1:]).strip()
        return score, explanation
    except (ValueError, IndexError):
        return 0.0, "Parse error in Minto evaluation."

# Step 2: Feynman Judge - Uses ReAct (Reason + Act + Observe)
def feynman_judge_output(generated_output, original_prompt):
    """
    Feynman Method with ReAct:
    - Reason: Form hypothesis about quality
    - Act: Test it (simplify, verify claims, check understanding)
    - Observe: Did tests pass? What's the verdict?
    """
    feynman_prompt = f"""
    You are the "Feynman Judge" - a scientist using the ReAct method to evaluate.

    USE REACT - REASON, ACT, OBSERVE:

    Original Prompt: {original_prompt}
    Generated Output: {generated_output}

    STEP 1 - REASON (Form Hypothesis):
    - What is the core message of this output?
    - Hypothesis: Is this message clear, truthful, and simple?

    STEP 2 - ACT (Test Your Hypothesis):

    Action A - SIMPLICITY TEST:
    • Try to explain the core message in one sentence a 12-year-old would understand
    • Test: Does it work? Can you strip away jargon?
    • Result: Simple version and clarity score (0-10)

    Action B - TRUTH TEST:
    • Identify each claim in the output
    • Test: Is each claim specific and defensible, or vague/exaggerated?
    • Example: "Premium quality" = VAGUE, "20-hour battery" = SPECIFIC
    • Result: Truth score (0-10)

    Action C - ELEGANCE TEST:
    • Count words used vs. minimum needed
    • Test: Remove fluff. Did meaning change?
    • Result: Elegance score (0-10)

    STEP 3 - OBSERVE (Draw Conclusion):
    • Based on test results, what's the scientific verdict?
    • Average the 3 test scores

    OUTPUT FORMAT:
    First line: Overall score (0-10) as a number only (e.g., 7.5)
    Following lines: Show your Reasoning, Actions taken, and Observations for each test
    """

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=400,
        temperature=0.1,
        messages=[{"role": "user", "content": feynman_prompt}]
    )
    content = response.content[0].text.strip()

    try:
        lines = content.split('\n')
        score = float(lines[0].strip())
        explanation = '\n'.join(lines[1:]).strip()
        return score, explanation
    except (ValueError, IndexError):
        return 0.0, "Parse error in Feynman evaluation."

# Step 3: Cohere Rerank - Replaces Taylor Swift creativity judge
def cohere_rerank_candidates(candidates, query):
    """
    Cohere Rerank: Uses rerank-english-v3.0 for semantic reranking

    Replaces the Taylor Swift creativity judge with Cohere's reranking model
    which provides semantic similarity scoring based on query relevance.

    Args:
        candidates: List of dicts with 'output' key containing generated text
        query: The original user prompt (what we're trying to optimize for)

    Returns:
        List of tuples: (original_candidate_index, relevance_score)
        Sorted by relevance score (highest first)
    """
    # Extract outputs from candidates
    documents = [candidate['output'] for candidate in candidates]

    # Use Cohere Rerank v3.0
    # Model: rerank-english-v3.0 (state-of-the-art semantic reranking)
    results = co.rerank(
        model="rerank-english-v3.0",
        query=query,
        documents=documents,
        top_n=len(documents)  # Return all candidates, ranked
    )

    # Extract scores and return as (index, score) tuples
    # Cohere returns results sorted by relevance score (descending)
    ranked_results = []
    for result in results.results:
        # result.index is the original index in the documents list
        # result.relevance_score is the relevance score (0-1, higher = more relevant)
        ranked_results.append((result.index, result.relevance_score))

    return ranked_results

# Step 4: Generate output from a prompt
def generate_output(prompt):
    """Generate text output using Claude"""
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=100,
        temperature=0.7,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()

# Step 4: Enhanced ReAct Refinement - Identifies "What is Limiting?" then tests variants
def react_refine_prompt(current_prompt, current_output, minto_score, feynman_score, minto_feedback, feynman_feedback, original_user_prompt):
    """
    ReAct with Limiting Factor Analysis:
    1. Reason: Identify what is LIMITING the quality
    2. Act: Generate 3 variants addressing those limitations
    3. Test: Run each variant through BOTH judges separately
    4. Select: Choose the best performing variant
    """

    # REASON: Identify the limiting factors
    reason_prompt = f"""
    You are analyzing WHY a prompt is underperforming.

    CURRENT SITUATION:
    - Prompt: {current_prompt}
    - Generated Output: {current_output}
    - Minto Judge Score: {minto_score}/10
    - Minto Feedback: {minto_feedback}
    - Feynman Judge Score: {feynman_score}/10
    - Feynman Feedback: {feynman_feedback}
    - Original Intent: {original_user_prompt}

    CRITICAL QUESTION: What is LIMITING this prompt from achieving excellence?

    Analyze the limiting factors in these categories:
    1. STRUCTURAL LIMITS: Is the prompt too vague, too complex, or missing key constraints?
    2. CONTENT LIMITS: Does it lack specific features, benefits, or emotional hooks?
    3. CLARITY LIMITS: Is it confusing, ambiguous, or using unclear language?

    OUTPUT FORMAT:
    First, identify the TOP 3 LIMITING FACTORS (be specific).
    Then, suggest {NUM_VARIANTS} refined prompt variants that address these limits.
    Number each variant 1-{NUM_VARIANTS}.
    """

    reason_response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=400,
        temperature=0.5,
        messages=[{"role": "user", "content": reason_prompt}]
    )
    variants_text = reason_response.content[0].text.strip()

    # Extract limiting factors and variants
    print("\n" + "="*60)
    print("LIMITING FACTOR ANALYSIS:")
    print("="*60)

    # Find where variants start
    lines = variants_text.split('\n')
    limiting_section = []
    variants_section = []
    in_variants = False

    for line in lines:
        if any(line.strip().startswith(f"{i}.") for i in range(1, NUM_VARIANTS+2)):
            in_variants = True

        if in_variants:
            variants_section.append(line)
        else:
            limiting_section.append(line)

    print('\n'.join(limiting_section))
    print("\n" + "="*60)

    # Extract actual prompt variants (lines starting with numbers)
    variants = []
    for line in variants_section:
        for i in range(1, NUM_VARIANTS+1):
            if line.strip().startswith(f"{i}."):
                # Remove the number prefix
                variant_text = line.split(".", 1)[1].strip()
                variants.append(variant_text)
                break

    # ACT: Generate & evaluate each variant with BOTH judges
    variant_results = []
    for i, variant in enumerate(variants[:NUM_VARIANTS], 1):
        print(f"\n--- Testing Variant {i} ---")
        print(f"Variant Prompt: {variant}")

        # Generate output from this variant
        variant_output = generate_output(variant)
        print(f"Generated Output: {variant_output}")

        # Judge with Minto Judge
        minto_score_v, minto_feedback_v = minto_judge_output(variant_output, original_user_prompt)
        print(f"  → Minto Judge Score: {minto_score_v:.2f}")

        # Judge with Feynman Judge
        feynman_score_v, feynman_feedback_v = feynman_judge_output(variant_output, original_user_prompt)
        print(f"  → Feynman Judge Score: {feynman_score_v:.2f}")

        # Combined score (average of both judges)
        combined_score = (minto_score_v + feynman_score_v) / 2
        print(f"  → Combined Score: {combined_score:.2f}")

        variant_results.append({
            'variant': variant,
            'output': variant_output,
            'minto_score': minto_score_v,
            'feynman_score': feynman_score_v,
            'combined_score': combined_score,
            'minto_feedback': minto_feedback_v,
            'feynman_feedback': feynman_feedback_v
        })

    # Select best Feynman variant by combined score (Minto + Feynman)
    best_feynman = max(variant_results, key=lambda x: x['combined_score'])

    print("\n" + "="*60)
    print("📊 MINTO RESULT:")
    print(f"   Prompt: {current_prompt}")
    print(f"   Output: {current_output}")
    print(f"   Minto: {minto_score:.2f} | Feynman: {feynman_score:.2f} | Combined: {(minto_score + feynman_score) / 2:.2f}")

    print("\n" + "="*60)
    print(f"🔬 BEST FEYNMAN VARIANT:")
    print(f"   Prompt: {best_feynman['variant']}")
    print(f"   Output: {best_feynman['output']}")
    print(f"   Minto: {best_feynman['minto_score']:.2f} | Feynman: {best_feynman['feynman_score']:.2f} | Combined: {best_feynman['combined_score']:.2f}")
    print("="*60)

    # Return both for collection (no Swift evaluation yet)
    return {
        'minto_candidate': {
            'type': 'Minto',
            'variant': current_prompt,
            'output': current_output,
            'minto_score': minto_score,
            'feynman_score': feynman_score,
            'combined_score': (minto_score + feynman_score) / 2
        },
        'feynman_candidate': {
            'type': 'Feynman Winner',
            'variant': best_feynman['variant'],
            'output': best_feynman['output'],
            'minto_score': best_feynman['minto_score'],
            'feynman_score': best_feynman['feynman_score'],
            'combined_score': best_feynman['combined_score']
        }
    }

# Step 5: Main Optimization Loop with Dual-Judge System + Taylor Swift Re-ranking
def dual_judge_optimization_loop(user_prompt, max_iterations=MAX_ITERATIONS):
    """
    Iterative optimization using both Minto and Feynman judges.
    Asks "What is limiting?" at each iteration and generates targeted variants.
    Uses Taylor Swift creativity for re-ranking.
    Collects all candidates for final re-ranking.
    """
    current_prompt = user_prompt
    best_combined_score = 0.0
    history = []
    rerank_queue = []  # Collect Minto + winners for final re-ranking

    print("\n" + "="*70)
    print("TRIPLE-JUDGE PROMPT OPTIMIZATION")
    print("Minto Judge (CoT): Pyramid Principle (Structured thinking)")
    print("Feynman Judge (ReAct): Scientific Method (Simplicity & clarity)")
    print("Taylor Swift Judge: Creativity & Emotional Resonance")
    print("="*70)

    for iteration in range(max_iterations):
        print(f"\n{'#'*70}")
        print(f"# ITERATION {iteration + 1}")
        print(f"{'#'*70}")

        # Generate output from current prompt
        print(f"\nCurrent Prompt: {current_prompt}")
        current_output = generate_output(current_prompt)
        print(f"Generated Output: {current_output}")

        # Evaluate with Minto Judge
        print("\n--- MINTO JUDGE EVALUATION ---")
        minto_score, minto_explanation = minto_judge_output(current_output, user_prompt)
        print(f"Score: {minto_score:.2f}/10")
        print(f"Analysis:\n{minto_explanation}")

        # Evaluate with Feynman Judge
        print("\n--- FEYNMAN JUDGE EVALUATION ---")
        feynman_score, feynman_explanation = feynman_judge_output(current_output, user_prompt)
        print(f"Score: {feynman_score:.2f}/10")
        print(f"Analysis:\n{feynman_explanation}")

        # Combined score
        combined_score = (minto_score + feynman_score) / 2
        print(f"\n*** COMBINED SCORE: {combined_score:.2f}/10 ***")

        # Track history
        history.append({
            'iteration': iteration + 1,
            'prompt': current_prompt,
            'output': current_output,
            'minto_score': minto_score,
            'feynman_score': feynman_score,
            'combined_score': combined_score
        })

        # Check if threshold met
        if combined_score >= SCORE_THRESHOLD:
            print(f"\n✓ THRESHOLD MET! ({combined_score:.2f} >= {SCORE_THRESHOLD})")
            break

        # Refine if below threshold - Ask "What is limiting?"
        print(f"\n>>> Score below threshold ({combined_score:.2f} < {SCORE_THRESHOLD})")
        print(">>> Initiating ReAct refinement with limiting factor analysis...")

        result = react_refine_prompt(
            current_prompt, current_output,
            minto_score, feynman_score,
            minto_explanation, feynman_explanation,
            user_prompt
        )

        # Add both Minto and Feynman winner to re-rank queue
        rerank_queue.append({
            'iteration': iteration + 1,
            'prompt': result['minto_candidate']['variant'],
            'output': result['minto_candidate']['output'],
            'type': f"Iteration {iteration + 1} - Minto",
            'minto_score': result['minto_candidate']['minto_score'],
            'feynman_score': result['minto_candidate']['feynman_score'],
            'combined_score': result['minto_candidate']['combined_score']
        })

        rerank_queue.append({
            'iteration': iteration + 1,
            'prompt': result['feynman_candidate']['variant'],
            'output': result['feynman_candidate']['output'],
            'type': f"Iteration {iteration + 1} - Feynman Winner",
            'minto_score': result['feynman_candidate']['minto_score'],
            'feynman_score': result['feynman_candidate']['feynman_score'],
            'combined_score': result['feynman_candidate']['combined_score']
        })

        # Check for improvement (use Feynman winner for next iteration)
        if result['feynman_candidate']['combined_score'] > best_combined_score:
            current_prompt = result['feynman_candidate']['variant']
            best_combined_score = result['feynman_candidate']['combined_score']
            print(f"\n✓ IMPROVED! New best combined score: {best_combined_score:.2f}")
        else:
            print(f"\n✗ No improvement ({result['feynman_candidate']['combined_score']:.2f} <= {best_combined_score:.2f})")
            print("Stopping iteration.")
            break

    # FINAL RE-RANKING: Cohere Rerank evaluates ALL collected candidates ONCE
    print("\n" + "🔄"*35)
    print("🔄 FINAL COHERE RERANK RE-RANKING 🔄")
    print(f"Re-ranking {len(rerank_queue)} candidates from all iterations...")
    print("Using Cohere rerank-english-v3.0")
    print("🔄"*35)

    if rerank_queue:
        # Evaluate all candidates with Cohere Rerank
        print("\n📋 Candidates to re-rank:")
        for i, candidate in enumerate(rerank_queue, 1):
            print(f"   {i}. {candidate['type']}")

        print(f"\n🔄 Re-ranking with Cohere Rerank v3.0...")
        print(f"   Query: \"{user_prompt}\"")

        # Use Cohere to rerank based on query relevance
        ranked_results = cohere_rerank_candidates(rerank_queue, user_prompt)

        # Add Cohere scores to candidates
        for idx, score in ranked_results:
            rerank_queue[idx]['cohere_score'] = score
            print(f"   ✓ {rerank_queue[idx]['type']}: {score:.4f}")

        # Sort candidates by Cohere score (descending)
        final_reranked = sorted(rerank_queue, key=lambda x: x['cohere_score'], reverse=True)

        print("\n" + "="*70)
        print("🌟 FINAL RANKINGS (By Cohere Semantic Relevance):")
        print("="*70)

        for rank, candidate in enumerate(final_reranked, 1):
            print(f"\n🏅 RANK #{rank}: {candidate['type']}")
            print(f"   🔄 Cohere: {candidate['cohere_score']:.4f}")
            print(f"   📊 Minto: {candidate['minto_score']:.2f}/10")
            print(f"   🔬 Feynman: {candidate['feynman_score']:.2f}/10")
            print(f"   📈 Combined (M+F): {candidate['combined_score']:.2f}/10")
            print(f"   💭 Output: {candidate['output']}")

        ultimate_winner = final_reranked[0]
        print("\n" + "🏆"*35)
        print("🌟 ULTIMATE WINNER - MOST RELEVANT 🌟")
        print("🏆"*35)
        print(f"\n{ultimate_winner['type']}")
        print(f"\n🔄 Cohere Relevance: {ultimate_winner['cohere_score']:.4f}")
        print(f"📊 Minto Structure: {ultimate_winner['minto_score']:.2f}/10")
        print(f"🔬 Feynman Simplicity: {ultimate_winner['feynman_score']:.2f}/10")
        print(f"📈 Combined Quality (M+F): {ultimate_winner['combined_score']:.2f}/10")
        print(f"\n💎 WINNING OUTPUT:\n{ultimate_winner['output']}")
        print(f"\n✨ WINNING PROMPT:\n{ultimate_winner['prompt']}")
        print("\n" + "🏆"*35)

    else:
        # No refinement happened, just show final result
        print("\nNo refinement iterations - showing final result only")
        final_output = generate_output(current_prompt)
        final_minto, _ = minto_judge_output(final_output, user_prompt)
        final_feynman, _ = feynman_judge_output(final_output, user_prompt)
        final_combined = (final_minto + final_feynman) / 2

        print(f"\nFinal Prompt:\n{current_prompt}")
        print(f"\nFinal Output:\n{final_output}")
        print(f"\nFinal Scores:")
        print(f"  • Minto Judge: {final_minto:.2f}/10")
        print(f"  • Feynman Judge: {final_feynman:.2f}/10")
        print(f"  • Combined (M+F): {final_combined:.2f}/10")
        print(f"\nNote: Cohere re-ranking only applies when comparing multiple candidates")

    print("\n" + "="*70)
    print("OPTIMIZATION COMPLETE")
    print("="*70)

    return history, rerank_queue

# Run the optimization
if __name__ == "__main__":
    history, final_output = dual_judge_optimization_loop(user_prompt)