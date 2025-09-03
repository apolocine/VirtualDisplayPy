#!/usr/bin/env python3
"""
🧪 Test Runner - Automated Test Execution Engine
Date: 03/09/2025
Description: Automated test scenario execution with reporting
"""

import asyncio
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from models.test_scenario import TestScenario, TestStep, TestResult, ResultStatus
from models.display_config import VirtualDisplayConfig
from core.serial_emulator import SerialEmulator
from utils.logger import setup_logger
from automation.scenario_validator import ScenarioValidator


class TestRunner:
    """Automated test scenario runner"""
    
    def __init__(self, serial_emulator: SerialEmulator):
        self.serial_emulator = serial_emulator
        self.logger = setup_logger('test_runner')
        self.validator = ScenarioValidator()
        self.results: List[TestResult] = []
        self.current_scenario: Optional[TestScenario] = None
        
    async def run_scenario(self, scenario: TestScenario, 
                          config: VirtualDisplayConfig) -> TestResult:
        """Execute a single test scenario"""
        self.current_scenario = scenario
        self.logger.info(f"Starting scenario: {scenario.name}")
        
        result = TestResult(
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            start_time=datetime.now(),
            status=ResultStatus.RUNNING
        )
        
        try:
            # Setup display port
            await self._setup_display(config)
            
            # Execute test steps
            for i, step in enumerate(scenario.steps):
                self.logger.info(f"Executing step {i+1}: {step.name}")
                step_result = await self._execute_step(step, config)
                result.step_results.append(step_result)
                
                if not step_result.success:
                    result.status = ResultStatus.FAILED
                    result.error_message = step_result.error_message
                    break
                
                # Wait between steps if specified
                if step.delay_after > 0:
                    await asyncio.sleep(step.delay_after / 1000.0)
            
            # Mark as passed if all steps succeeded
            if result.status == ResultStatus.RUNNING:
                result.status = ResultStatus.PASSED
                
        except Exception as e:
            self.logger.error(f"Scenario failed with exception: {str(e)}")
            result.status = ResultStatus.FAILED
            result.error_message = str(e)
            
        finally:
            result.end_time = datetime.now()
            result.duration = (result.end_time - result.start_time).total_seconds()
            await self._cleanup_display(config)
            
        self.results.append(result)
        self.logger.info(f"Scenario completed: {result.status.value}")
        return result
    
    async def run_scenarios(self, scenarios: List[TestScenario], 
                           config: VirtualDisplayConfig) -> List[TestResult]:
        """Execute multiple test scenarios"""
        self.logger.info(f"Running {len(scenarios)} test scenarios")
        results = []
        
        for scenario in scenarios:
            result = await self.run_scenario(scenario, config)
            results.append(result)
            
            # Short delay between scenarios
            await asyncio.sleep(0.5)
        
        return results
    
    async def _setup_display(self, config: VirtualDisplayConfig):
        """Setup display port for testing"""
        try:
            await self.serial_emulator.open_port(config.port_name, config)
            await asyncio.sleep(0.1)  # Wait for connection
        except Exception as e:
            self.logger.error(f"Failed to setup display: {str(e)}")
            raise
    
    async def _cleanup_display(self, config: VirtualDisplayConfig):
        """Cleanup display port after testing"""
        try:
            await self.serial_emulator.close_port(config.port_name)
        except Exception as e:
            self.logger.warning(f"Failed to cleanup display: {str(e)}")
    
    async def _execute_step(self, step: TestStep, 
                           config: VirtualDisplayConfig) -> Dict[str, Any]:
        """Execute a single test step"""
        step_start = time.time()
        
        try:
            if step.action == "send":
                await self._execute_send_step(step, config)
            elif step.action == "wait":
                await self._execute_wait_step(step)
            elif step.action == "clear":
                await self._execute_clear_step(step, config)
            elif step.action == "validate":
                await self._execute_validate_step(step, config)
            else:
                raise ValueError(f"Unknown test action: {step.action}")
            
            return {
                "step_name": step.name,
                "success": True,
                "duration": time.time() - step_start,
                "action": step.action,
                "expected_result": step.expected_result
            }
            
        except Exception as e:
            return {
                "step_name": step.name,
                "success": False,
                "duration": time.time() - step_start,
                "action": step.action,
                "error_message": str(e),
                "expected_result": step.expected_result
            }
    
    async def _execute_send_step(self, step: TestStep, config: VirtualDisplayConfig):
        """Execute send message step"""
        if not step.data:
            raise ValueError("Send step requires data")
        
        await self.serial_emulator.send_message(
            config.port_name, step.data, config
        )
    
    async def _execute_wait_step(self, step: TestStep):
        """Execute wait step"""
        wait_time = step.parameters.get("duration", 1000) / 1000.0
        await asyncio.sleep(wait_time)
    
    async def _execute_clear_step(self, step: TestStep, config: VirtualDisplayConfig):
        """Execute clear display step"""
        await self.serial_emulator.send_message(
            config.port_name, "", config
        )
    
    async def _execute_validate_step(self, step: TestStep, config: VirtualDisplayConfig):
        """Execute validation step"""
        # Get current display state
        display = self.serial_emulator.get_display_state(config.port_name)
        if not display:
            raise ValueError("Display not found or not active")
        
        # Validate based on expected result
        if step.expected_result:
            validation_result = await self.validator.validate_display_content(
                display, step.expected_result
            )
            if not validation_result.is_valid:
                raise ValueError(f"Validation failed: {validation_result.error_message}")
    
    def generate_report(self, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """Generate test execution report"""
        if not self.results:
            return {"error": "No test results available"}
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.status == ResultStatus.PASSED)
        failed_tests = sum(1 for r in self.results if r.status == ResultStatus.FAILED)
        
        total_duration = sum(r.duration or 0 for r in self.results)
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
                "total_duration": total_duration,
                "generated_at": datetime.now().isoformat()
            },
            "results": []
        }
        
        for result in self.results:
            report["results"].append({
                "scenario_id": result.scenario_id,
                "scenario_name": result.scenario_name,
                "status": result.status.value,
                "duration": result.duration,
                "start_time": result.start_time.isoformat() if result.start_time else None,
                "end_time": result.end_time.isoformat() if result.end_time else None,
                "error_message": result.error_message,
                "steps": result.step_results
            })
        
        # Save to file if path provided
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Test report saved to: {output_path}")
        
        return report
    
    def clear_results(self):
        """Clear test results"""
        self.results.clear()
        self.logger.info("Test results cleared")


class ContinuousTestRunner:
    """Continuous integration test runner"""
    
    def __init__(self, test_runner: TestRunner):
        self.test_runner = test_runner
        self.logger = setup_logger('continuous_runner')
        self.is_running = False
        
    async def run_continuous_tests(self, scenarios: List[TestScenario],
                                  config: VirtualDisplayConfig,
                                  interval: int = 3600):  # 1 hour default
        """Run tests continuously at specified interval"""
        self.is_running = True
        self.logger.info(f"Starting continuous testing (interval: {interval}s)")
        
        while self.is_running:
            try:
                self.logger.info("Running scheduled test cycle")
                await self.test_runner.run_scenarios(scenarios, config)
                
                # Generate report
                report_path = Path("reports") / f"continuous_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                self.test_runner.generate_report(report_path)
                
                # Wait for next cycle
                if self.is_running:
                    await asyncio.sleep(interval)
                    
            except Exception as e:
                self.logger.error(f"Continuous test cycle failed: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    def stop(self):
        """Stop continuous testing"""
        self.is_running = False
        self.logger.info("Stopping continuous testing")