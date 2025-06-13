import json
import boto3

s3_client = boto3.client('s3')
redshift_client = boto3.client('redshift-data')

# Configuration
BUCKET_NAME = 'logsbank'
REDSHIFT_CLUSTER_ID = 'redshift-cluster-1'
REDSHIFT_DATABASE = 'dev'
REDSHIFT_DB_USER = 'awsuser'
REDSHIFT_REGION = 'ap-south-1'

def lambda_handler(event, context):
    print("Lambda triggered: Scanning all JSON files in bucket/logs/")

    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix='logs/')
        if 'Contents' not in response:
            print("No files found under logs/")
            return {"statusCode": 200, "body": "No files to process"}

        for obj in response['Contents']:
            key = obj['Key']
            if not key.startswith('logs/') or not key.endswith('.json'):
                continue

            print(f"Reading file: {key}")
            try:
                file_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
                content = file_obj['Body'].read().decode('utf-8')
                lines = content.strip().split('\n')

                for line in lines:
                    print(f"Processing line: {line}")
                    log = json.loads(line)
                    transaction_type = log.get("transaction_type")

                    table_map = {
                        "UPI": "upi_transactions",
                        "NEFT": "neft_transactions",
                        "IMPS": "imps_transactions"
                    }

                    table_name = table_map.get(transaction_type)
                    if not table_name:
                        print(f"Skipping unknown transaction type: {transaction_type}")
                        continue

                    txn_id = log["transaction_id"]
                    acct_id = log["account_id"]
                    txn_type = log["transaction_type"]
                    amount = log["amount"]
                    timestamp = log["timestamp"]
                    merchant = log["merchant"]
                    status = log["status"]

                    sql = f"""
                    INSERT INTO {table_name} (
                        transaction_id, account_id, transaction_type, amount, timestamp, merchant, status
                    )
                    VALUES (
                        '{txn_id}', '{acct_id}', '{txn_type}', {amount}, '{timestamp}', '{merchant}', '{status}'
                    );
                    """
                    print(f"Executing SQL: {sql.strip()}")

                    result = redshift_client.execute_statement(
                        ClusterIdentifier=REDSHIFT_CLUSTER_ID,
                        Database=REDSHIFT_DATABASE,
                        DbUser=REDSHIFT_DB_USER,
                        Sql=sql
                    )

                    print(f"Executed. Query ID: {result['Id']}")

                # Optional: Move to archive folder after processing
                archive_key = key.replace('logs/', 'archive/logs/')
                s3_client.copy_object(Bucket=BUCKET_NAME, CopySource={'Bucket': BUCKET_NAME, 'Key': key}, Key=archive_key)
                s3_client.delete_object(Bucket=BUCKET_NAME, Key=key)
                print(f"Archived file: {key} to {archive_key}")

            except Exception as e:
                print(f"Error processing file {key}: {str(e)}")

        return {
            'statusCode': 200,
            'body': 'Processed all JSON log files in logs/ folder (duplicates allowed)'
        }

    except Exception as e:
        print(f"Fatal Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': 'Lambda failed to process files'
        }
AmazonRedshiftFullAccess
AWS managed
1
AmazonS3FullAccess
AWS managed
1
AWSLambdaBasicExecutionRole
AWS managed
1
CloudWatchEventsFullAccess
