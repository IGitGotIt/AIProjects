# Install if needed: pip install evaluate datasets transformers torch sentencepiece
import evaluate
from datasets import Dataset

# Sample data: LLM predictions vs. human references (list of strings)
predictions = [
    "To fix the video streaming issue, first verify your API key is valid in the dashboard. Then check if your request includes the required 'video_id' parameter. Make sure you're using the correct endpoint: POST /api/v2/stream. If the error persists, enable debug mode by adding '?debug=true' to see detailed logs.",
    "The authentication error occurs because your API key lacks video access permissions. Go to Settings > API Keys, select your key, and enable 'Video API' under permissions. Wait 5 minutes for changes to propagate, then retry your request."
]
references = [
    ["yeah so the video thing isnt working... u need to check ur api key is good and also make sure u put the video_id in there. oh and use POST /api/v2/stream endpoint. if it still breaks turn on debug=true or whatever"],
    ["The authentication error is due to missing video access permissions on your API key. Navigate to Settings > API Keys in your dashboard, select the appropriate key, and enable the 'Video API' permission. Allow approximately 5 minutes for the permission changes to propagate through our system before retrying your request."]
]

# Wrap in Dataset for batching (optional but efficient)
dataset = Dataset.from_dict({"predictions": predictions, "references": references})

# Load metrics
bleu = evaluate.load("bleu")
rouge = evaluate.load("rouge")
bertscore = evaluate.load("bertscore")

# Compute scores
bleu_score = bleu.compute(predictions=predictions, references=references)
rouge_score = rouge.compute(predictions=predictions, references=references)
bertscore_results = bertscore.compute(predictions=predictions, references=references, lang="en")

# Print results
print("\n=== Evaluation Results ===\n")
print(f"Overall BLEU Score: {bleu_score['bleu']:.4f}")
print(f"Overall ROUGE-1: {rouge_score['rouge1']:.4f}")
print(f"Overall ROUGE-2: {rouge_score['rouge2']:.4f}")
print(f"Overall ROUGE-L: {rouge_score['rougeL']:.4f}")
print(f"Overall BERTScore F1 (avg): {sum(bertscore_results['f1'])/len(bertscore_results['f1']):.4f}")

print("\n=== Individual Scores ===\n")
for i, (pred, ref) in enumerate(zip(predictions, references)):
    print(f"Example {i+1}:")
    print(f"  BERTScore F1: {bertscore_results['f1'][i]:.4f}")
    print()

# For LLM-as-judge (using Claude)
import anthropic
client = anthropic.Anthropic(api_key="")

def llm_judge(llm_output, human_ref, prompt="Rate tech support helpfullness  from 1-10. Reply with only the number."):
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": f"{prompt}\nLLM: {llm_output}\nHuman: {human_ref}"}]
    )
    import re
    text = response.content[0].text.strip()
    match = re.search(r'\d+\.?\d*', text)
    score = float(match.group()) if match else 0.0
    return score

# Example
print("\n=== LLM Judge ===\n")
for i, (pred, ref) in enumerate(zip(predictions, references)):
    judge_score = llm_judge(pred, ref[0])
    print(f"Example {i+1} - LLM Judge Score: {judge_score}/10")