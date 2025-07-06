import json
import logging
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from crawl_api import LeetCodeAPICrawler

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LeetCodeIntegration:
    def __init__(self, data_file: str = "problems.json"):
        self.data_file = data_file
        self.crawler = LeetCodeAPICrawler()
        self.problems = self._load_problems()

    def _load_problems(self) -> Dict:
        """Load problems from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Handle migration from list format to dict format
                if isinstance(data, list):
                    logger.info(
                        f"Migrating {len(data)} problems from list format to dict format"
                    )
                    problems_dict = {}
                    for i, problem in enumerate(data):
                        # Generate ID if not present
                        problem_id = str(problem.get("id", i + 1))
                        problems_dict[problem_id] = problem

                    # Save in new format
                    with open(self.data_file, "w", encoding="utf-8") as f:
                        json.dump(problems_dict, f, indent=2, ensure_ascii=False)

                    logger.info(
                        f"Migration completed. Saved {len(problems_dict)} problems in dict format"
                    )
                    return problems_dict
                elif isinstance(data, dict):
                    return data
                else:
                    logger.error(
                        f"Unexpected data type in {self.data_file}: {type(data)}"
                    )
                    return {}

            except Exception as e:
                logger.error(f"Error loading problems: {e}")
        return {}

    def _save_problems(self):
        """Save problems to JSON file"""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.problems, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving problems: {e}")

    def add_problem_by_url(self, url: str) -> Optional[Dict]:
        """Add problem by crawling URL"""
        try:
            logger.info(f"Starting to add problem from URL: {url}")
            problem_data = self.crawler.get_problem_content(url)
            logger.info(f"Got problem_data: {problem_data is not None}")

            if not problem_data:
                logger.error("No problem data returned from crawler")
                return None

            logger.info(f"Problem title: {problem_data.get('title', 'No title')}")
            logger.info(f"Problem ID: {problem_data.get('id', 'No ID')}")

            problem_id = str(problem_data["id"])
            logger.info(f"Using problem_id: {problem_id}")

            self.problems[problem_id] = problem_data
            logger.info(f"Added to problems dict, total problems: {len(self.problems)}")

            # self._save_problems()
            # logger.info("Saved problems to file")

            return problem_data
        except Exception as e:
            logger.error(f"Error adding problem: {e}")
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    def get_current_problem(self) -> Optional[int]:
        """Get current problem ID from file, increment it, and save back to file"""
        try:
            # Read current problem ID from file
            with open("current_problem.txt", "r") as f:
                current_id = int(f.read().strip())
            
            # Increment by 1
            next_id = current_id + 1
            
            # Write the new ID back to file
            with open("current_problem.txt", "w") as f:
                f.write(str(next_id))
            
            logger.info(f"Current problem ID updated from {current_id} to {next_id}")
            return next_id
            
        except FileNotFoundError:
            logger.error("current_problem.txt file not found")
            return None
        except ValueError:
            logger.error("Invalid format in current_problem.txt")
            return None
        except Exception as e:
            logger.error(f"Error reading/writing current_problem.txt: {e}")
            return None

    def format_problem_for_discord(self, problem: Dict) -> str:
        content = self.crawler.format_problem_for_discord(problem)
        if len(content) > 1950:
            content = content[:1950] + "..."
        return content

    def get_daily_challenge(self) -> Optional[int]:
        """Get a random problem for daily challenge"""
        return self.get_current_problem()
