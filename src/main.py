# src/main.py
# Template for the main application logic of the Maths Online Assistant.
# This file serves as the entry point for the application, allowing users to interact with the screenshot functionality,
# capture screenshots, and retrieve step-by-step guidance and final answers from OpenAI.

# This file is temporary and will be replaced with a more robust implementation in the future.


from .screenshot import (
    capture_screenshot,
    optimize_image_for_openai,
    clear_all_screenshots,
    answers_dir,
)
from config import config
from .debug import log
from .openai import get_step_by_step_guidance, get_final_answer

import sys


def main():
    print("Starting the Mathsonline application...")
    print("--- Maths Online Assistant Application ---")
    print(
        "This application helps students with their math questions by providing step-by-step guidance and final answers."
    )
    print(
        "It captures screenshots of the question and answers regions based on the configuration settings."
    )
    print("It also logs debug information to help with troubleshooting.")

    if not config["debug"]["enabled"]:
        print("Debugging is disabled. Enable it in the config to see debug logs.")
        return

    log("Application started", "debug")

    print("\n You have multiple options:")
    print("1. Capture a screenshot of the question region.")
    print("2. Clear all screenshots.")
    print("3. Clear all logs.")
    print("4. Exit the application.")

    choice = input("Enter your choice (1-4): ")

    match choice:
        case "1":
            try:
                screenshot_file = capture_screenshot()
                log(f"Screenshot captured: {screenshot_file}", "debug")
                print(f"Screenshot saved as: {screenshot_file}")

                screenshot_file = answers_dir / screenshot_file

                optimized_image = optimize_image_for_openai(screenshot_file)
                log(f"Optimized image for OpenAI: {optimized_image}", "debug")

                step_by_step_guidance = get_step_by_step_guidance(optimized_image)
                log(f"Step-by-step guidance: {step_by_step_guidance}", "debug")
                print(step_by_step_guidance)

                final_answer = get_final_answer(optimized_image)
                log(f"Final answer: {final_answer}", "debug")
                print(f"Final answer: {final_answer}")

            except Exception as e:
                log(f"Error capturing screenshot: {e}", "debug")
                print(f"Error capturing screenshot: Check the logs for details.")
        case "2":
            try:
                clear_all_screenshots()
                log("All screenshots cleared", "debug")
                print("All screenshots have been cleared.")
            except Exception as e:
                log(f"Error clearing screenshots: {e}", "debug")
                print(f"Error clearing screenshots: Check the logs for details.")
        case "3":
            try:
                from debug import clear_all_logs

                clear_all_logs()
                log("All logs cleared", "debug")
                print("All logs have been cleared.")
            except Exception as e:
                log(f"Error clearing logs: {e}", "debug")
                print(f"Error clearing logs: Check the logs for details.")
        case "4":
            print("Exiting the application. Goodbye!")
            log("Application exited", "debug")
            sys.exit(0)


if __name__ == "__main__":
    main()
