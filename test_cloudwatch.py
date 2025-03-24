#!/usr/bin/env python3

import logging
import argparse
import json
from aws_cloudwatch import CloudWatchIntegration

def setup_logging(verbose=False):
    """Configure logging based on verbosity level"""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main function to test CloudWatch integration"""
    parser = argparse.ArgumentParser(description='Test AWS CloudWatch Integration')
    
    # Add command argument
    parser.add_argument('command', choices=['log-groups', 'alarms', 'saved-queries'],
                      help='Command to execute')
    
    # Add optional arguments
    parser.add_argument('--profile', default='default',
                      help='AWS profile name (default: default)')
    parser.add_argument('-v', '--verbose', action='store_true',
                      help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Initialize CloudWatch integration
    cw = CloudWatchIntegration(profile_name=args.profile)
    
    # Process commands
    if args.command == 'log-groups':
        log_groups = cw.get_log_groups()
        print(json.dumps(log_groups, indent=2))
    
    elif args.command == 'alarms':
        alarms = cw.get_formatted_alarms()
        print(json.dumps(alarms, indent=2))
        
    elif args.command == 'saved-queries':
        saved_queries = cw.get_saved_queries()
        print(json.dumps(saved_queries, indent=2))

if __name__ == '__main__':
    main() 