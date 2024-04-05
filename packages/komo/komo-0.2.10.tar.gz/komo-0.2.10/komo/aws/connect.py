import json

import boto3
import botocore

from komo import printing
from komo.api_client import APIClient
from komo.types import ClientException


def connect():
    api_client = APIClient()
    user_id = api_client.get_user_id()

    session = boto3.Session()
    iam_client = session.client("iam")
    sts_client = session.client("sts")
    try:
        aws_account_id = sts_client.get_caller_identity()["Account"]
    except botocore.exceptions.BotoCoreError as e:
        raise ClientException(
            "Unable to get AWS caller identity. Please ensure that you are logged in with AWS"
        )

    iam_role_name = f"komodo-iam-role-{user_id}"
    policy_name = f"komodo-iam-role-policy-{user_id}"
    policy_arn = f"arn:aws:iam::{aws_account_id}:policy/{policy_name}"

    try:
        try:
            role_response = iam_client.get_role(RoleName=iam_role_name)
        except iam_client.exceptions.NoSuchEntityException:
            printing.info(
                "Creating IAM Role to allow the Komodo server access to your account"
            )

            try:
                policy_response = iam_client.get_policy(PolicyArn=policy_arn)
            except iam_client.exceptions.NoSuchEntityException:
                policy_response = iam_client.create_policy(
                    PolicyName=policy_name,
                    PolicyDocument=json.dumps(
                        {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Action": "ec2:RunInstances",
                                    "Resource": "arn:aws:ec2:*::image/ami-*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": "ec2:RunInstances",
                                    "Resource": [
                                        f"arn:aws:ec2:*:{aws_account_id}:instance/*",
                                        f"arn:aws:ec2:*:{aws_account_id}:network-interface/*",
                                        f"arn:aws:ec2:*:{aws_account_id}:subnet/*",
                                        f"arn:aws:ec2:*:{aws_account_id}:volume/*",
                                        f"arn:aws:ec2:*:{aws_account_id}:security-group/*",
                                    ],
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "ec2:TerminateInstances",
                                        "ec2:DeleteTags",
                                        "ec2:StartInstances",
                                        "ec2:CreateTags",
                                        "ec2:StopInstances",
                                    ],
                                    "Resource": f"arn:aws:ec2:*:{aws_account_id}:instance/*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": ["ec2:Describe*"],
                                    "Resource": "*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "ec2:CreateSecurityGroup",
                                        "ec2:AuthorizeSecurityGroupIngress",
                                    ],
                                    "Resource": f"arn:aws:ec2:*:{aws_account_id}:*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "iam:GetRole",
                                        "iam:PassRole",
                                        "iam:CreateRole",
                                        "iam:AttachRolePolicy",
                                    ],
                                    "Resource": [
                                        f"arn:aws:iam::{aws_account_id}:role/skypilot-v1"
                                    ],
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "iam:GetInstanceProfile",
                                        "iam:CreateInstanceProfile",
                                        "iam:AddRoleToInstanceProfile",
                                    ],
                                    "Resource": f"arn:aws:iam::{aws_account_id}:instance-profile/skypilot-v1",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": "iam:CreateServiceLinkedRole",
                                    "Resource": "*",
                                    "Condition": {
                                        "StringEquals": {
                                            "iam:AWSServiceName": "spot.amazonaws.com"
                                        }
                                    },
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "ec2:DeleteSecurityGroup",
                                        "ec2:ModifyInstanceAttribute",
                                    ],
                                    "Resource": f"arn:aws:ec2:*:{aws_account_id}:*",
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": ["s3:*", "s3-object-lambda:*"],
                                    "Resource": "*",
                                },
                            ],
                        }
                    ),
                    Description="These are the permissions that the Komodo server will have to be able to manage your infrastructure",
                )

            role_response = iam_client.create_role(
                RoleName=iam_role_name,
                AssumeRolePolicyDocument=json.dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Sid": "Statement1",
                                "Effect": "Allow",
                                "Principal": {"AWS": "211125406737"},
                                "Condition": {
                                    "StringEquals": {
                                        "sts:ExternalId": user_id,
                                    }
                                },
                                "Action": "sts:AssumeRole",
                            }
                        ],
                    }
                ),
            )

            attach_response = iam_client.attach_role_policy(
                RoleName=iam_role_name,
                PolicyArn=policy_arn,
            )
    except botocore.exceptions.BotoCoreError as e:
        raise ClientException(str(e))

    role_arn = role_response["Role"]["Arn"]
    api_client.connect_aws(role_arn)
