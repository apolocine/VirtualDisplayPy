#!/usr/bin/env python3
"""
🖥️ Test Runner CLI - Command Line Interface for Test Execution
Date: 03/09/2025
Description: Command line interface for running automated tests
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional
import argparse
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from automation.test_runner import TestRunner, ContinuousTestRunner
from automation.scenario_loader import ScenarioLoader, create_default_scenarios, save_default_scenarios
from core.serial_emulator import SerialEmulator
from models.display_config import VirtualDisplayConfig, ConnectionType, DisplayTheme
from utils.logger import setup_logger


def create_default_config() -> VirtualDisplayConfig:
    """Create default display configuration for testing"""
    return VirtualDisplayConfig(
        port_name="COM_TEST",
        connection_type=ConnectionType.SERIAL,
        baud_rate=9600,
        display_lines=2,
        line_length=20,
        theme=DisplayTheme.LCD_GREEN,
        font_size=12,
        brightness=100,
        contrast=80,
        clear_on_connect=True,
        cursor_visible=False,
        blinking_cursor=False
    )


async def run_tests(args):
    """Run test scenarios"""
    logger = setup_logger('cli_runner')
    
    # Initialize components
    serial_emulator = SerialEmulator()
    test_runner = TestRunner(serial_emulator)
    scenario_loader = ScenarioLoader()
    
    # Load scenarios
    scenarios = []
    
    if args.scenario_file:
        file_path = Path(args.scenario_file)
        if file_path.suffix.lower() in ['.yaml', '.yml']:
            scenarios = scenario_loader.load_from_yaml(file_path)
        elif file_path.suffix.lower() == '.json':
            scenarios = scenario_loader.load_from_json(file_path)
        else:
            logger.error(f"Unsupported scenario file format: {file_path.suffix}")
            return 1
    elif args.scenario_dir:
        scenarios = scenario_loader.load_from_directory(Path(args.scenario_dir))
    else:
        # Use default scenarios
        scenarios = create_default_scenarios()
        logger.info("Using default test scenarios")
    
    if not scenarios:
        logger.error("No test scenarios loaded")
        return 1
    
    # Filter scenarios by tags if specified
    if args.tags:
        filtered_scenarios = []
        for scenario in scenarios:
            if any(tag in scenario.tags for tag in args.tags):
                filtered_scenarios.append(scenario)
        scenarios = filtered_scenarios
        logger.info(f"Filtered to {len(scenarios)} scenarios with tags: {args.tags}")
    
    # Filter by category if specified
    if args.category:
        scenarios = [s for s in scenarios if s.category.value == args.category]
        logger.info(f"Filtered to {len(scenarios)} scenarios in category: {args.category}")
    
    # Create display configuration
    config = create_default_config()
    if args.port:
        config.port_name = args.port
    if args.connection_type:
        config.connection_type = ConnectionType(args.connection_type.lower())
    if args.lines:
        config.display_lines = args.lines
    if args.columns:
        config.line_length = args.columns
    
    logger.info(f"Running {len(scenarios)} test scenarios")
    logger.info(f"Display config: {config.port_name} ({config.connection_type.value})")
    
    # Run scenarios
    if args.continuous:
        # Continuous testing mode
        continuous_runner = ContinuousTestRunner(test_runner)
        interval = args.interval or 3600  # Default 1 hour
        logger.info(f"Starting continuous testing (interval: {interval}s)")
        await continuous_runner.run_continuous_tests(scenarios, config, interval)
    else:
        # Single run
        results = await test_runner.run_scenarios(scenarios, config)
        
        # Generate report
        if args.report:
            report_path = Path(args.report)
        else:
            report_path = Path("reports") / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = test_runner.generate_report(report_path)
        
        # Print summary
        summary = report["summary"]
        print("\n" + "="*50)
        print("TEST EXECUTION SUMMARY")
        print("="*50)
        print(f"Total tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success rate: {summary['success_rate']:.1f}%")
        print(f"Total duration: {summary['total_duration']:.2f}s")
        print(f"Report saved: {report_path}")
        
        # Return exit code based on results
        return 0 if summary['failed_tests'] == 0 else 1


def create_scenarios_command(args):
    """Create default scenario files"""
    output_dir = Path(args.output_dir or "test_scenarios")
    save_default_scenarios(output_dir)
    print(f"Default scenarios created in: {output_dir}")
    return 0


def list_scenarios_command(args):
    """List available scenarios"""
    scenario_loader = ScenarioLoader()
    
    if args.scenario_file:
        file_path = Path(args.scenario_file)
        if file_path.suffix.lower() in ['.yaml', '.yml']:
            scenarios = scenario_loader.load_from_yaml(file_path)
        elif file_path.suffix.lower() == '.json':
            scenarios = scenario_loader.load_from_json(file_path)
    elif args.scenario_dir:
        scenarios = scenario_loader.load_from_directory(Path(args.scenario_dir))
    else:
        scenarios = create_default_scenarios()
    
    print(f"\nFound {len(scenarios)} test scenarios:")
    print("-" * 80)
    
    for scenario in scenarios:
        status = "✓" if scenario.enabled else "✗"
        print(f"{status} {scenario.id:30} | {scenario.category.value:12} | {scenario.name}")
        if args.verbose:
            print(f"   Description: {scenario.description}")
            print(f"   Tags: {', '.join(scenario.tags)}")
            print(f"   Steps: {len(scenario.steps)}")
            print(f"   Duration: {scenario.expected_duration}s")
            print()
    
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="VirtualDisplayPy Test Runner CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run default scenarios
  python -m cli.test_runner_cli run
  
  # Run scenarios from file
  python -m cli.test_runner_cli run --scenario-file test_scenarios/default_scenarios.yaml
  
  # Run scenarios with specific tags
  python -m cli.test_runner_cli run --tags basic usb
  
  # Run continuous testing
  python -m cli.test_runner_cli run --continuous --interval 1800
  
  # Create default scenario files
  python -m cli.test_runner_cli create-scenarios
  
  # List available scenarios
  python -m cli.test_runner_cli list-scenarios --verbose
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run test scenarios')
    run_parser.add_argument('--scenario-file', '-f', help='Scenario file to load')
    run_parser.add_argument('--scenario-dir', '-d', help='Directory containing scenario files')
    run_parser.add_argument('--tags', '-t', nargs='+', help='Filter scenarios by tags')
    run_parser.add_argument('--category', '-c', help='Filter scenarios by category')
    run_parser.add_argument('--port', '-p', help='Display port name')
    run_parser.add_argument('--connection-type', choices=['serial', 'usb', 'network'], 
                          help='Connection type')
    run_parser.add_argument('--lines', type=int, help='Number of display lines')
    run_parser.add_argument('--columns', type=int, help='Number of columns per line')
    run_parser.add_argument('--report', '-r', help='Report output file')
    run_parser.add_argument('--continuous', action='store_true', help='Run continuously')
    run_parser.add_argument('--interval', type=int, help='Continuous testing interval (seconds)')
    
    # Create scenarios command
    create_parser = subparsers.add_parser('create-scenarios', 
                                        help='Create default scenario files')
    create_parser.add_argument('--output-dir', '-o', help='Output directory')
    
    # List scenarios command
    list_parser = subparsers.add_parser('list-scenarios', help='List available scenarios')
    list_parser.add_argument('--scenario-file', '-f', help='Scenario file to list')
    list_parser.add_argument('--scenario-dir', '-d', help='Directory containing scenario files')
    list_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'run':
            return asyncio.run(run_tests(args))
        elif args.command == 'create-scenarios':
            return create_scenarios_command(args)
        elif args.command == 'list-scenarios':
            return list_scenarios_command(args)
        else:
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())