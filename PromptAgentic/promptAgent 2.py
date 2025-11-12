import os
from crewai import Agent, Task, Crew, Process
from anthropic import Anthropic
import evaluate
from datasets import Dataset
from typing import List, Dict, Any
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Load BERTScore
bertscore = evaluate.load("bertscore")

# Sample data
task_prompt = "Generate a engaging 50-word description for a wireless earbuds product."
reference_output = "These sleek wireless earbuds deliver crystal-clear sound with noise cancellation, perfect for workouts or commutes. Battery lasts 20 hours, and they're sweat-resistant. Comfortable fit for all-day wear—your new audio essential!"
initial_prompt = task_prompt
MAX_ITERATIONS = 3
NUM_VARIANTS = 3
SCORE_THRESHOLD = 7.0  # Stop if >=7/10

# Custom Tools (wrapped for CrewAI)
def generate_output_tool(prompt: str) -> str:
    """Tool: Generate output from prompt."""
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        temperature=0.7,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()

def judge_output_tool(output: str, reference: str) -> float:
    """Tool: LLM judge with CoT (returns score 0-10)."""
    cot_prompt = f"""
    You are an expert evaluator. Use Chain of Thought:
    Step 1: Read generated output and reference.
    Step 2: Assess relevance, fluency, similarity (1-10 each).
    Step 3: Average score.
    Step 4: Output ONLY the final average score as a number (e.g., 8.5).

    Reference: {reference}
    Generated: {output}
    """
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=50,
        temperature=0.1,
        messages=[{"role": "user", "content": cot_prompt}]
    )
    try:
        return float(response.content[0].text.strip())
    except ValueError:
        return 0.0

def compute_bertscore_tool(output: str, reference: str) -> float:
    """Tool: BERTScore F1 (0-1, scaled to 0-10)."""
    results = bertscore.compute(predictions=[output], references=[reference], lang="en")
    return results['f1'][0] * 10  # Normalize to 0-10

# Agents
generator_agent = Agent(
    role="Prompt Generator",
    goal="Generate high-quality text outputs from given prompts, focusing on engaging and relevant content.",
    backstory="You are a creative writer specializing in product descriptions. Always aim for concise, compelling language.",
    tools=[generate_output_tool],  # Custom tool as function
    verbose=True,
    allow_delegation=False
)

evaluator_agent = Agent(
    role="Quality Evaluator",
    goal="Score generated outputs against a reference using CoT reasoning and semantic metrics, providing clear feedback.",
    backstory="You are a meticulous critic with expertise in NLP metrics. Break down strengths/weaknesses step-by-step.",
    tools=[judge_output_tool, compute_bertscore_tool],
    verbose=True,
    allow_delegation=False
)

refiner_agent = Agent(
    role="Prompt Refiner",
    goal="Analyze poor scores, generate refined prompt variants using ReAct (Reason + Act), evaluate them, and re-rank to select the best.",
    backstory="You are an optimization expert. Use reasoning to identify issues, act by creating targeted variants, and choose the highest-scoring one.",
    tools=[generate_output_tool, judge_output_tool, compute_bertscore_tool],
    verbose=True,
    allow_delegation=True  # Can delegate to generator/evaluator
)

# Dynamic Tasks (updated per iteration via crew kickoff)
def create_optimization_crew(current_prompt: str, reference: str, iteration: int, history: List[Dict]) -> Crew:
    # Task 1: Generate
    generate_task = Task(
        description=f"Using the current prompt: '{current_prompt}', generate a 50-word product description.",
        agent=generator_agent,
        expected_output="A generated text output."
    )
    
    # Task 2: Evaluate
    evaluate_task = Task(
        description=f"Evaluate the generated output against reference: '{reference}'. Use CoT for judge score and BERTScore. Provide combined score and feedback.",
        agent=evaluator_agent,
        expected_output="Score (0-10), feedback, and combined metric."
    )
    
    # Task 3: Refine (conditional: if score < threshold)
    refine_task = Task(
        description=f"""If score < {SCORE_THRESHOLD}, use ReAct: 
        - Thought (CoT): Analyze issues from evaluation.
        - Action: Generate {NUM_VARIANTS} prompt variants (more specific, e.g., add features).
        - Evaluate each variant's output with judge + BERTScore.
        - Re-rank and select the best variant as new prompt.
        If score >= {SCORE_THRESHOLD}, output 'No refinement needed.'""",
        agent=refiner_agent,
        expected_output="New refined prompt (or current if no change), new output, and updated score."
    )
    
    # Crew: Sequential process (generate → evaluate → refine)
    return Crew(
        agents=[generator_agent, evaluator_agent, refiner_agent],
        tasks=[generate_task, evaluate_task, refine_task],
        process=Process.sequential,  # Linear delegation
        verbose=2  # Detailed logs for explainability
    )

# Main Loop: Orchestrate Crew Iteratively
def run_crewai_optimization(initial_prompt: str, reference: str, max_iterations: int = MAX_ITERATIONS):
    current_prompt = initial_prompt
    history = []
    best_score = 0.0
    
    for iteration in range(max_iterations):
        print(f"\n--- CrewAI Iteration {iteration + 1} ---")
        
        # Kickoff crew with current state
        crew = create_optimization_crew(current_prompt, reference, iteration, history)
        result = crew.kickoff()  # Runs tasks collaboratively
        
        # Parse result (CrewAI outputs as string; in prod, use structured parsing)
        lines = result.split('\n')
        current_output = next((line for line in lines if 'Generated Output:' in line), 'N/A').split(': ')[1].strip()
        current_judge_score = float(next((line for line in lines if 'Judge Score:' in line), '0').split(': ')[1])
        bert_f1 = float(next((line for line in lines if 'BERT F1:' in line), '0').split(': ')[1])
        combined_score = (current_judge_score + bert_f1) / 2
        new_prompt = next((line for line in lines if 'New Prompt:' in line), current_prompt).split(': ')[1].strip()
        
        history.append({
            'iteration': iteration + 1,
            'prompt': current_prompt,
            'output': current_output,
            'judge_score': current_judge_score,
            'bert_f1': bert_f1,
            'combined': combined_score
        })
        
        print(f"Combined Score: {combined_score:.2f}")
        
        if combined_score > best_score:
            current_prompt = new_prompt
            best_score = combined_score
            print(f"Improved! New best: {best_score:.2f}")
        else:
            print("No improvement; stopping.")
            break
    
    # Final run for best
    final_crew = create_optimization_crew(current_prompt, reference, max_iterations, history)
    final_result = final_crew.kickoff()
    final_output = next((line for line in final_result.split('\n') if 'Final Output:' in line), 'N/A').split(': ')[1].strip()
    final_combined = best_score
    
    print(f"\nFinal Prompt: {current_prompt}")
    print(f"Final Output: {final_output}")
    print(f"Final Combined Score: {final_combined:.2f}")
    return history, final_output

# Run
history, final_output = run_crewai_optimization(initial_prompt, reference_output)