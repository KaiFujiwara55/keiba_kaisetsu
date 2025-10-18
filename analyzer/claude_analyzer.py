"""
Claude 4.5 analyzer module for horse race analysis
Handles LLM interaction and response parsing.
"""

import os
import time
from typing import Dict, Optional
from anthropic import Anthropic
from .prompts import SYSTEM_PROMPT, create_user_prompt


class ClaudeAnalyzer:
    """Claude 4.5 based horse race analyzer"""

    # Claude 4.5 pricing (per 1 million tokens)
    # Source: https://www.anthropic.com/pricing
    PRICING = {
        'claude-sonnet-4-5-20250929': {
            'input': 3.0,    # $3.00 per 1M input tokens
            'output': 15.0   # $15.00 per 1M output tokens
        }
    }

    # Default pricing for unknown models
    DEFAULT_PRICING = {
        'input': 3.0,
        'output': 15.0
    }

    def __init__(self):
        """Initialize Claude analyzer with Anthropic client"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = Anthropic(api_key=api_key)

        # Load configuration from environment
        self.model = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-5-20250929')
        self.max_tokens = int(os.getenv('CLAUDE_MAX_TOKENS', '8000'))
        self.temperature = float(os.getenv('CLAUDE_TEMPERATURE', '0.7'))

    def analyze_horses(self, race_data: Dict, custom_prompt: str = "") -> Optional[Dict]:
        """
        Analyze horses using Claude 4.5

        Args:
            race_data: Dictionary containing race and horse information
            custom_prompt: Optional custom user instructions

        Returns:
            Dictionary containing:
            - raw_response: str - Full Claude response
            - individual_analysis: str - Individual horse analysis section
            - comparison: str - Horse comparison section
            - ranking: str - Ranking section
            - tokens_used: Dict - Token usage information
        """
        # Create prompt
        user_prompt = create_user_prompt(race_data, custom_prompt)

        # Log token estimate
        estimated_tokens = self._estimate_tokens(user_prompt)
        print(f"Estimated input tokens: {estimated_tokens}")

        try:
            start_time = time.time()

            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            elapsed_time = time.time() - start_time

            # Extract response
            raw_response = response.content[0].text

            # Log token usage
            usage = response.usage
            print(f"Token usage - Input: {usage.input_tokens}, Output: {usage.output_tokens}, Total: {usage.input_tokens + usage.output_tokens}")
            print(f"Response time: {elapsed_time:.2f}s")

            # Calculate cost
            cost_usd = self.calculate_cost(usage.input_tokens, usage.output_tokens)
            print(f"Estimated cost: ${cost_usd:.4f}")

            # Parse response into sections
            parsed = self._parse_response(raw_response)

            return {
                'raw_response': raw_response,
                'individual_analysis': parsed.get('individual', ''),
                'comparison': parsed.get('comparison', ''),
                'ranking': parsed.get('ranking', ''),
                'tokens_used': {
                    'input': usage.input_tokens,
                    'output': usage.output_tokens,
                    'total': usage.input_tokens + usage.output_tokens
                },
                'cost_usd': cost_usd,
                'response_time': elapsed_time
            }

        except Exception as e:
            print(f"Error calling Claude API: {e}")
            return None

    def _parse_response(self, response: str) -> Dict[str, str]:
        """
        Parse Claude response into sections

        Args:
            response: Raw Claude response text

        Returns:
            Dictionary with parsed sections
        """
        sections = {
            'individual': '',
            'comparison': '',
            'ranking': ''
        }

        # Split by main headers
        parts = response.split('##')

        for part in parts:
            part = part.strip()

            if not part:
                continue

            # Check section type
            if '1.' in part and '個別' in part:
                sections['individual'] = '##' + part

            elif '2.' in part and '比較' in part:
                sections['comparison'] = '##' + part

            elif '3.' in part and 'ランキング' in part or 'おすすめ' in part:
                sections['ranking'] = '##' + part

        return sections

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        # Claude's token counting is roughly:
        # 1 token ≈ 0.75 English words or 0.5 Japanese characters
        japanese_chars = sum(1 for c in text if ord(c) > 0x3000)
        other_chars = len(text) - japanese_chars
        estimated = (japanese_chars / 2) + (other_chars / 4)

        return int(estimated)

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate the cost in USD for a given token usage

        Args:
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used

        Returns:
            Total cost in USD
        """
        pricing = self.PRICING.get(self.model, self.DEFAULT_PRICING)

        # Calculate cost (pricing is per 1 million tokens)
        input_cost = (input_tokens / 1_000_000) * pricing['input']
        output_cost = (output_tokens / 1_000_000) * pricing['output']

        return input_cost + output_cost
