# This file initiates the training process for the AI models.

import argparse
import os
from src.kairos.training.trainer import Trainer

def main():
    parser = argparse.ArgumentParser(description="Train the Voice-Activated Presentation System model.")
    parser.add_argument('--config', type=str, required=True, help='Path to the configuration file.')
    parser.add_argument('--output_dir', type=str, default='models/checkpoints', help='Directory to save model checkpoints.')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    trainer = Trainer(config_path=args.config, output_dir=args.output_dir)
    trainer.train()

if __name__ == "__main__":
    main()