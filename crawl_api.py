import logging
import re
import time
from typing import Dict, List, Optional

import requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LeetCodeAPICrawler:
    def __init__(self):
        self.session = requests.Session()
        self.graphql_url = "https://leetcode.com/graphql"

        # Optimized headers
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Origin": "https://leetcode.com",
                "Referer": "https://leetcode.com/",
            }
        )

        # Cache for problem list
        self._problem_list_cache = None
        self._cache_timestamp = 0
        self._cache_duration = 300  # 5 minutes

    def _extract_slug_from_url(self, url: str) -> Optional[str]:
        """Extract problem slug from URL"""
        if "?" in url:
            url = url.split("?")[0]

        path_parts = url.split("/")
        for i, part in enumerate(path_parts):
            if part == "problems" and i + 1 < len(path_parts):
                return path_parts[i + 1]
        return None

    def _make_graphql_request(self, query: str, variables: Dict) -> Optional[Dict]:
        """Make GraphQL request with error handling"""
        try:
            payload = {"query": query, "variables": variables}
            response = self.session.post(self.graphql_url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"GraphQL request failed: {str(e)}")
            return None

    def get_problem_content(self, problem_url: str) -> Optional[Dict]:
        """Get problem content using GraphQL API"""
        slug = self._extract_slug_from_url(problem_url)
        if not slug:
            logger.error(f"Could not extract slug from URL: {problem_url}")
            return None

        logger.info(f"Fetching problem data for slug: {slug}")

        query = """
        query questionData($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionId, title, titleSlug, difficulty, content,
                exampleTestcases, topicTags { name, slug }, hints
            }
        }
        """

        data = self._make_graphql_request(query, {"titleSlug": slug})
        if not data or "data" not in data or not data["data"]["question"]:
            logger.error(f"No data found for slug: {slug}")
            return None
        return self._format_problem_data(data["data"]["question"], problem_url)

    def _extract_constraints(self, content: str) -> List[str]:
        """Extract constraints from content, chuyển <code>...</code> thành `...` và xử lý <sup>"""
        # Updated pattern to stop at Follow up section as well
        pattern = r"<strong>Constraints:</strong>(.*?)(?=<strong>Follow up:|<strong[^>]*class=\"example\"|$)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if not match:
            return []
            
        constraints_text = match.group(1)
        
        # Tách từng constraint từ <li> tags
        constraints = []
        li_matches = re.findall(r"<li>(.*?)</li>", constraints_text, re.DOTALL)
        
        for item in li_matches:
            # Xử lý <sup> và <code> tags trước khi xóa HTML
            clean_item = re.sub(r"<sup>(.*?)</sup>", r"^\1", item, flags=re.DOTALL)
            clean_item = re.sub(r"<code>(.*?)</code>", r"`\1`", clean_item, flags=re.DOTALL)
            
            # Xóa các HTML tags còn lại và xử lý entities
            clean_item = self._clean_text(clean_item)
            
            if clean_item:
                constraints.append(clean_item)
        
        # Nếu không có <li>, thử tách theo dòng
        if not constraints:
            # Xử lý <sup> và <code> tags
            clean_text = re.sub(r"<sup>(.*?)</sup>", r"^\1", constraints_text, flags=re.DOTALL)
            clean_text = re.sub(r"<code>(.*?)</code>", r"`\1`", clean_text, flags=re.DOTALL)
            clean_text = self._clean_text(clean_text)
            
            constraints = [
                line.strip() for line in clean_text.split("\n") 
                if line.strip() and not line.strip().startswith("&")
            ]
        
        return constraints

    def _extract_follow_up(self, content: str) -> Optional[str]:
        """Extract Follow up section from content"""
        # More specific pattern to capture everything after Follow up until end of content
        pattern = r"<strong>Follow up:</strong>\s*(.*?)(?:</p>|$)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if not match:
            return None
            
        follow_up_text = match.group(1).strip()
        return self._clean_text(follow_up_text) if follow_up_text else None

    def _html_to_markdown(self, html_content: str) -> str:
        """Convert HTML to markdown, tối ưu cho Discord"""
        if not html_content:
            return ""

        markdown = html_content

        # 1. Xử lý entity HTML (cần làm trước các thao tác khác)
        html_entities = [
            (r"&nbsp;", " "),
            (r"&lt;", "<"),
            (r"&gt;", ">"),
            (r"&le;", "≤"),
            (r"&ge;", "≥"),
            (r"&quot;", '"'),
            (r"&#39;", "'"),  # Single quote
            (r"&amp;", "&"),  # Phải làm cuối cùng để tránh conflict
        ]
        for pattern, repl in html_entities:
            markdown = re.sub(pattern, repl, markdown)

        # 2. Chuyển <sup>...</sup> thành ^...
        markdown = re.sub(r"<sup>(.*?)</sup>", r"^\1", markdown, flags=re.DOTALL)

        # 3. Chuyển <strong class="example">Example X:</strong> thành ### Example X
        markdown = re.sub(
            r'<strong[^>]*class="example"[^>]*>(.*?)</strong>',
            r"\n### \1\n",
            markdown,
            flags=re.IGNORECASE,
        )

        # 4. Chuyển <strong>Follow up:</strong> thành **Follow up:**
        markdown = re.sub(
            r'<strong>Follow up:</strong>',
            r"\n**Follow up:**",
            markdown,
            flags=re.IGNORECASE,
        )

        # 5. Chuyển <img ... src="..."> thành ![image](url)
        markdown = re.sub(
            r'<img [^>]*src="([^"]+)"[^>]*>', r"\n![image](\1)\n", markdown
        )

        # 6. Chuyển <ul>...</ul> và <li>...</li> thành list markdown
        markdown = re.sub(r"<ul>", "", markdown)
        markdown = re.sub(r"</ul>", "", markdown)
        markdown = re.sub(r"<li>(.*?)</li>", r"- \1", markdown, flags=re.DOTALL)

        # 7. Chuyển <pre>...</pre> thành code block
        markdown = re.sub(
            r"<pre>(.*?)</pre>",
            lambda m: f"\n```\n{m.group(1).strip()}\n```\n",
            markdown,
            flags=re.DOTALL,
        )

        # 8. Chuyển <code>...</code> thành inline code
        markdown = re.sub(r"<code>(.*?)</code>", r"`\1`", markdown, flags=re.DOTALL)

        # 9. Chuyển <strong>...</strong> thành **...** (trừ example đã xử lý ở trên)
        markdown = re.sub(
            r"<strong>(.*?)</strong>", r"**\1**", markdown, flags=re.DOTALL
        )

        # 10. Chuyển <em>...</em> thành *...*
        markdown = re.sub(r"<em>(.*?)</em>", r"*\1*", markdown, flags=re.DOTALL)

        # 11. Xóa các thẻ còn lại (<p>, <div>, <span>, ...)
        markdown = re.sub(r"<[^>]+>", "", markdown)

        # 12. Làm sạch nhiều dòng trống liên tiếp
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)
        markdown = markdown.strip()

        return markdown

    def _extract_description(self, content: str) -> str:
        """Extract only the description part (before examples)"""
        # Find the first example to know where description ends
        example_pattern = r'<strong[^>]*class="example"[^>]*>Example\s*\d+:</strong>'
        match = re.search(example_pattern, content, re.IGNORECASE)
        
        if match:
            # Get content before the first example
            description_content = content[:match.start()].strip()
        else:
            # If no examples found, use the whole content
            description_content = content
        
        # Convert to markdown
        return self._html_to_markdown(description_content)

    def _format_problem_data(self, question: Dict, original_url: str) -> Dict:
        """Format API response into standard format"""
        content = question.get("content", "")

        return {
            "id": question.get("questionId"),
            "slug": question.get("titleSlug"),
            "title": question.get("title"),
            "difficulty": question.get("difficulty"),
            "description": self._extract_description(content),
            "examples": self._extract_examples(content),
            "constraints": self._extract_constraints(content),
            "follow_up": self._extract_follow_up(content),
            "topics": [tag["name"] for tag in question.get("topicTags", [])],
            "hints": question.get("hints", []),
            "time_complexity": "O(n)",
            "space_complexity": "O(1)",
            "url": original_url,
            "markdown": self._html_to_markdown(content),
        }

    def _clean_text(self, text: str) -> str:
        """Clean text by removing HTML tags and converting entities"""
        if not text:
            return text
            
        # Xóa HTML tags
        clean_text = re.sub(r"<[^>]+>", "", text)
        
        # Xử lý HTML entities
        html_entities = [
            (r"&nbsp;", " "),
            (r"&lt;", "<"),
            (r"&gt;", ">"),
            (r"&le;", "≤"),
            (r"&ge;", "≥"),
            (r"&quot;", '"'),
            (r"&#39;", "'"),  # Single quote
            (r"&amp;", "&"),
        ]
        for pattern, repl in html_entities:
            clean_text = re.sub(pattern, repl, clean_text)
            
        return clean_text.strip()

    def _extract_examples(self, content: str) -> List[Dict]:
        """Extract examples from content, tách input/output/explanation/ảnh"""
        examples = []
        
        # Updated pattern to match <strong class="example">Example X:</strong>
        pattern = r'<strong[^>]*class="example"[^>]*>Example\s*(\d+):</strong>(.*?)(?=<strong[^>]*class="example"|<strong>Constraints:|$)'
        
        for num, example_content in re.findall(pattern, content, re.DOTALL | re.IGNORECASE):
            # Tìm ảnh trong example
            img_match = re.search(r'<img [^>]*src="([^"]+)"[^>]*>', example_content)
            img_url = img_match.group(1) if img_match else None
            
            # Xóa thẻ img khỏi example_content
            example_content = re.sub(r'<img [^>]*src="([^"]+)"[^>]*>', "", example_content)
            
            # Tách input/output/explanation từ <pre> blocks
            input_val = None
            output_val = None
            explanation_val = None
            
            # Tìm content trong <pre> tag
            pre_match = re.search(r'<pre>(.*?)</pre>', example_content, re.DOTALL)
            if pre_match:
                pre_content = pre_match.group(1)
                
                # Tách Input
                input_match = re.search(r'<strong>Input:</strong>\s*(.+?)(?=<strong>|$)', pre_content, re.DOTALL)
                if input_match:
                    input_val = self._clean_text(input_match.group(1))
                
                # Tách Output
                output_match = re.search(r'<strong>Output:</strong>\s*(.+?)(?=<strong>|$)', pre_content, re.DOTALL)
                if output_match:
                    output_val = self._clean_text(output_match.group(1))
                
                # Tách Explanation
                explanation_match = re.search(r'<strong>Explanation:</strong>\s*(.+?)(?=<strong>|$)', pre_content, re.DOTALL)
                if explanation_match:
                    explanation_val = self._clean_text(explanation_match.group(1))
            
            # Nếu không tách được từ <pre>, thử tách trực tiếp
            if not (input_val or output_val or explanation_val):
                input_match = re.search(r'<strong>Input:</strong>\s*(.*?)(?=<strong>|$)', example_content, re.DOTALL)
                output_match = re.search(r'<strong>Output:</strong>\s*(.*?)(?=<strong>|$)', example_content, re.DOTALL)
                explanation_match = re.search(r'<strong>Explanation:</strong>\s*(.*?)(?=<strong>|$)', example_content, re.DOTALL)
                
                input_val = self._clean_text(input_match.group(1)) if input_match else None
                output_val = self._clean_text(output_match.group(1)) if output_match else None
                explanation_val = self._clean_text(explanation_match.group(1)) if explanation_match else None
            
            # Nếu vẫn không tách được, để raw
            if not (input_val or output_val or explanation_val):
                raw = self._html_to_markdown(example_content.strip())
            else:
                raw = None
            
            examples.append({
                "title": f"Example {num}",
                "input": input_val,
                "output": output_val,
                "explanation": explanation_val,
                "image": img_url,
                "raw": raw,
            })
        
        return examples

    def format_problem_for_discord(self, problem: Dict) -> str:
        """Format problem for Discord display (markdown đẹp, không code block cho example, ảnh preview được)"""
        difficulty_emoji = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}
        diff_emoji = difficulty_emoji.get(problem.get("difficulty", "Unknown"), "⚪")
        embed = f"## {diff_emoji} {problem['title']}\n\n"
        embed += f"**Difficulty:** {problem.get('difficulty', 'Unknown')}\n"
        embed += f"**Topics:** {', '.join(problem.get('topics', []))}\n"
        embed += f"**URL:** {problem.get('url', 'N/A')}\n\n"
        
        # Add description (truncated if too long)
        description = problem.get("description", "")
        if len(description) > 1000:
            description = description[:1000] + "..."
        embed += f"**Description:**\n{description}\n\n"
        
        # Add examples (markdown đẹp, không code block)
        examples = problem.get("examples", [])
        if examples:
            for ex in examples:
                embed += f"### {ex['title']}\n\n"
                if ex.get("image"):
                    embed += f"![image]({ex['image']})\n\n"
                if ex.get("input"):
                    embed += f"**Input:** {ex['input']}  \n"
                if ex.get("output"):
                    embed += f"**Output:** {ex['output']}  \n"
                if ex.get("explanation"):
                    embed += f"**Explanation:** {ex['explanation']}  \n"
                if ex.get("raw"):
                    embed += ex["raw"] + "\n"
                embed += "\n"
        
        # Add constraints (chỉ một section, markdown list)
        constraints = problem.get("constraints", [])
        if constraints:
            embed += "**Constraints:**\n"
            for constraint in constraints:
                embed += f"- {constraint}\n"
            embed += "\n"
        
        # Add follow up section if exists
        follow_up = problem.get("follow_up")
        if follow_up:
            embed += f"**Follow up:** {follow_up}\n"
        
        return embed

    def get_problem_list(self, limit: int = 50) -> List[Dict]:
        """Get problem list with caching"""
        current_time = time.time()

        # Return cached data if still valid
        if (
            self._problem_list_cache
            and current_time - self._cache_timestamp < self._cache_duration
        ):
            return self._problem_list_cache[:limit]

        query = """
        query problemsetQuestionList($limit: Int, $skip: Int) {
            problemsetQuestionList: questionList(limit: $limit, skip: $skip) {
                questions: data {
                    title, titleSlug, difficulty, topicTags { name }
                }
            }
        }
        """

        data = self._make_graphql_request(query, {"limit": limit, "skip": 0})
        if not data or "data" not in data:
            return []

        questions = data["data"]["problemsetQuestionList"]["questions"]

        # Cache the results
        self._problem_list_cache = questions
        self._cache_timestamp = current_time

        return questions
