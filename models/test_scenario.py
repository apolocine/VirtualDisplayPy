"""
🖥️ Test Scenario Models
Date: 03/09/2025
Description: Test scenarios and automation models
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
from enum import Enum


class TestStatus(Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ResultStatus(Enum):
    """Result status for test execution"""
    PENDING = "pending"
    RUNNING = "running" 
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ScenarioCategory(Enum):
    """Test scenario categories"""
    BASIC = "basic"
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    STRESS = "stress"
    ERROR_HANDLING = "error_handling"
    INTEGRATION = "integration"
    HARDWARE = "hardware"


class ValidationRuleType(Enum):
    """Types of validation rules"""
    EQUALS = "equals"
    CONTAINS = "contains"
    MATCHES = "matches"
    RANGE = "range"
    CUSTOM = "custom"


@dataclass
class ValidationRule:
    """Validation rule for tests"""
    type: ValidationRuleType
    field: str
    value: Any
    message: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of a validation rule"""
    rule: ValidationRule
    passed: bool
    actual_value: Any
    message: str


@dataclass
class TestStep:
    """Individual test step - simple version for scenario loading"""
    name: str
    action: str
    data: Optional[str] = None
    expected_result: Optional[Any] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    delay_after: int = 0  # milliseconds
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class StepResult:
    """Result of test step execution"""
    step_id: str
    action: str
    
    # Timing
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    
    # Result
    passed: bool = False
    result: Optional[Any] = None
    error: Optional[str] = None
    
    # Validations
    validations: List[ValidationResult] = field(default_factory=list)
    
    # Step metrics
    step_metrics: Optional[Dict[str, Any]] = None


@dataclass
class SuccessCriteria:
    """Success criteria for tests"""
    min_success_rate: float = 95.0  # percentage
    max_error_rate: float = 5.0  # percentage
    max_latency: float = 1000.0  # milliseconds
    required_steps: List[str] = field(default_factory=list)  # Required step IDs
    custom_validations: List[ValidationRule] = field(default_factory=list)


@dataclass
class TestScenario:
    """Test scenario definition"""
    id: str
    name: str
    description: str
    category: ScenarioCategory = ScenarioCategory.BASIC
    tags: List[str] = field(default_factory=list)
    steps: List[TestStep] = field(default_factory=list)
    expected_duration: float = 10.0
    priority: str = "medium"
    enabled: bool = True


@dataclass
class TestResult:
    """Test execution result"""
    scenario_id: str
    scenario_name: str
    
    # Timing
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    
    # Results  
    status: ResultStatus = ResultStatus.PENDING
    passed: bool = False
    success_rate: float = 0.0
    
    # Details
    steps: List[StepResult] = field(default_factory=list)
    step_results: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list) 
    error_message: Optional[str] = None
    
    # Metrics
    metrics: Dict[str, Any] = field(default_factory=lambda: {
        "total_steps": 0,
        "passed_steps": 0,
        "failed_steps": 0,
        "skipped_steps": 0,
        "avg_step_duration": 0.0,
        "total_messages": 0,
        "avg_latency": 0.0,
        "error_count": 0
    })
    
    # Environment context
    environment: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestReport:
    """Complete test report"""
    id: str
    name: str
    generated_at: datetime
    
    # Executive summary
    summary: Dict[str, Any] = field(default_factory=lambda: {
        "total_scenarios": 0,
        "passed_scenarios": 0,
        "failed_scenarios": 0,
        "skipped_scenarios": 0,
        "overall_pass_rate": 0.0,
        "total_duration": 0.0
    })
    
    # Detailed results
    results: List[TestResult] = field(default_factory=list)
    
    # Analysis
    analysis: Dict[str, Any] = field(default_factory=lambda: {
        "top_errors": [],
        "performance_stats": {
            "avg_latency": 0.0,
            "max_latency": 0.0,
            "throughput": 0.0
        },
        "recommendations": []
    })
    
    # Environment metadata
    environment: Dict[str, Any] = field(default_factory=dict)


# Test action types and their expected parameters
TEST_ACTION_SCHEMAS = {
    "connect": {
        "description": "Connect to a display port",
        "parameters": ["port", "connection_type?", "timeout?"]
    },
    "send": {
        "description": "Send text message to display", 
        "parameters": ["message", "line?", "column?", "formatting?"]
    },
    "clear": {
        "description": "Clear display content",
        "parameters": ["method?"]
    },
    "validate": {
        "description": "Verify display shows expected content",
        "parameters": ["expected_content", "line?"]
    },
    "wait": {
        "description": "Wait for specified duration",
        "parameters": ["duration_ms"]
    }
}
