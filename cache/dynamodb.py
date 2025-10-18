"""
DynamoDB cache module for storing and retrieving scraped data
Implements TTL-based caching with single table design.
"""

import os
import time
import json
import hashlib
from typing import Optional, Dict, Any
from decimal import Decimal
import boto3
from botocore.exceptions import ClientError


class DynamoDBCache:
    """DynamoDB cache implementation with TTL support"""

    @staticmethod
    def _convert_floats_to_decimal(obj: Any) -> Any:
        """
        Recursively convert all float values to Decimal for DynamoDB compatibility

        Args:
            obj: Object to convert (can be dict, list, or primitive)

        Returns:
            Converted object with floats replaced by Decimals
        """
        if isinstance(obj, list):
            return [DynamoDBCache._convert_floats_to_decimal(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: DynamoDBCache._convert_floats_to_decimal(value) for key, value in obj.items()}
        elif isinstance(obj, float):
            return Decimal(str(obj))
        else:
            return obj

    def __init__(self):
        """Initialize DynamoDB client"""
        # Streamlit Cloud対応: st.secretsから認証情報を取得
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'aws' in st.secrets:
                # Streamlit Cloudで実行中
                self.region = st.secrets.get('aws', {}).get('region', 'ap-northeast-1')
                self.table_name = st.secrets.get('dynamodb', {}).get('table_name', 'keiba_cache')
                aws_access_key_id = st.secrets['aws']['access_key_id']
                aws_secret_access_key = st.secrets['aws']['secret_access_key']

                # AWS認証情報を使用してDynamoDBクライアントを初期化
                self.dynamodb = boto3.resource(
                    'dynamodb',
                    region_name=self.region,
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key
                )
            else:
                # ローカル環境（環境変数から取得）
                self.region = os.getenv('AWS_REGION', 'ap-northeast-1')
                self.table_name = os.getenv('DYNAMODB_TABLE', 'keiba_cache')
                self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
        except ImportError:
            # Streamlitがインストールされていない環境
            self.region = os.getenv('AWS_REGION', 'ap-northeast-1')
            self.table_name = os.getenv('DYNAMODB_TABLE', 'keiba_cache')
            self.dynamodb = boto3.resource('dynamodb', region_name=self.region)

        self.ttl_seconds = int(os.getenv('CACHE_TTL_SECONDS', '604800'))  # 7 days default
        self.table = self.dynamodb.Table(self.table_name)

    def get(self, partition_key: str, sort_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve data from cache

        Args:
            partition_key: Primary partition key (PK)
            sort_key: Sort key (SK)

        Returns:
            Cached data dictionary or None if not found/expired
        """
        try:
            response = self.table.get_item(
                Key={
                    'PK': partition_key,
                    'SK': sort_key
                }
            )

            if 'Item' not in response:
                return None

            item = response['Item']

            # Check if item is expired (manual check in addition to TTL)
            if 'ttl' in item:
                current_time = int(time.time())
                if item['ttl'] < current_time:
                    print(f"Cache expired for {partition_key}#{sort_key}")
                    return None

            # Return the data field
            if 'data' in item:
                return item['data']

            return None

        except ClientError as e:
            print(f"Error retrieving from cache: {e}")
            return None

        except Exception as e:
            print(f"Unexpected error retrieving from cache: {e}")
            return None

    def set(self, partition_key: str, sort_key: str, data: Dict[str, Any]) -> bool:
        """
        Store data in cache with TTL

        Args:
            partition_key: Primary partition key (PK)
            sort_key: Sort key (SK)
            data: Data to store

        Returns:
            True if successful, False otherwise
        """
        try:
            current_time = int(time.time())
            ttl = current_time + self.ttl_seconds

            # Convert all floats to Decimal for DynamoDB compatibility
            converted_data = self._convert_floats_to_decimal(data)

            item = {
                'PK': partition_key,
                'SK': sort_key,
                'data': converted_data,
                'fetched_at': current_time,
                'ttl': ttl
            }

            self.table.put_item(Item=item)

            return True

        except ClientError as e:
            print(f"Error storing to cache: {e}")
            return False

        except Exception as e:
            print(f"Unexpected error storing to cache: {e}")
            return False

    def delete(self, partition_key: str, sort_key: str) -> bool:
        """
        Delete data from cache

        Args:
            partition_key: Primary partition key (PK)
            sort_key: Sort key (SK)

        Returns:
            True if successful, False otherwise
        """
        try:
            self.table.delete_item(
                Key={
                    'PK': partition_key,
                    'SK': sort_key
                }
            )

            return True

        except ClientError as e:
            print(f"Error deleting from cache: {e}")
            return False

        except Exception as e:
            print(f"Unexpected error deleting from cache: {e}")
            return False

    # Convenience methods for specific data types

    def get_race_ids(self, date: str, track: str) -> Optional[Dict]:
        """Get race IDs for a specific date and track"""
        pk = f"RACE#{date}#{track}"
        sk = "IDS"
        return self.get(pk, sk)

    def set_race_ids(self, date: str, track: str, race_ids: Dict) -> bool:
        """Store race IDs for a specific date and track"""
        pk = f"RACE#{date}#{track}"
        sk = "IDS"
        return self.set(pk, sk, race_ids)

    def get_race_metadata(self, race_id: str) -> Optional[Dict]:
        """Get race metadata by race ID"""
        pk = f"RACE#{race_id}"
        sk = "METADATA"
        return self.get(pk, sk)

    def set_race_metadata(self, race_id: str, metadata: Dict) -> bool:
        """Store race metadata"""
        pk = f"RACE#{race_id}"
        sk = "METADATA"
        return self.set(pk, sk, metadata)

    def get_horse_results(self, horse_id: str) -> Optional[Dict]:
        """Get horse race results by horse ID"""
        pk = f"HORSE#{horse_id}"
        sk = "RESULTS"
        return self.get(pk, sk)

    def set_horse_results(self, horse_id: str, results: Dict) -> bool:
        """Store horse race results"""
        pk = f"HORSE#{horse_id}"
        sk = "RESULTS"
        return self.set(pk, sk, results)

    def get_horse_parents(self, horse_id: str) -> Optional[Dict]:
        """Get parent horse information"""
        pk = f"HORSE#{horse_id}"
        sk = "PARENT"
        return self.get(pk, sk)

    def set_horse_parents(self, horse_id: str, parents: Dict) -> bool:
        """Store parent horse information"""
        pk = f"HORSE#{horse_id}"
        sk = "PARENT"
        return self.set(pk, sk, parents)

    def get_jockey_stats(self, jockey_id: str) -> Optional[Dict]:
        """Get jockey statistics"""
        pk = f"JOCKEY#{jockey_id}"
        sk = "STATS"
        return self.get(pk, sk)

    def set_jockey_stats(self, jockey_id: str, stats: Dict) -> bool:
        """Store jockey statistics"""
        pk = f"JOCKEY#{jockey_id}"
        sk = "STATS"
        return self.set(pk, sk, stats)

    def _generate_prompt_hash(self, custom_prompt: str) -> str:
        """
        Generate a hash for custom prompt

        Args:
            custom_prompt: Custom prompt string (empty string if no custom prompt)

        Returns:
            MD5 hash of the prompt (or "default" if empty)
        """
        if not custom_prompt or custom_prompt.strip() == "":
            return "default"

        # Generate MD5 hash of the prompt
        return hashlib.md5(custom_prompt.encode('utf-8')).hexdigest()

    def get_llm_analysis(self, race_id: str, custom_prompt: str = "") -> Optional[Dict]:
        """
        Get cached LLM analysis result

        Args:
            race_id: Race identifier
            custom_prompt: Custom prompt used for analysis (empty string if none)

        Returns:
            Cached analysis result or None if not found/expired
        """
        prompt_hash = self._generate_prompt_hash(custom_prompt)
        pk = f"ANALYSIS#{race_id}"
        sk = f"PROMPT#{prompt_hash}"
        return self.get(pk, sk)

    def set_llm_analysis(self, race_id: str, custom_prompt: str, analysis_result: Dict) -> bool:
        """
        Store LLM analysis result in cache

        Args:
            race_id: Race identifier
            custom_prompt: Custom prompt used for analysis (empty string if none)
            analysis_result: Complete analysis result including raw_response, tokens_used, cost_usd

        Returns:
            True if successful, False otherwise
        """
        prompt_hash = self._generate_prompt_hash(custom_prompt)
        pk = f"ANALYSIS#{race_id}"
        sk = f"PROMPT#{prompt_hash}"

        # Store the analysis result with metadata
        data = {
            'analysis_result': analysis_result,
            'custom_prompt': custom_prompt,
            'prompt_hash': prompt_hash
        }

        return self.set(pk, sk, data)
