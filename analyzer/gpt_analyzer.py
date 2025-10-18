"""
GPT-5 analyzer module for horse race analysis
Handles LLM interaction and response parsing.
"""

import os
import time
from typing import Dict, Optional
from openai import OpenAI
from .prompts import SYSTEM_PROMPT, create_user_prompt

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


class GPTAnalyzer:
    """GPT-5 based horse race analyzer"""

    # GPT-5 pricing (per 1 million tokens)
    # Source: https://openai.com/api/pricing/
    PRICING = {
        'gpt-5': {
            'input': 1.25,    # $1.25 per 1M input tokens
            'output': 10.0    # $10.00 per 1M output tokens
        }
    }

    def __init__(self):
        """Initialize GPT analyzer with OpenAI client"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = OpenAI(api_key=api_key)

        # Load configuration from environment
        self.model = "gpt-5"
        self.max_input_tokens = int(os.getenv('GPT5_MAX_INPUT_TOKENS', '250000'))
        self.max_output_tokens = int(os.getenv('GPT5_MAX_OUTPUT_TOKENS', '8000'))
        self.reasoning_effort = os.getenv('GPT5_REASONING_EFFORT', 'medium')
        self.temperature = 0.7

    def analyze_horses(self, race_data: Dict, custom_prompt: str = "") -> Optional[Dict]:
        """
        Analyze horses using GPT-5

        Args:
            race_data: Dictionary containing race and horse information
            custom_prompt: Optional custom user instructions

        Returns:
            Dictionary containing:
            - raw_response: str - Full GPT-5 response
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

        if estimated_tokens > self.max_input_tokens:
            print(f"Warning: Input may exceed token limit ({self.max_input_tokens})")

        try:
            start_time = time.time()

            # Call GPT-5 API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_completion_tokens=self.max_output_tokens,
                reasoning_effort=self.reasoning_effort
            )

            elapsed_time = time.time() - start_time

            # Extract response
            raw_response = response.choices[0].message.content

            # Log token usage
            usage = response.usage
            print(f"Token usage - Input: {usage.prompt_tokens}, Output: {usage.completion_tokens}, Total: {usage.total_tokens}")
            print(f"Response time: {elapsed_time:.2f}s")

            # Calculate cost
            cost_usd = self.calculate_cost(usage.prompt_tokens, usage.completion_tokens)
            print(f"Estimated cost: ${cost_usd:.4f}")

            # Parse response into sections
            parsed = self._parse_response(raw_response)

            return {
                'raw_response': raw_response,
                'individual_analysis': parsed.get('individual', ''),
                'comparison': parsed.get('comparison', ''),
                'ranking': parsed.get('ranking', ''),
                'tokens_used': {
                    'input': usage.prompt_tokens,
                    'output': usage.completion_tokens,
                    'total': usage.total_tokens
                },
                'cost_usd': cost_usd,
                'response_time': elapsed_time
            }

        except Exception as e:
            print(f"Error calling GPT-5 API: {e}")
            return None

    def _parse_response(self, response: str) -> Dict[str, str]:
        """
        Parse GPT-5 response into sections

        Args:
            response: Raw GPT-5 response text

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
        Estimate token count for text using tiktoken if available

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        if TIKTOKEN_AVAILABLE:
            try:
                # Use o200k_base encoding (used by GPT-4o and newer models)
                # Falls back to cl100k_base if o200k_base is not available
                try:
                    encoding = tiktoken.get_encoding("o200k_base")
                except Exception:
                    encoding = tiktoken.get_encoding("cl100k_base")

                return len(encoding.encode(text))
            except Exception as e:
                print(f"Tiktoken encoding failed, using fallback: {e}")

        # Fallback: Rough estimate for Japanese text
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
        pricing = self.PRICING.get(self.model, self.PRICING['gpt-5'])

        # Calculate cost (pricing is per 1 million tokens)
        input_cost = (input_tokens / 1_000_000) * pricing['input']
        output_cost = (output_tokens / 1_000_000) * pricing['output']

        return input_cost + output_cost
