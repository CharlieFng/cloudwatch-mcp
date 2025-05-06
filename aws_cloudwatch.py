import logging
import boto3
import os
import json
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Initialize logger
logger = logging.getLogger(__name__)

class CloudWatchIntegration:
    """Simplified wrapper for AWS CloudWatch and CloudWatch Logs integration"""
    
    def __init__(self, profile_name='default'):
        """
        Initialize AWS CloudWatch clients with a specific profile
        
        Args:
            profile_name: AWS profile name to use for credentials
        """
        self.session = boto3.Session(profile_name=profile_name, region_name='us-east-1')
        self.cloudwatch = self.session.client('cloudwatch')
        self.logs = self.session.client('logs')
        logger.info(f"CloudWatch integration initialized with profile: {profile_name}")
        
        # Static map of log groups
        self.static_log_groups = {
            "solo": {
                "server-side": os.getenv("SERVER_SIDE_LOG_GROUPS"),
                "client-side": os.getenv("CLIENT_SIDE_LOG_GROUPS")
            },
        }
    
    def format_timestamp(self, timestamp):
        """Format a timestamp for display"""
        if isinstance(timestamp, datetime):
            return timestamp.isoformat()
        return timestamp
    
    def get_log_groups(self):
        """
        Get all CloudWatch log groups from static map
        
        Returns:
            List of log group objects
        """
        return self.static_log_groups
    
    def get_all_alarms(self):
        """
        Get all CloudWatch alarms regardless of state or type
        
        Returns:
            List of all alarm objects (both metric and composite)
        """
        # Get metric alarms
        response = self.cloudwatch.describe_alarms()
        metric_alarms = response.get('MetricAlarms', [])
        composite_alarms = response.get('CompositeAlarms', [])
        
        # Handle pagination if needed
        while response.get('NextToken'):
            response = self.cloudwatch.describe_alarms(
                NextToken=response['NextToken']
            )
            metric_alarms.extend(response.get('MetricAlarms', []))
            composite_alarms.extend(response.get('CompositeAlarms', []))
        
        # Add a type field to each alarm for identification
        for alarm in metric_alarms:
            alarm['AlarmType'] = 'MetricAlarm'
        
        for alarm in composite_alarms:
            alarm['AlarmType'] = 'CompositeAlarm'
        
        # Combine both types of alarms
        return metric_alarms + composite_alarms
    
    def get_composite_alarms(self):
        """
        Get all CloudWatch composite alarms
        
        Returns:
            List of composite alarm objects
        """
        response = self.cloudwatch.describe_alarms(AlarmTypes=['CompositeAlarm'])
        alarms = response.get('CompositeAlarms', [])
        
        # Handle pagination if needed
        while response.get('NextToken'):
            response = self.cloudwatch.describe_alarms(
                AlarmTypes=['CompositeAlarm'],
                NextToken=response['NextToken']
            )
            alarms.extend(response.get('CompositeAlarms', []))
        
        return alarms
    
    def log_group_exists(self, log_group_name):
        """
        Verify if a CloudWatch log group exists
        
        Args:
            log_group_name: The name of the log group to check
            
        Returns:
            Boolean indicating whether the log group exists
        """
        try:
            response = self.logs.describe_log_groups(
                logGroupNamePrefix=log_group_name,
                limit=1
            )
            
            # Check if the exact log group exists in the response
            for log_group in response.get('logGroups', []):
                if log_group.get('logGroupName') == log_group_name:
                    logger.info(f"Log group '{log_group_name}' exists")
                    return True
                    
            logger.info(f"Log group '{log_group_name}' does not exist")
            return False
        except Exception as e:
            logger.error(f"Error checking log group '{log_group_name}': {str(e)}")
            return False
    
    def get_alarms_in_alarm_state(self):
        """
        Get all CloudWatch alarms that are in ALARM state, regardless of type
        
        Returns:
            List of alarm objects in ALARM state (both metric and composite)
        """
        # Get all alarms in ALARM state
        response = self.cloudwatch.describe_alarms(StateValue='ALARM')
        metric_alarms = response.get('MetricAlarms', [])
        composite_alarms = response.get('CompositeAlarms', [])
        
        # Handle pagination if needed
        while response.get('NextToken'):
            response = self.cloudwatch.describe_alarms(
                StateValue='ALARM',
                NextToken=response['NextToken']
            )
            metric_alarms.extend(response.get('MetricAlarms', []))
            composite_alarms.extend(response.get('CompositeAlarms', []))
        
        # Add a type field to each alarm for identification
        for alarm in metric_alarms:
            alarm['AlarmType'] = 'MetricAlarm'
        
        for alarm in composite_alarms:
            alarm['AlarmType'] = 'CompositeAlarm'
        
        # Combine both types of alarms
        return metric_alarms + composite_alarms
    
    def get_alarms(self):
        """
        Get all CloudWatch alarms that are in ALARM state
        (Legacy method, maintained for backwards compatibility)
        
        Returns:
            List of alarm objects in ALARM state
        """
        return self.get_alarms_in_alarm_state()
    
    def get_formatted_alarms(self, only_in_alarm=False):
        """
        Get CloudWatch alarms in a formatted structure
        
        Args:
            only_in_alarm: If True, returns only alarms in ALARM state
        
        Returns:
            List of formatted alarm dictionaries
        """
        if only_in_alarm:
            alarms = self.get_alarms_in_alarm_state()
        else:
            alarms = self.get_all_alarms()
        
        formatted_alarms = []
        for alarm in alarms:
            alarm_type = alarm.get('AlarmType', 'Unknown')
            
            formatted_alarm = {
                "alarmName": alarm.get('AlarmName'),
                "alarmDescription": alarm.get('AlarmDescription'),
                "stateValue": alarm.get('StateValue'),
                "alarmType": alarm_type
            }
            
            # Add metric-specific fields only for metric alarms
            if alarm_type == 'MetricAlarm':
                formatted_alarm.update({
                    "metric": alarm.get('MetricName'),
                    "namespace": alarm.get('Namespace'),
                    "statistic": alarm.get('Statistic'),
                    "dimensions": alarm.get('Dimensions', [])
                })
            # Add composite-specific fields only for composite alarms
            elif alarm_type == 'CompositeAlarm':
                formatted_alarm.update({
                    "alarmRule": alarm.get('AlarmRule')
                })
            
            formatted_alarms.append(formatted_alarm)
        
        return formatted_alarms
        
    def discover_log_fields(self, log_group_names: List[str]) -> Dict[str, str]:
        """
        Discover fields in a CloudWatch log group, including nested fields in @message
        
        Args:
            log_group_name: The name of the log group to analyze
            
        Returns:
            Dictionary of discovered fields and their types
        """
        try:
            for log_group_name in log_group_names:
                if not self.log_group_exists(log_group_name):
                    logger.warning(f"Log group '{log_group_name}' does not exist")
                    return {}
                    
            # Use a query that returns more log entries to better discover fields
            query = "fields @timestamp, @message | limit 20"
            
            start_query_response = self.logs.start_query(
                logGroupNames=log_group_names,
                startTime=int((datetime.now().timestamp() - 86400) * 1000),
                endTime=int(datetime.now().timestamp() * 1000),
                queryString=query
            )
            
            query_id = start_query_response['queryId']
            
            # Wait for query to complete
            response = None
            while response is None or response['status'] in ['Running', 'Scheduled']:
                logger.info(f"Waiting for query to complete... Status: {response['status'] if response else 'Starting'}")
                response = self.logs.get_query_results(queryId=query_id)
                
            logger.info(f"Query completed with status: {response['status']}")
            
            fields = {}
            if response['status'] == 'Complete':
                if response.get('results'):
                    for result in response['results']:
                        for field_entry in result:
                            field_name = field_entry.get('field')
                            value = field_entry.get('value', '')
                            
                            # Handle base fields
                            if field_name and field_name not in fields:
                                if field_name == '@message':
                                    fields[field_name] = 'json'
                                    # Parse @message JSON and discover nested fields
                                    try:
                                        message_json = json.loads(value)
                                        if isinstance(message_json, dict):
                                            def extract_fields(obj, prefix=''):
                                                for key, val in obj.items():
                                                    field_path = f"{prefix}{key}" if prefix else key
                                                    if isinstance(val, dict):
                                                        extract_fields(val, f"{field_path}.")
                                                    elif isinstance(val, list):
                                                        fields[field_path] = 'array'
                                                    elif isinstance(val, bool):
                                                        fields[field_path] = 'boolean'
                                                    elif isinstance(val, (int, float)):
                                                        fields[field_path] = 'number'
                                                    else:
                                                        fields[field_path] = 'string'
                                            
                                            extract_fields(message_json)
                                    except json.JSONDecodeError:
                                        pass
                                else:
                                    # Determine type for non-@message fields
                                    if value.isdigit():
                                        fields[field_name] = 'number'
                                    elif value.lower() in ['true', 'false']:
                                        fields[field_name] = 'boolean'
                                    else:
                                        fields[field_name] = 'string'
            
            logger.info(f"Discovered {len(fields)} fields for log group '{log_group_name}'")
            return fields
        except Exception as e:
            logger.error(f"Error discovering fields for log group '{log_group_name}': {str(e)}")
            return {}
    
    def query_logs(self, log_group_names: List[str], query_string, start_time, end_time):
        """
        Query CloudWatch logs using CloudWatch Insights
        
        Args:
            log_group_name: The name of the log group to query
            query_string: The CloudWatch Insights query string
            start_time: The start time for the query as Unix timestamp (default: 24 hours ago)
            end_time: The end time for the query as Unix timestamp (default: now)
            
        Returns:
            Dictionary containing query results and metadata
        """
        try:
            for log_group_name in log_group_names:
                if not self.log_group_exists(log_group_name):
                    logger.warning(f"Log group '{log_group_name}' does not exist")
                    return {
                        "status": "Failed",
                        "message": f"Log group '{log_group_name}' does not exist",
                        "results": []
                    }
                
            # Set default time range if not provided (last 24 hours)
            if start_time is None:
                start_time = int((datetime.now().timestamp() - 86400) * 1000)  # 24 hours ago
            if end_time is None:
                end_time = int(datetime.now().timestamp() * 1000)  # now
                
            # Start the query
            start_query_response = self.logs.start_query(
                logGroupNames=log_group_names,
                startTime=start_time,
                endTime=end_time,
                queryString=query_string
            )
            
            query_id = start_query_response['queryId']
            
            # Wait for query to complete
            response = None
            while response is None or response['status'] in ['Running', 'Scheduled']:
                logger.info(f"Waiting for query to complete... Status: {response['status'] if response else 'Starting'}")
                response = self.logs.get_query_results(queryId=query_id)
                
            logger.info(f"Query completed with status: {response['status']}")
            
            # Format results
            result = {
                "status": response['status'],
                "statistics": response.get('statistics', {}),
                "results": []
            }
            
            # Extract results
            if response['status'] == 'Complete':
                for log_result in response.get('results', []):
                    log_entry = {}
                    for field in log_result:
                        field_name = field['field']
                        field_value = field['value']
                        
                        # Special handling for @message field
                        if field_name == '@message':
                            try:
                                field_value = json.loads(field_value)
                            except json.JSONDecodeError:
                                # Keep original value if it's not valid JSON
                                pass
                        
                        log_entry[field_name] = field_value
                    result["results"].append(log_entry)
                    
            return result
        except Exception as e:
            logger.error(f"Error querying logs for log group '{log_group_name}': {str(e)}")
            return {
                "status": "Failed",
                "message": str(e),
                "results": []
            }
            
    def get_saved_queries(self):
        """
        Fetch all saved CloudWatch Logs Insights queries
        
        Returns:
            List of saved query definitions
        """
        try:
            # Initialize results list
            saved_queries = []
            
            # Get the first page of results
            response = self.logs.describe_query_definitions()
            saved_queries.extend(response.get('queryDefinitions', []))
            
            # Handle pagination if needed
            while 'nextToken' in response:
                response = self.logs.describe_query_definitions(nextToken=response['nextToken'])
                saved_queries.extend(response.get('queryDefinitions', []))
            
            # Format the results
            formatted_queries = []
            for query in saved_queries:
                formatted_query = {
                    "queryDefinitionId": query.get('queryDefinitionId'),
                    "name": query.get('name'),
                    "queryString": query.get('queryString'),
                    "lastModified": self.format_timestamp(query.get('lastModified'))
                }
                
                # Include log group names if available
                if 'logGroupNames' in query:
                    formatted_query['logGroupNames'] = query['logGroupNames']
                
                formatted_queries.append(formatted_query)
            
            logger.info(f"Retrieved {len(formatted_queries)} saved CloudWatch Logs Insights queries")
            return formatted_queries
            
        except Exception as e:
            logger.error(f"Error fetching saved CloudWatch Logs Insights queries: {str(e)}")
            return []

