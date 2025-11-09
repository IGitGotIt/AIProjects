import os
import anthropic
import evaluate
from datasets import Dataset
import random

# Initialize Anthropic client
client = anthropic.Anthropic(api_key="")

# Load BERTScore for supplementary eval (semantic similarity to reference)
bertscore = evaluate.load("bertscore")

# Step 1: Define the task (e.g., generate a product description; reference is human-written)
task_prompt = "Generate a engaging 50-word description for a wireless earbuds product."
reference_output = "These sleek wireless earbuds deliver crystal-clear sound with noise cancellation, perfect for workouts or commutes. Battery lasts 20 hours, and they're sweat-resistant. Comfortable fit for all-day wear—your new audio essential!"

# Initial prompt (to optimize)
initial_prompt = task_prompt  # Start simple; we'll refine it

# Step 2: LLM-as-Judge with CoT (scores on relevance, fluency, similarity to ref: 1-10 scale)
def llm_judge_with_cot(generated_output, reference, criteria="relevance, fluency, similarity"):
    cot_prompt = f"""
    You are an expert evaluator. Use Chain of Thought: Step 1: Read the generated output and reference.
    Step 2: Assess on {criteria} (1-10 scale each).
    Step 3: Compute average score.
    Step 4: Output ONLY the final average score as a number (e.g., 8.5).

    Reference: {reference}
    Generated: {generated_output}
    """
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",  # Using Claude 3.5 Haiku
        max_tokens=1024,
        messages=[{"role": "user", "content": cot_prompt}],
        temperature=0.1
    )
    try:
        score = float(response.content[0].text.strip())
        return score
    except ValueError:
        return 0.0  # Fallback on parse error

# Step 3: Generate output from a prompt
def generate_output(prompt, model="claude-3-5-haiku-20241022"):
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.content[0].text.strip()

# Step 4: ReAct-like Agent for Refinement (Reason + Act)
def react_refine_prompt(current_prompt, current_output, reference, num_variants=3):
    # Reason (CoT): Analyze why it's not great
    reason_prompt = f"""
    Current Prompt: {current_prompt}
    Output: {current_output}
    Reference: {reference}
    
    Use ReAct: Thought: What issues exist (e.g., too vague, missing details)? 
    Action: Suggest {num_variants} refined prompt variants (shorter, more specific).
    Output ONLY the list of variants, numbered 1-{num_variants}.
    """
    reason_response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": reason_prompt}],
        temperature=0.5
    )
    variants_text = reason_response.content[0].text.strip()
    variants = [v.strip() for v in variants_text.split('\n') if v.strip().startswith(tuple(f"{i}." for i in range(1, num_variants+1)))]

    # Act: Generate & evaluate variants
    variant_scores = []
    for i, variant in enumerate(variants[:num_variants], 1):
        new_output = generate_output(variant)
        judge_score = llm_judge_with_cot(new_output, reference)
        bert_score = bertscore.compute(predictions=[new_output], references=[reference], lang='en')['f1'][0]
        combined_score = (judge_score + bert_score * 10) / 2  # Normalize BERT (0-1) to 0-10
        variant_scores.append((variant, new_output, combined_score))
        print(f"Variant {i} Score: {combined_score:.2f}")

    # Re-rank: Sort by score, pick top
    best_variant = max(variant_scores, key=lambda x: x[2])
    return best_variant[0], best_variant[1], best_variant[2]  # New prompt, output, score

# Step 5: Iterative Loop (Run for N iterations)
def optimization_loop(initial_prompt, reference, max_iterations=3):
    current_prompt = initial_prompt
    best_score = 0
    history = []

    for iteration in range(max_iterations):
        print(f"\n--- Iteration {iteration + 1} ---")
        current_output = generate_output(current_prompt)
        initial_judge_score = llm_judge_with_cot(current_output, reference)
        
        # ReAct refinement
        new_prompt, new_output, new_score = react_refine_prompt(current_prompt, current_output, reference)
        
        history.append({
            'iteration': iteration + 1,
            'prompt': current_prompt,
            'output': current_output,
            'score': initial_judge_score
        })
        
        if new_score > best_score:
            current_prompt = new_prompt
            best_score = new_score
            print(f"Improved! New best score: {best_score:.2f}")
        else:
            print("No improvement; stopping early.")
            break

    # Final best
    final_output = generate_output(current_prompt)
    final_score = llm_judge_with_cot(final_output, reference)
    print(f"\nFinal Prompt: {current_prompt}")
    print(f"Final Output: {final_output}")
    print(f"Final Score: {final_score:.2f}")
    return history, final_output

# Run the loop
history, final_output = optimization_loop(initial_prompt, reference_output)