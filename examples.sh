#!/bin/bash

# Make sure the CloudWatch MCP server is running before executing these commands

# List all log groups
echo "Listing all log groups..."
mcp inspect cloudwatch://log-groups

# Get details about a specific log group (replace with an actual log group name from your AWS account)
echo -e "\nGetting details for a specific log group..."
mcp inspect cloudwatch://log-groups/Gamma-OneBox-us-east-1-ExsStack-TuxedoAppBuilderTuxedoFirelensLogTuxedoLogs2F4A1E9B-CMZQOrFLDwvR

# List all alarms
echo -e "\nListing all alarms..."
mcp inspect cloudwatch://alarms

# List alarms in ALARM state
echo -e "\nListing alarms in ALARM state..."
mcp inspect cloudwatch://alarms/in-alarm

# Query logs using CloudWatch Insights
echo -e "\nQuerying logs..."
mcp call query_logs --log_group_name "Gamma-OneBox-us-east-1-ExsStack-TuxedoAppBuilderTuxedoFirelensLogTuxedoLogs2F4A1E9B-CMZQOrFLDwvR" --query_string "fields @timestamp, @message | limit 10"

# Discover fields in a log group
echo -e "\nDiscovering fields in a log group..."
mcp call discover_log_fields --log_group_name "Gamma-OneBox-us-east-1-ExsStack-TuxedoAppBuilderTuxedoFirelensLogTuxedoLogs2F4A1E9B-CMZQOrFLDwvR"

# Check if a log group exists
echo -e "\nChecking if a log group exists..."
mcp call log_group_exists --log_group_name "Gamma-OneBox-us-east-1-ExsStack-TuxedoAppBuilderTuxedoFirelensLogTuxedoLogs2F4A1E9B-CMZQOrFLDwvR"

# List all saved CloudWatch Logs Insights queries
echo -e "\nListing all saved CloudWatch Logs Insights queries..."
mcp inspect cloudwatch://saved-queries

# Get saved queries using the tool
echo -e "\nGetting saved queries using the tool..."
mcp call get_saved_queries 