# For testing/standalone usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test the integration
    cw = CloudWatchIntegration()

    log_groups = cw.get_log_groups()
    
    # Test log groups
    print("\n=== Log Groups ===")
    print(json.dumps(log_groups, indent=2))
    
    # Test all alarms (both metric and composite)
    print("\n=== All Alarms (Both Metric and Composite) ===")
    all_alarms = cw.get_formatted_alarms(only_in_alarm=False)
    print(json.dumps(all_alarms[:3], indent=2))  # Show first 3 alarms
    
    # Test alarms in ALARM state (both metric and composite)
    print("\n=== Alarms In ALARM State (Both Metric and Composite) ===")
    in_alarm = cw.get_formatted_alarms(only_in_alarm=True)
    print(json.dumps(in_alarm[:3], indent=2))  # Show first 3 alarms
    
    # Test log group verification
    print("\n=== Log Group Verification ===")
    for log_group in log_groups["solo"]["server-side"]:
        exists = cw.log_group_exists(log_group)
        print(f"Log group '{log_group}' exists: {exists}")

    # Test saved queries
    print("\n=== Saved Queries ===")
    saved_queries = cw.get_saved_queries()
    print(f"Retrieved {len(saved_queries)} saved queries:")
    print(json.dumps(saved_queries[:5], indent=2))  # Show first 5 saved queries 

        # Test log field discovery using client-side log group
    print("\n=== Log Field Discovery ===")
    fields = cw.discover_log_fields(log_groups["solo"]["client-side"])
    print(f"Discovered fields for '{log_groups['solo']['client-side']}':")
    print(json.dumps(fields, indent=2))

    # Test log querying using server-side log group
    print("\n=== Log Querying ===")
    query = "fields @timestamp, @message | limit 5"
    start_time = int((datetime.now().timestamp() - 86400*14) * 1000)
    end_time = int((datetime.now().timestamp() - 86400*7) * 1000)
    results = cw.query_logs(log_groups["solo"]["server-side"], query, start_time, end_time)
    print(f"Query results for '{log_groups['solo']['server-side']}':")
    print(json.dumps(results, indent=2))
    

    

        
