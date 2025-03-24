# CloudWatch MCP Server

This simplified MCP server provides a streamlined way to interact with AWS CloudWatch resources through the MCP protocol. It exposes CloudWatch log groups, log queries, and alarms as resources and tools.

## Features

- List all CloudWatch log groups with their metadata
- List all CloudWatch alarms with their current states
- Query CloudWatch logs using CloudWatch Insights
- Discover available fields in log groups
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
    - `log_group_name`: Name of the log group to query
    - `query_string`: CloudWatch Insights query string
    - `start_time`: (Optional) Start time for the query in Unix timestamp milliseconds
    - `end_time`: (Optional) End time for the query in Unix timestamp milliseconds

- `discover_log_fields` - Discover available fields in a CloudWatch log group
  - Parameters:
    - `log_group_name`: Name of the log group to analyze

- `log_group_exists` - Check if a CloudWatch log group exists
  - Parameters:
    - `log_group_name`: Name of the log group to check

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

# Query logs using CloudWatch Insights
mcp call query_logs --log_group_name "my-log-group" --query_string "fields @timestamp, @message | limit 10"

# Discover fields in a log group
mcp call discover_log_fields --log_group_name "my-log-group"

# Check if a log group exists
mcp call log_group_exists --log_group_name "my-log-group"

# Get all saved CloudWatch Logs Insights queries
mcp call get_saved_queries
```

## License

MIT
