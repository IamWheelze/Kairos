# This file contains the command-line interface for the application, allowing users to interact with the system via terminal commands.

import argparse
from kairos.core import Kairos

def main():
    parser = argparse.ArgumentParser(description='Voice-Activated Presentation System')
    parser.add_argument('--start', action='store_true', help='Start the presentation system')
    parser.add_argument('--stop', action='store_true', help='Stop the presentation system')
    parser.add_argument('--status', action='store_true', help='Get the current status of the presentation system')
    parser.add_argument('--config', type=str, default=None, help='Path to configuration YAML')

    args = parser.parse_args()
    kairos = Kairos()

    if args.start:
        kairos.start(config_path=args.config)
        print("Presentation system started.")
    elif args.stop:
        kairos.stop()
        print("Presentation system stopped.")
    elif args.status:
        status = kairos.get_status()
        print(f"Current status: {status}")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
