import logging
import json
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context
from aws_cloudwatch import CloudWatchIntegration
from typing import Dict, List, Optional, Any, Union

# Load environment variables from .env file
load_dotenv()

# Create logger
logger = logging.getLogger(__name__)

# Create an MCP server for CloudWatch integration
mcp = FastMCP("CloudWatch")

# Get AWS profile from environment variables
aws_profile = os.getenv("AWS_PROFILE", "default")

# Initialize the CloudWatch integration
cloudwatch_integration = CloudWatchIntegration(profile_name=aws_profile)

# Add a tool 
@mcp.tool()
def greeting(name: str, ctx: Context) -> str:
    """Greet a person"""
    ctx.debug(f"Greeting {name}!")
    return f"Hello, {name}!"

# Resource: Log Groups
@mcp.resource("cloudwatch://log-groups")
def list_log_groups() -> str:
    """List all CloudWatch log groups"""
    formatted_groups = cloudwatch_integration.get_log_groups()
    return json.dumps(formatted_groups, indent=2)

# Tool: Fetch all alarms
@mcp.tool()
def list_alarms() -> str:
    """List all CloudWatch alarms"""
    alarms = cloudwatch_integration.get_formatted_alarms(only_in_alarm=False)
    return json.dumps(alarms, indent=2)

# Tool: Fetch alarms in ALARM state
@mcp.tool()
def list_alarms_in_alarm_state() -> List[str]:
    """List all CloudWatch alarms currently in ALARM state"""
    return cloudwatch_integration.get_formatted_alarms(only_in_alarm=True)
    

# Tool: Query logs
@mcp.tool()
def query_logs(log_group_name: str, query_string: str, ctx: Context, start_time: Optional[int] = None, end_time: Optional[int] = None) -> str:
    """
    Query CloudWatch logs using CloudWatch Insights
    
    Args:
        log_group_name: The name of the CloudWatch log group to query
        query_string: CloudWatch Insights query string
        start_time: Start time in unix timestamp milliseconds (optional, default: 24 hours ago)
        end_time: End time in unix timestamp milliseconds (optional, default: now)
    
    Returns:
        JSON string with query results
    """
    ctx.debug(f"Querying log group '{log_group_name}' with query: {query_string}")
    query_results = cloudwatch_integration.query_logs(
        log_group_name=log_group_name,
        query_string=query_string,
        start_time=start_time,
        end_time=end_time
    )
    return json.dumps(query_results, indent=2)

# Tool: Discover log fields
@mcp.tool()
def discover_log_fields(log_group_name: str, ctx: Context) -> str:
    """
    Discover available fields in a CloudWatch log group
    
    Args:
        log_group_name: The name of the CloudWatch log group to analyze
    
    Returns:
        JSON string with discovered field names and their types
    """
    ctx.debug(f"Discovering fields for log group '{log_group_name}'")
    fields = cloudwatch_integration.discover_log_fields(log_group_name)
    return json.dumps(fields, indent=2)

# Tool: Check if log group exists
@mcp.tool()
def log_group_exists(log_group_name: str, ctx: Context) -> bool:
    """
    Check if a CloudWatch log group exists
    
    Args:
        log_group_name: The name of the CloudWatch log group to check
    
    Returns:
        Boolean indicating whether the log group exists
    """
    ctx.debug(f"Checking if log group '{log_group_name}' exists")
    return cloudwatch_integration.log_group_exists(log_group_name)

# Tool: Get saved queries
@mcp.tool()
def get_saved_queries(ctx: Context) -> str:
    """
    Fetch all saved CloudWatch Logs Insights queries
    
    Returns:
        JSON string with all saved queries
    """
    ctx.debug("Fetching all saved CloudWatch Logs Insights queries")
    saved_queries = cloudwatch_integration.get_saved_queries()
    return json.dumps(saved_queries, indent=2)


if __name__ == "__main__":
    # Get log level from environment variable, default to INFO
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info(f"Starting CloudWatch MCP server with profile: {aws_profile}")
    logger.info(f"Log level set to: {log_level_str}")
    
    # Run the MCP server
    mcp.run(transport='stdio')