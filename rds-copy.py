#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse

import boto3


def copy_rds_instances(
        source_access_key_id,
        source_secret_access_key,
        source_region_name,
        dest_access_key_id,
        dest_secret_access_key,
        dest_region_name,
        instance_name):
    """Copy RDS DB instance from one AWS account to another using boto3.

        @type source_access_key_id: string
        @param source_access_key_id: ACCESS_KEY_ID of source account
        @type source_secret_access_key: string
        @param source_secret_access_key: SECRET_ACCESS_KEY of source account
        @type source_region_name: string
        @param source_region_name: REGION_NAME of source account
        @type dest_access_key_id: string
        @param dest_access_key_id: ACCESS_KEY_ID of source account
        @type dest_secret_access_key: string
        @param dest_secret_access_key: SECRET_ACCESS_KEY of source account
        @type dest_region_name: string
        @param dest_region_name: REGION_NAME of source account
        @type instance_name: string
        @param instance_name: DB instance name on source account"""

    # Create source and destination account sessions
    source_session = boto3.session.Session(
        aws_access_key_id=source_access_key_id,
        aws_secret_access_key=source_secret_access_key,
        region_name=source_region_name)

    dest_session = boto3.session.Session(
        aws_access_key_id=dest_access_key_id,
        aws_secret_access_key=dest_secret_access_key,
        region_name=dest_region_name)

    # Get source and destination AWS account IDs
    source_iam = source_session.client("iam")
    source_aws_account_id = source_iam.get_user()["User"]["Arn"].split(":")[4]

    dest_iam = dest_session.client('iam')
    dest_aws_account_id = dest_iam.get_user()["User"]["Arn"].split(":")[4]

    # Define DB snapshot name
    snapshot_name = "{}-snapshot".format(instance_name)

    # Create DB snapshot on source account
    source_rds = source_session.client("rds")
    source_rds.create_db_snapshot(
        DBSnapshotIdentifier=snapshot_name,
        DBInstanceIdentifier=instance_name)

    print("Waiting to create DB snapshot...")
    waiter = source_rds.get_waiter('db_snapshot_completed')
    waiter.wait()

    # Share DB snapshot with destination account
    source_rds.modify_db_snapshot_attribute(
        DBSnapshotIdentifier=snapshot_name,
        AttributeName='restore',
        ValuesToAdd=[dest_aws_account_id, ])

    snapshot_arn = "arn:aws:rds:{}:{}:snapshot:{}".format(
        source_region_name,
        source_aws_account_id,
        snapshot_name)

    # Restore DB instance from DB snapshot
    dest_rds = dest_session.client("rds")
    dest_rds.restore_db_instance_from_db_snapshot(
        DBInstanceIdentifier=instance_name,
        DBSnapshotIdentifier=snapshot_arn)

    print("Waiting to restore DB instance from snapshot...")
    waiter = dest_rds.get_waiter('db_instance_available')
    waiter.wait(DBInstanceIdentifier=instance_name)

    # Delete DB snapshot
    print("Deleting DB snapshot...")
    source_rds.delete_db_snapshot(DBSnapshotIdentifier=snapshot_name)

    print("Completed!")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    # Define arguments for CLI
    source_credentials_help = (
        "\"<AWS_ACCESS_KEY_ID>:<AWS_SECRET_ACCESS_KEY>:<REGION_NAME>\"")
    parser.add_argument(
        "source_credentials",
        help=source_credentials_help)

    destination_credentials_help = (
        "\"<AWS_ACCESS_KEY_ID>:<AWS_SECRET_ACCESS_KEY>:<REGION_NAME>\"")
    parser.add_argument(
        "destination_credentials",
        help=destination_credentials_help)

    parser.add_argument("instance_name", help="DB instance name")

    # Parse arguments from CLI
    args = parser.parse_args()

    sc = args.source_credentials.split(":")
    source_access_key_id, source_secret_access_key, source_region_name = sc

    dc = args.destination_credentials.split(":")
    dest_access_key_id, dest_secret_access_key, dest_region_name = dc

    instance_name = args.instance_name

    # Call with parsed arguments
    copy_rds_instances(
        source_access_key_id,
        source_secret_access_key,
        source_region_name,
        dest_access_key_id,
        dest_secret_access_key,
        dest_region_name,
        instance_name)
