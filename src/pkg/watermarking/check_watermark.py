
from pkg.utils import check_watermarking
import argparse
def main(text, args):
    
    model = args.model  # Replace with your model name
    check_watermarking(model, text)
def parse_arguments():
    parser = argparse.ArgumentParser(description="Run the watermarking script.")
    parser.add_argument("--model", type=str, default="qwen3.5", help="Model name to use for streaming responses.")
    parser.add_argument("--text", type=str, help="Text to check instead of the built-in sample.")
    return parser.parse_args()
if __name__ == "__main__":
    args = parse_arguments()
    text = args.text or """High above the village of Oakhaven, atop the jagged peak of Cinder Peak, lived Ignis, a dragon of immense size and fiery breath. The villagers whispered in fear at his name, but in the heart of the village, a young knight named Elara stood ready to face her destiny.



Elara was not a knight of great strength or wealth, but her courage was unmatched. She had trained her entire life for this moment, honing her skills in the quiet solitude of the training grounds, always keeping a watchful eye on the horizon Ignis. One day, a young child was lost in the forest near the dragon’s lair. The villagers were in chaos, and Elara knew she had to act. With her armor gleaming in the sunlight and her sword at her side, she rode forth into the forest, her heart pounding with fear and determination.
As she ventured deeper, the air grew thick with sulfur and heat. The trees twisted and groaned in the wind, as if warning her of the dangers that lay ahead. Suddenly, a massive shadow fell over her, and Ignis emerged from the shadows, his eyes glowing red with power. Elara did not falter; instead, she stood her ground, her sword raised high. "I am here to protect the innocent,!" she shouted bravely.
"""
    main(text, args)