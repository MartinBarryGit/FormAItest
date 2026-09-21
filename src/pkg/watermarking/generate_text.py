
import numpy as np
import argparse
from pkg.utils import new_generate_text

def main(args):
    seed = args.seed
    np.random.seed(seed)
    model = args.model  # Replace with your model name
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": args.prompt}
    ]
    # print("===============================")
    # print("Welcome to the Watermarking Script")
    # print('Running with model:', model, 'Watermarking:', args.watermarking, 'Seed:', seed)
    # print("===============================")
    new_generate_text(model, messages, watermarking=args.watermarking, n_duels=8)


    
def parse_arguments():
    parser = argparse.ArgumentParser(description="Run the watermarking script.")
    parser.add_argument("--model", type=str, default="qwen3.5", help="Model name to use for streaming responses.")
    parser.add_argument("--watermarking", action="store_true", help="Enable watermarking in the streaming response.")
    parser.add_argument("--seed", type=int, default=1, help="Random seed for reproducibility.")
    parser.add_argument("--prompt", type=str, default="Tell me a short story about a brave knight and a dragon.", help="Prompt to send to the model.")
    return parser.parse_args()
if __name__ == "__main__":
    args = parse_arguments()
    print("Parsed arguments:", args)
    main(args)