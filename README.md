# CloudWatch MCP Server

This simplified MCP server provides a streamlined way to interact with AWS CloudWatch resources through the MCP protocol. It exposes CloudWatch log groups, log queries, and alarms as resources and tools.

## Features

- List all CloudWatch log groups with their metadata
- List all CloudWatch alarms with their current states
- Query CloudWatch logs using CloudWatch Insights across multiple log groups
- Discover available fields across multiple log groups with shared schema
- Automatic JSON parsing for @message field in log queries
- Check if specific log groups exist
- Get detailed information about specific log groups
- Filter alarms by state (all alarms or only those in ALARM state)
- Retrieve all saved CloudWatch Logs Insights queries

## Prerequisites

- Python 3.12 or higher
- AWS credentials configured (via environment variables, AWS CLI, or IAM role)
- MCP CLI (version 0.1.1 or higher)
- Boto3 (AWS SDK for Python)

## Setup

1. Make sure you have Python 3.12+ installed.

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure AWS credentials if you haven't already:
   ```
   aws configure
   ```
   
   Or set environment variables:
   ```
   export AWS_ACCESS_KEY_ID="your-access-key"
   export AWS_SECRET_ACCESS_KEY="your-secret-key"
   export AWS_REGION="your-region"
   ```

## Project Structure

- `cloudwatch_server.py` - MCP server implementation for CloudWatch integration
- `aws_cloudwatch.py` - Simplified AWS CloudWatch integration module
- `test_cloudwatch.py` - Command-line utility to test the CloudWatch integration

## Running the server

Start the MCP server:

```
python cloudwatch_server.py
```

Or using the MCP CLI:

```
mcp run cloudwatch_server.py
```

## Using the MCP server

### Resources

The server exposes the following resources:

- `cloudwatch://log-groups` - Lists all CloudWatch log groups
- `cloudwatch://log-groups/{log_group_name}` - Gets detailed information about a specific log group
- `cloudwatch://alarms` - Lists all CloudWatch alarms
- `cloudwatch://alarms/in-alarm` - Lists only CloudWatch alarms currently in ALARM state
- `cloudwatch://saved-queries` - Lists all saved CloudWatch Logs Insights queries

### Tools

The server provides the following tools:

- `query_logs` - Query CloudWatch logs using CloudWatch Insights
  - Parameters:
    - `log_group_names`: Single log group name or list of log group names to query
    - `query_string`: CloudWatch Insights query string
    - `start_time`: (Optional) Start time for the query in Unix timestamp milliseconds
    - `end_time`: (Optional) End time for the query in Unix timestamp milliseconds
  - Features:
    - Automatically parses JSON in @message field
    - Returns structured data for JSON messages
    - Handles multiple log groups in a single query

- `discover_log_fields` - Discover available fields across multiple log groups
  - Parameters:
    - `log_group_names`: Single log group name or list of log group names to analyze
  - Features:
    - Efficiently discovers fields across multiple log groups
    - Assumes shared schema across log groups
    - Detects nested JSON fields in @message
    - Identifies field types (number, boolean, string, array)

- `log_group_exists` - Check if CloudWatch log groups exist
  - Parameters:
    - `log_group_names`: Single log group name or list of log group names to check
  - Returns:
    - Dictionary mapping each log group to its existence status

- `get_saved_queries` - Fetch all saved CloudWatch Logs Insights queries
  - No parameters required

## Testing the CloudWatch integration

You can test the CloudWatch integration directly using the provided test script:

```
# Make the test file executable
chmod +x test_cloudwatch.py

# List all log groups
./test_cloudwatch.py log-groups

# List all alarms
./test_cloudwatch.py alarms

# Use a specific AWS profile
./test_cloudwatch.py log-groups --profile my-profile

# Enable verbose logging
./test_cloudwatch.py alarms -v
```

## Examples with MCP CLI

Using the MCP CLI:

```bash
# List all log groups
mcp inspect cloudwatch://log-groups

# Get details about a specific log group
mcp inspect cloudwatch://log-groups/my-log-group-name

# List all alarms
mcp inspect cloudwatch://alarms

# List alarms currently in ALARM state
mcp inspect cloudwatch://alarms/in-alarm

# List all saved CloudWatch Logs Insights queries
mcp inspect cloudwatch://saved-queries

# Query logs from multiple log groups using CloudWatch Insights
mcp call query_logs --log_group_names '["log-group-1", "log-group-2"]' --query_string "fields @timestamp, @message | limit 10"

# Query logs from a single log group (still supported)
mcp call query_logs --log_group_names "my-log-group" --query_string "fields @timestamp, @message | limit 10"

# Discover fields across multiple log groups
mcp call discover_log_fields --log_group_names '["log-group-1", "log-group-2"]'

# Check if multiple log groups exist
mcp call log_group_exists --log_group_names '["log-group-1", "log-group-2"]'

# Get all saved CloudWatch Logs Insights queries
mcp call get_saved_queries
```

## License

MIT
