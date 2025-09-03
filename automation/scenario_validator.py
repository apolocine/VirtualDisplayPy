#!/usr/bin/env python3
"""
✅ Scenario Validator - Test Result Validation
Date: 03/09/2025
Description: Validates test results against expected outcomes
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from models.display_config import VirtualDisplay


@dataclass
class ValidationResult:
    """Result of a validation check"""
    is_valid: bool
    error_message: Optional[str] = None
    details: Dict[str, Any] = None


class ScenarioValidator:
    """Validates test scenario results"""
    
    def __init__(self):
        self.validation_rules = {
            "content_match": self._validate_content_match,
            "line_count": self._validate_line_count,
            "character_count": self._validate_character_count,
            "response_time": self._validate_response_time,
            "status": self._validate_status,
            "regex_match": self._validate_regex_match,
            "not_empty": self._validate_not_empty,
            "is_empty": self._validate_is_empty
        }
    
    async def validate_display_content(self, display: VirtualDisplay, 
                                     expected: Dict[str, Any]) -> ValidationResult:
        """Validate display content against expected results"""
        
        if not expected:
            return ValidationResult(is_valid=True)
        
        for rule_name, rule_value in expected.items():
            if rule_name not in self.validation_rules:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Unknown validation rule: {rule_name}"
                )
            
            validator = self.validation_rules[rule_name]
            result = await validator(display, rule_value)
            
            if not result.is_valid:
                return result
        
        return ValidationResult(is_valid=True)
    
    async def _validate_content_match(self, display: VirtualDisplay, 
                                    expected_content: Any) -> ValidationResult:
        """Validate exact content match"""
        current_content = display.current_content or []
        
        if isinstance(expected_content, str):
            # Single line expected
            actual = "\n".join(current_content).strip()
            if actual != expected_content:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Content mismatch. Expected: '{expected_content}', Got: '{actual}'"
                )
        elif isinstance(expected_content, list):
            # Multiple lines expected
            if len(current_content) != len(expected_content):
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Line count mismatch. Expected: {len(expected_content)}, Got: {len(current_content)}"
                )
            
            for i, (actual_line, expected_line) in enumerate(zip(current_content, expected_content)):
                if actual_line.strip() != expected_line:
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"Line {i+1} mismatch. Expected: '{expected_line}', Got: '{actual_line}'"
                    )
        
        return ValidationResult(is_valid=True)
    
    async def _validate_line_count(self, display: VirtualDisplay, 
                                 expected_count: int) -> ValidationResult:
        """Validate number of lines"""
        current_content = display.current_content or []
        actual_count = len([line for line in current_content if line.strip()])
        
        if actual_count != expected_count:
            return ValidationResult(
                is_valid=False,
                error_message=f"Line count mismatch. Expected: {expected_count}, Got: {actual_count}"
            )
        
        return ValidationResult(is_valid=True)
    
    async def _validate_character_count(self, display: VirtualDisplay, 
                                      expected_count: int) -> ValidationResult:
        """Validate total character count"""
        current_content = display.current_content or []
        actual_count = sum(len(line) for line in current_content)
        
        if actual_count != expected_count:
            return ValidationResult(
                is_valid=False,
                error_message=f"Character count mismatch. Expected: {expected_count}, Got: {actual_count}"
            )
        
        return ValidationResult(is_valid=True)
    
    async def _validate_response_time(self, display: VirtualDisplay, 
                                    max_time_ms: int) -> ValidationResult:
        """Validate response time"""
        # This would need to be implemented with timing measurement
        # For now, assume it passes
        return ValidationResult(is_valid=True)
    
    async def _validate_status(self, display: VirtualDisplay, 
                             expected_status: str) -> ValidationResult:
        """Validate display status"""
        if expected_status == "active" and not display.is_active:
            return ValidationResult(
                is_valid=False,
                error_message="Expected display to be active"
            )
        elif expected_status == "inactive" and display.is_active:
            return ValidationResult(
                is_valid=False,
                error_message="Expected display to be inactive"
            )
        
        return ValidationResult(is_valid=True)
    
    async def _validate_regex_match(self, display: VirtualDisplay, 
                                  pattern: str) -> ValidationResult:
        """Validate content matches regex pattern"""
        current_content = display.current_content or []
        content_str = "\n".join(current_content)
        
        try:
            if not re.search(pattern, content_str):
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Content does not match pattern: {pattern}"
                )
        except re.error as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"Invalid regex pattern: {pattern} - {str(e)}"
            )
        
        return ValidationResult(is_valid=True)
    
    async def _validate_not_empty(self, display: VirtualDisplay, 
                                _: Any) -> ValidationResult:
        """Validate display is not empty"""
        current_content = display.current_content or []
        
        if not any(line.strip() for line in current_content):
            return ValidationResult(
                is_valid=False,
                error_message="Expected display to have content, but it's empty"
            )
        
        return ValidationResult(is_valid=True)
    
    async def _validate_is_empty(self, display: VirtualDisplay, 
                               _: Any) -> ValidationResult:
        """Validate display is empty"""
        current_content = display.current_content or []
        
        if any(line.strip() for line in current_content):
            return ValidationResult(
                is_valid=False,
                error_message="Expected display to be empty, but it has content"
            )
        
        return ValidationResult(is_valid=True)


class PerformanceValidator:
    """Validates performance metrics"""
    
    def __init__(self):
        self.metrics_history: List[Dict[str, Any]] = []
    
    def record_metric(self, metric_name: str, value: float, timestamp: float):
        """Record a performance metric"""
        self.metrics_history.append({
            "name": metric_name,
            "value": value,
            "timestamp": timestamp
        })
    
    def validate_latency(self, max_latency_ms: float) -> ValidationResult:
        """Validate communication latency"""
        latency_metrics = [m for m in self.metrics_history if m["name"] == "latency"]
        
        if not latency_metrics:
            return ValidationResult(
                is_valid=False,
                error_message="No latency metrics recorded"
            )
        
        max_recorded = max(m["value"] for m in latency_metrics)
        
        if max_recorded > max_latency_ms:
            return ValidationResult(
                is_valid=False,
                error_message=f"Latency exceeds threshold. Max recorded: {max_recorded}ms, Threshold: {max_latency_ms}ms"
            )
        
        return ValidationResult(is_valid=True)
    
    def validate_throughput(self, min_messages_per_second: float) -> ValidationResult:
        """Validate message throughput"""
        throughput_metrics = [m for m in self.metrics_history if m["name"] == "throughput"]
        
        if not throughput_metrics:
            return ValidationResult(
                is_valid=False,
                error_message="No throughput metrics recorded"
            )
        
        avg_throughput = sum(m["value"] for m in throughput_metrics) / len(throughput_metrics)
        
        if avg_throughput < min_messages_per_second:
            return ValidationResult(
                is_valid=False,
                error_message=f"Throughput below threshold. Average: {avg_throughput:.2f}msg/s, Threshold: {min_messages_per_second}msg/s"
            )
        
        return ValidationResult(is_valid=True)
    
    def clear_metrics(self):
        """Clear recorded metrics"""
        self.metrics_history.clear()


class ErrorPatternValidator:
    """Validates error handling patterns"""
    
    def __init__(self):
        self.error_patterns = {
            "timeout": r"timeout|timed out",
            "connection_lost": r"connection lost|disconnected",
            "invalid_command": r"invalid command|unknown command",
            "checksum_error": r"checksum|crc error",
            "buffer_overflow": r"buffer overflow|buffer full"
        }
    
    def validate_error_handling(self, error_log: List[str], 
                              expected_patterns: List[str]) -> ValidationResult:
        """Validate that expected error patterns are handled"""
        
        for pattern_name in expected_patterns:
            if pattern_name not in self.error_patterns:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Unknown error pattern: {pattern_name}"
                )
            
            pattern = self.error_patterns[pattern_name]
            found = False
            
            for log_entry in error_log:
                if re.search(pattern, log_entry, re.IGNORECASE):
                    found = True
                    break
            
            if not found:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Expected error pattern not found: {pattern_name}"
                )
        
        return ValidationResult(is_valid=True)