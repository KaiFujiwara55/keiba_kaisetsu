#!/usr/bin/env python3
"""
DynamoDBテーブルを作成するスクリプト

競馬解説アプリのキャッシュ用テーブルを作成します。
"""
import boto3
from botocore.exceptions import ClientError
import sys


def create_dynamodb_table():
    """DynamoDBテーブルを作成"""
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
    table_name = 'keiba_cache'

    print("=== DynamoDBテーブル作成 ===\n")

    try:
        # 既存テーブルをチェック
        existing_tables = [table.name for table in dynamodb.tables.all()]
        if table_name in existing_tables:
            print(f"ℹ️  テーブル '{table_name}' は既に存在します。")

            # テーブル情報を表示
            table = dynamodb.Table(table_name)
            print(f"\n現在の設定:")
            print(f"  - テーブル名: {table.table_name}")
            print(f"  - 状態: {table.table_status}")
            print(f"  - アイテム数: {table.item_count}")
            print(f"  - サイズ: {table.table_size_bytes / 1024:.2f} KB")
            return

        # テーブル作成（複合キー: PK + SK）
        print(f"テーブル '{table_name}' を作成中...")

        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'PK',
                    'KeyType': 'HASH'  # パーティションキー
                },
                {
                    'AttributeName': 'SK',
                    'KeyType': 'RANGE'  # ソートキー
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'PK',
                    'AttributeType': 'S'  # String型
                },
                {
                    'AttributeName': 'SK',
                    'AttributeType': 'S'  # String型
                }
            ],
            # オンデマンド課金モード（無料枠: 読み250万回/月、書き25万回/月）
            BillingMode='PAY_PER_REQUEST',

            # または プロビジョンド課金モード（永続無料枠: 25RCU/25WCU）
            # BillingMode='PROVISIONED',
            # ProvisionedThroughput={
            #     'ReadCapacityUnits': 5,
            #     'WriteCapacityUnits': 5
            # },

            # TTL設定（オプション: 古いキャッシュを自動削除）
            Tags=[
                {
                    'Key': 'Project',
                    'Value': 'keiba-kaisetsu'
                },
                {
                    'Key': 'Environment',
                    'Value': 'production'
                }
            ]
        )

        # テーブル作成完了を待機
        print("テーブル作成中（約30秒）...")
        table.wait_until_exists()

        print(f"\n✅ テーブル '{table_name}' の作成が完了しました。")
        print(f"\nテーブル情報:")
        print(f"  - ARN: {table.table_arn}")
        print(f"  - 状態: {table.table_status}")
        print(f"  - 課金モード: オンデマンド")
        print(f"\n無料枠:")
        print(f"  - 読み取り: 月250万リクエスト（最初の12ヶ月）")
        print(f"  - 書き込み: 月25万リクエスト（最初の12ヶ月）")
        print(f"  - ストレージ: 月25GB（永続）")

    except ClientError as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)


def delete_dynamodb_table():
    """DynamoDBテーブルを削除（クリーンアップ用）"""
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
    table_name = 'keiba_cache'

    print(f"=== DynamoDBテーブル削除: {table_name} ===\n")

    try:
        table = dynamodb.Table(table_name)

        # 確認
        response = input(f"本当に '{table_name}' を削除しますか？ (yes/no): ")
        if response.lower() != 'yes':
            print("削除をキャンセルしました。")
            return

        print(f"テーブル '{table_name}' を削除中...")
        table.delete()

        print("削除処理中（約30秒）...")
        table.wait_until_not_exists()

        print(f"✅ テーブル '{table_name}' を削除しました。\n")

    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"ℹ️  テーブル '{table_name}' が見つかりません。\n")
        else:
            print(f"❌ エラー: {e}\n")
            sys.exit(1)


def list_table_items():
    """テーブル内のアイテムを一覧表示（デバッグ用）"""
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
    table_name = 'keiba_cache'

    try:
        table = dynamodb.Table(table_name)
        response = table.scan(Limit=10)  # 最初の10件のみ

        print(f"=== {table_name} のアイテム（最大10件）===\n")

        if not response['Items']:
            print("アイテムがありません。")
        else:
            for item in response['Items']:
                print(f"キー: {item.get('key', 'N/A')}")
                print(f"  - タイムスタンプ: {item.get('timestamp', 'N/A')}")
                print(f"  - データサイズ: {len(str(item))} bytes")
                print()

        print(f"合計アイテム数（概算）: {table.item_count}")

    except ClientError as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == 'delete':
            delete_dynamodb_table()
        elif sys.argv[1] == 'list':
            list_table_items()
        else:
            print("使用方法:")
            print("  python setup_dynamodb.py          # テーブル作成")
            print("  python setup_dynamodb.py delete   # テーブル削除")
            print("  python setup_dynamodb.py list     # アイテム一覧")
    else:
        create_dynamodb_table()
