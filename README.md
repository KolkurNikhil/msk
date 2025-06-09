# msk
MSK TO S3
{
  "connector.class": "io.confluent.connect.s3.S3SinkConnector",
  "s3.region": "ap-south-1",
  "flush.size": "5",
  "schema.compatibility": "NONE",
  "tasks.max": "1",
  "topics": "topic1",
  "s3.part.size": "5242880",
  "format.class": "io.confluent.connect.s3.format.json.JsonFormat",
  "value.converter": "org.apache.kafka.connect.storage.StringConverter",
  "storage.class": "io.confluent.connect.s3.storage.S3Storage",
  "s3.bucket.name": "msks31",
  "key.converter": "org.apache.kafka.connect.storage.StringConverter"
}
IAM POLICY for msk connect
CREATE THE IAM ROLE AND ATTACH POLICY PERMISSIONS
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "kafka-cluster:Connect",
                "kafka-cluster:DescribeCluster"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "kafka-cluster:ReadData",
                "kafka-cluster:DescribeTopic"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "kafka-cluster:WriteData",
                "kafka-cluster:DescribeTopic"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "kafka-cluster:CreateTopic",
                "kafka-cluster:WriteData",
                "kafka-cluster:ReadData",
                "kafka-cluster:DescribeTopic"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "kafka-cluster:AlterGroup",
                "kafka-cluster:DescribeGroup"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:*"
            ],
            "Resource": "*"
        }
    ]
}
TRUSTED POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "kafkaconnect.amazonaws.com"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {
                    "aws:SourceAccount": ""
                }
            }
        }
    ]
}

create the vpcendpoint for s3 as gateway .
com.amazonaws.ap-south-1.s3 as gateway
secretsmanager.ap-south-1.amazonaws.com interface
sts.ap-south-1.amazonaws.com
com.amazonaws.ap-south-1.redshift-data 
redshift iam 
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "GlueCatalogRead",
            "Effect": "Allow",
            "Action": [
                "glue:GetDatabase",
                "glue:GetDatabases",
                "glue:GetTable",
                "glue:GetTables",
                "glue:GetPartition",
                "glue:GetPartitions"
            ],
            "Resource": "*"
        },
        {
            "Sid": "S3ReadData",
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::msks31",
                "arn:aws:s3:::msks31/*"
            ]
        }
    ]
}
