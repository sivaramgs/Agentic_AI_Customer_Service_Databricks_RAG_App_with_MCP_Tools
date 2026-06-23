# Databricks notebook source
# Import PySpark SQL functions
from pyspark.sql import functions as F
from pyspark.sql.types import StringType

print("✓ Libraries imported successfully")

# COMMAND ----------

# Load the products table
products_df = spark.table("agentic_catalog.agentic_schema.products")

print("Products Table Schema:")
products_df.printSchema()
print(f"\nTotal products: {products_df.count()}")

# Display sample data
print("\nSample products:")
display(products_df.limit(5))

# COMMAND ----------

# Load the product documentation table
product_docs_df = spark.table("agentic_catalog.agentic_schema.product_docs")

print("Product Docs Table Schema:")
product_docs_df.printSchema()
print(f"\nTotal documents: {product_docs_df.count()}")

# Display sample data (truncate long text)
print("\nSample documents:")
display(product_docs_df.limit(5))

# COMMAND ----------

# Join products with product_docs on product_name
joined_df = products_df.join(
    product_docs_df,
    on="product_name",
    how="inner"
)

print("Joined Table Schema:")
joined_df.printSchema()
print(f"\nTotal joined records: {joined_df.count()}")

# Display sample joined data
print("\nSample joined data:")
display(joined_df.limit(3))

# COMMAND ----------

# Create the indexed_doc column with XML-style tags
indexed_df = joined_df.withColumn(
    "indexed_doc",
    F.concat(
        F.lit("<product_category>"),
        F.col("product_category"),
        F.lit("</product_category>\n"),
        F.lit("<product_sub_category>"),
        F.col("product_sub_category"),
        F.lit("</product_sub_category>\n"),
        F.lit("<product_name>"),
        F.col("product_name"),
        F.lit("</product_name>\n"),
        F.lit("<product_doc>\n"),
        F.col("product_doc"),
        F.lit("\n</product_doc>")
    )
)

print("✓ Indexed document column created")

# Display sample indexed document
print("\nSample indexed document (first 500 characters):")
sample_indexed = indexed_df.select("product_name", "indexed_doc").first()
print(f"\nProduct: {sample_indexed['product_name']}")
print(f"\nIndexed Doc:\n{sample_indexed['indexed_doc'][:500]}...")

# COMMAND ----------

# Select the required columns in the specified order
final_df = indexed_df.select(
    "product_id",
    "product_name",
    "product_doc",
    "product_category",
    "product_sub_category",
    "indexed_doc"
)

print("Final Table Schema:")
final_df.printSchema()
print(f"\nTotal records: {final_df.count()}")

# Display final sample
print("\nSample final data:")
display(final_df.limit(5))

# COMMAND ----------

# Define the target table name
target_table = "agentic_catalog.agentic_schema.product_docs_combined"

# Write the DataFrame to Unity Catalog as a managed Delta table
# Using 'overwrite' mode to replace if exists
final_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(target_table)

print(f"✓ Table saved successfully: {target_table}")
print(f"\nTotal records written: {spark.table(target_table).count()}")


# COMMAND ----------

# Read the table back and verify
verify_df = spark.table("agentic_catalog.agentic_schema.product_docs_combined")

print("Verification Results:")
print(f"Total records: {verify_df.count()}")
print("\nTable Schema:")
verify_df.printSchema()

# Display sample records
print("\nSample Records:")
display(verify_df.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC ✓ **Pipeline Complete!**
# MAGIC
# MAGIC We have successfully:
# MAGIC 1. Loaded products and product documentation from Unity Catalog
# MAGIC 2. Joined the tables on `product_name`
# MAGIC 3. Created indexed documents with XML-style formatting
# MAGIC 4. Saved the results to `agentic_catalog.agentic_schema.products_indexed`
# MAGIC
# MAGIC The indexed documents are now ready for:
# MAGIC - Vector embeddings generation
# MAGIC - LLM-based retrieval
# MAGIC - Semantic search applications
# MAGIC - AI agent workflows

# COMMAND ----------

spark.sql("""
ALTER TABLE agentic_catalog.agentic_schema.product_docs_combined
SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")