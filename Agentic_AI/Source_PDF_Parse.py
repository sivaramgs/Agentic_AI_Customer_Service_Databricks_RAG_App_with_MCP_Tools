# Databricks notebook source
#%pip install PyPDF2

# COMMAND ----------

source_path = "/Volumes/agentic_catalog/agentic_schema/customer_service/01_Data_Files/product_docs/"

# List all files in the directory
files = dbutils.fs.ls(source_path)

# Filter for PDF files only
pdf_files = [f for f in files if f.name.endswith('.pdf')]

print(f"Found {len(pdf_files)} PDF files:")
for pdf in pdf_files:
    print(f"  - {pdf.name}")

# COMMAND ----------

import PyPDF2
import io

# Define Text Extraction Function
def extract_text_from_pdf(file_path):
    """
    Extract text content from a PDF file.
    
    Args:
        file_path: Full path to the PDF file in DBFS/Volumes
    
    Returns:
        Extracted text as a string
    """
    try:
        # Read the PDF file content
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()
        
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes.encode('latin-1') if isinstance(pdf_bytes, str) else pdf_bytes))
        
        # Extract text from all pages
        text_content = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text_content += page.extract_text() + "\n"
        
        return text_content.strip()
    
    except Exception as e:
        print(f"Error extracting text from {file_path}: {str(e)}")
        return None

print("Text extraction function defined successfully!")



# COMMAND ----------

#Step 3: Process All PDF Files
# Initialize list to store results
product_data = []

# Process each PDF file
for pdf_file in pdf_files:
    print(f"Processing: {pdf_file.name}")
    
    # Extract product name (remove .pdf extension)
    product_name = pdf_file.name.replace('.pdf', '')
    
    # Extract text from the PDF
    full_path = f"{source_path}{pdf_file.name}"
    product_doc = extract_text_from_pdf(full_path)
    
    if product_doc:
        product_data.append({
            'product_name': product_name,
            'product_doc': product_doc
        })
        print(f"  ✓ Successfully extracted {len(product_doc)} characters")
    else:
        print(f"  ✗ Failed to extract text")

print(f"\nTotal documents processed: {len(product_data)}")




# COMMAND ----------

# Create and Save DataFrame
from pyspark.sql.types import StructType, StructField, StringType

# Define schema for the DataFrame
schema = StructType([
    StructField("product_name", StringType(), False),
    StructField("product_doc", StringType(), True)
])

# Create Spark DataFrame from the extracted data
df = spark.createDataFrame(product_data, schema=schema)

# Display the DataFrame schema and count
print(f"DataFrame created with {df.count()} rows\n")
df.printSchema()

# Write to Unity Catalog table
table_name = "agentic_catalog.agentic_schema.product_docs"
print(f"\nWriting data to table: {table_name}")

df.write \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(table_name)

print(f"✓ Successfully created table: {table_name}")



# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE HISTORY agentic_catalog.agentic_schema.product_docs

# COMMAND ----------

# MAGIC
# MAGIC %sql 
# MAGIC select * from agentic_catalog.agentic_schema.product_docs