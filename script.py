https://repo1.maven.org/maven2/io/github/spark-redshift-community/spark-redshift_2.12/6.3.0-spark_3.5/spark-redshift_2.12-6.3.0-spark_3.5.jar
import sys
from awsglue.context import GlueContext
from pyspark.context import SparkContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

# Initialize Glue job
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read data from S3
s3_path = "s3://msks31/nik.json"
df = spark.read.json(s3_path)

# Print schema for debugging (optional)
df.printSchema()

# Filter based on type
upi_df = df.filter(df["transaction_type"] == "UPI")
neft_df = df.filter(df["transaction_type"] == "NEFT")
imps_df = df.filter(df["transaction_type"] == "IMPS")

# Redshift config
redshift_tmp_dir = "s3://msks31/redshift-temp/"
redshift_jdbc_url = "jdbc:redshift://redshift-cluster-1.czm2xpdnsgwr.ap-south-1.redshift.amazonaws.com:5439/dev"
redshift_iam_role = "arn:aws:iam::352437221780:role/glue"

# UPI
upi_df.write \
    .format("io.github.spark_redshift_community.spark.redshift") \
    .option("url", redshift_jdbc_url) \
    .option("dbtable", "upi_mart.transactions") \
    .option("tempdir", redshift_tmp_dir) \
    .option("aws_iam_role", redshift_iam_role) \
    .mode("append") \
    .save()

# NEFT
neft_df.write \
    .format("io.github.spark_redshift_community.spark.redshift") \
    .option("url", redshift_jdbc_url) \
    .option("dbtable", "neft_mart.transactions") \
    .option("tempdir", redshift_tmp_dir) \
    .option("aws_iam_role", redshift_iam_role) \
    .mode("append") \
    .save()

# IMPS
imps_df.write \
    .format("io.github.spark_redshift_community.spark.redshift") \
    .option("url", redshift_jdbc_url) \
    .option("dbtable", "imps_mart.transactions") \
    .option("tempdir", redshift_tmp_dir) \
    .option("aws_iam_role", redshift_iam_role) \
    .mode("append") \
    .save()

# Commit job
job.commit()
