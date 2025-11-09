"""
SuperGrokSnipV1 - Unified Entry Point
Choose between Paper Trading and Live Trading
"""

import os
import sys
from pathlib import Path

# Add directories to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("="*70)
    print("  SuperGrokSnipV1 - Crypto Sniper Bot")
    print("  Python 3.13 Edition")
    print("="*70)
    print()
    print("Choose mode:")
    print()
    print("1. Paper Trading (Safe - No Real Trades)")
    print("2. Live Trading (REAL MONEY - Use With Caution)")
    print("3. Exit")
    print()

    while True:
        choice = input("Enter choice (1-3): ").strip()

        if choice == "1":
            print("\nStarting Paper Trading Mode...\n")
            import asyncio
            from main_paper import main as paper_main
            asyncio.run(paper_main())
            break

        elif choice == "2":
            print("\nStarting Live Trading Mode...\n")
            print("⚠️  WARNING: This will trade REAL MONEY")
            confirm = input("Type 'CONFIRM' to proceed: ").strip()

            if confirm == "CONFIRM":
                import asyncio
                from main_live import main as live_main
                asyncio.run(live_main())
            else:
                print("Cancelled.")

            break

        elif choice == "3":
            print("Goodbye!")
            sys.exit(0)

        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
