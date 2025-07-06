#!/usr/bin/env python3

from crawl_api import LeetCodeAPICrawler
import json

# Test data from user
test_data = {'data': {'question': {'questionId': '53', 'title': 'Maximum Subarray', 'titleSlug': 'maximum-subarray', 'difficulty': 'Medium', 'content': '<p>Given an integer array <code>nums</code>, find the <span data-keyword="subarray-nonempty">subarray</span> with the largest sum, and return <em>its sum</em>.</p>\n\n<p>&nbsp;</p>\n<p><strong class="example">Example 1:</strong></p>\n\n<pre>\n<strong>Input:</strong> nums = [-2,1,-3,4,-1,2,1,-5,4]\n<strong>Output:</strong> 6\n<strong>Explanation:</strong> The subarray [4,-1,2,1] has the largest sum 6.\n</pre>\n\n<p><strong class="example">Example 2:</strong></p>\n\n<pre>\n<strong>Input:</strong> nums = [1]\n<strong>Output:</strong> 1\n<strong>Explanation:</strong> The subarray [1] has the largest sum 1.\n</pre>\n\n<p><strong class="example">Example 3:</strong></p>\n\n<pre>\n<strong>Input:</strong> nums = [5,4,-1,7,8]\n<strong>Output:</strong> 23\n<strong>Explanation:</strong> The subarray [5,4,-1,7,8] has the largest sum 23.\n</pre>\n\n<p>&nbsp;</p>\n<p><strong>Constraints:</strong></p>\n\n<ul>\n\t<li><code>1 &lt;= nums.length &lt;= 10<sup>5</sup></code></li>\n\t<li><code>-10<sup>4</sup> &lt;= nums[i] &lt;= 10<sup>4</sup></code></li>\n</ul>\n\n<p>&nbsp;</p>\n<p><strong>Follow up:</strong> If you have figured out the <code>O(n)</code> solution, try coding another solution using the <strong>divide and conquer</strong> approach, which is more subtle.</p>\n', 'exampleTestcases': '[-2,1,-3,4,-1,2,1,-5,4]\n[1]\n[5,4,-1,7,8]', 'topicTags': [{'name': 'Array', 'slug': 'array'}, {'name': 'Divide and Conquer', 'slug': 'divide-and-conquer'}, {'name': 'Dynamic Programming', 'slug': 'dynamic-programming'}], 'hints': []}}}


def test_functions():
    crawler = LeetCodeAPICrawler()
    question = test_data['data']['question']
    
    # Test _format_problem_data
    print("=== Testing _format_problem_data ===")
    formatted = crawler._format_problem_data(question, "https://leetcode.com/problems/maximum-subarray/")
    print(f"Title: {formatted['title']}")
    print(f"Difficulty: {formatted['difficulty']}")
    print(f"Topics: {formatted['topics']}")
    print(f"Number of examples: {len(formatted['examples'])}")
    print(f"Number of constraints: {len(formatted['constraints'])}")
    print(f"Follow up: {formatted.get('follow_up', 'None')}")
    print()
    
    # Test _extract_examples
    print("=== Testing _extract_examples ===")
    examples = crawler._extract_examples(question['content'])
    for i, example in enumerate(examples):
        print(f"Example {i+1}:")
        print(f"  Title: {example['title']}")
        print(f"  Input: {example['input']}")
        print(f"  Output: {example['output']}")
        print(f"  Explanation: {example['explanation']}")
        print(f"  Raw: {example['raw']}")
        print()
    
    # Test _extract_constraints
    print("=== Testing _extract_constraints ===")
    constraints = crawler._extract_constraints(question['content'])
    for i, constraint in enumerate(constraints):
        print(f"Constraint {i+1}: {constraint}")
    print()
    
    # Test _extract_follow_up
    print("=== Testing _extract_follow_up ===")
    follow_up = crawler._extract_follow_up(question['content'])
    print(f"Follow up: {follow_up}")
    print()
    
    # Test _html_to_markdown
    print("=== Testing _html_to_markdown ===")
    markdown = crawler._html_to_markdown(question['content'])
    print("Markdown output:")
    print(markdown)
    print()
    
    # Test complete format for Discord
    print("=== Testing format_problem_for_discord ===")
    discord_format = crawler.format_problem_for_discord(formatted)
    print(discord_format)

if __name__ == "__main__":
    test_functions() 