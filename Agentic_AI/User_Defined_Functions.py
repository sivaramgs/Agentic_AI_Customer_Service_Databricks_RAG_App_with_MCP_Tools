# Databricks notebook source
spark.sql(f"""
-- Create a function to retrieve company policy details
CREATE OR REPLACE FUNCTION agentic_catalog.agentic_schema.get_return_policy(
    policy_name STRING COMMENT 'Policy name to return. Example policies: Account Cancellation Policy, Exchange Policy, Refund Policy, Warranty Policy, Privacy Policy, Return Policy'
    )
    RETURNS TABLE (
    policy           STRING,
    policy_details   STRING,
    last_updated     DATE
    )
    COMMENT 'Returns the details of the Return Policy'
    LANGUAGE SQL
    RETURN (
    SELECT
    policy,
    policy_details,
    last_updated
    FROM agentic_catalog.agentic_schema.policies
    WHERE policy = policy_name
    LIMIT 1
    );
    """)

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC select * from agentic_catalog.agentic_schema.policies
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC select * from agentic_catalog.agentic_schema.get_return_policy("Return Policy")
# MAGIC
# MAGIC

# COMMAND ----------

spark.sql(f"""
-- Create a function to get service history by user
CREATE OR REPLACE FUNCTION agentic_catalog.agentic_schema.get_service_history(
    user_email STRING COMMENT 'User email to retrieve order history'
    )
    RETURNS TABLE (
    returns_last_12_months INT,
    issue_category STRING, 
    todays_date DATE
    )
    COMMENT 'This takes the user_name of a customer as an input and returns the number of returns and the issue category'
    LANGUAGE SQL
    RETURN(
    SELECT count(*) as returns_last_12_months, issue_category, now() as todays_date
    FROM agentic_catalog.agentic_schema.cust_service_data 
    WHERE email = user_email
    GROUP BY issue_category
    );""")


# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC select * from agentic_catalog.agentic_schema.cust_service_data 
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC select * from agentic_catalog.agentic_schema.get_service_history("nicolas.pelaez@example.com")