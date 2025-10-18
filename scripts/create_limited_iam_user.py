#!/usr/bin/env python3
"""
Streamlit Cloud用の最小権限IAMユーザーを作成するスクリプト

このスクリプトは以下を実行します:
1. 専用IAMユーザーの作成
2. DynamoDBの特定テーブルのみアクセス可能なポリシーを適用
3. アクセスキーの生成
"""
import boto3
import json
import sys


def create_limited_iam_user():
    """最小権限のIAMユーザーを作成"""
    iam = boto3.client('iam')
    user_name = 'streamlit-keiba-user'

    print("=== Streamlit Cloud用IAMユーザー作成 ===\n")

    # 1. IAMユーザー作成
    try:
        iam.create_user(UserName=user_name)
        print(f"✅ IAMユーザーを作成: {user_name}")
    except iam.exceptions.EntityAlreadyExistsException:
        print(f"ℹ️  既存のIAMユーザーを使用: {user_name}")
    except Exception as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)

    # 2. 最小権限ポリシーを作成
    # AWSアカウントIDを取得
    sts = boto3.client('sts')
    account_id = sts.get_caller_identity()['Account']

    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "KeibaKaisetsuDynamoDBAccess",
                "Effect": "Allow",
                "Action": [
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:Query",
                    "dynamodb:Scan"
                ],
                "Resource": f"arn:aws:dynamodb:ap-northeast-1:{account_id}:table/keiba_cache"
            }
        ]
    }

    policy_name = 'StreamlitDynamoDBAccessPolicy'

    try:
        # インラインポリシーをアタッチ
        iam.put_user_policy(
            UserName=user_name,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document)
        )
        print(f"✅ ポリシーを適用: {policy_name}")
        print(f"   - 許可されたテーブル: keiba_cache")
        print(f"   - 許可された操作: GetItem, PutItem, UpdateItem, Query, Scan")
        print(f"   - 禁止された操作: DeleteItem, DeleteTable など")
    except Exception as e:
        print(f"❌ ポリシー適用エラー: {e}")
        sys.exit(1)

    # 3. アクセスキー作成
    print("\n--- アクセスキー作成 ---")
    try:
        # 既存のアクセスキーを確認
        existing_keys = iam.list_access_keys(UserName=user_name)
        if len(existing_keys['AccessKeyMetadata']) >= 2:
            print("⚠️  このユーザーは既に2つのアクセスキーを持っています。")
            print("   新しいキーを作成するには、古いキーを削除してください:\n")
            for key in existing_keys['AccessKeyMetadata']:
                print(f"   aws iam delete-access-key --user-name {user_name} --access-key-id {key['AccessKeyId']}")
            sys.exit(1)

        response = iam.create_access_key(UserName=user_name)
        access_key = response['AccessKey']

        print("✅ アクセスキーを作成\n")
        print("=" * 60)
        print("以下をStreamlit Cloudの Secrets に保存してください:")
        print("=" * 60)
        print("\n[aws]")
        print(f'region = "ap-northeast-1"')
        print(f'access_key_id = "{access_key["AccessKeyId"]}"')
        print(f'secret_access_key = "{access_key["SecretAccessKey"]}"')
        print("\n[dynamodb]")
        print('table_name = "keiba_cache"')
        print("\n" + "=" * 60)
        print("\n⚠️  重要: このシークレットアクセスキーは二度と表示されません。")
        print("   安全な場所に保存してください。\n")

    except iam.exceptions.LimitExceededException:
        print("❌ アクセスキーの上限に達しています。")
        print("   既存のキーを削除してから再実行してください:")
        print(f"   aws iam list-access-keys --user-name {user_name}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ アクセスキー作成エラー: {e}")
        sys.exit(1)

    print("\n=== セットアップ完了 ===\n")


def delete_iam_user():
    """IAMユーザーを削除（クリーンアップ用）"""
    iam = boto3.client('iam')
    user_name = 'streamlit-keiba-user'

    print(f"=== IAMユーザー削除: {user_name} ===\n")

    try:
        # アクセスキーを削除
        keys = iam.list_access_keys(UserName=user_name)
        for key in keys['AccessKeyMetadata']:
            iam.delete_access_key(
                UserName=user_name,
                AccessKeyId=key['AccessKeyId']
            )
            print(f"✅ アクセスキーを削除: {key['AccessKeyId']}")

        # インラインポリシーを削除
        policies = iam.list_user_policies(UserName=user_name)
        for policy_name in policies['PolicyNames']:
            iam.delete_user_policy(
                UserName=user_name,
                PolicyName=policy_name
            )
            print(f"✅ ポリシーを削除: {policy_name}")

        # ユーザーを削除
        iam.delete_user(UserName=user_name)
        print(f"✅ IAMユーザーを削除: {user_name}\n")

    except iam.exceptions.NoSuchEntityException:
        print(f"ℹ️  ユーザーが見つかりません: {user_name}\n")
    except Exception as e:
        print(f"❌ エラー: {e}\n")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'delete':
        delete_iam_user()
    else:
        create_limited_iam_user()
