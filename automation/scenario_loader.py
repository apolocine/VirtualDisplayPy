#!/usr/bin/env python3
"""
📂 Scenario Loader - Test Scenario Loading and Management
Date: 03/09/2025
Description: Loads test scenarios from various sources (YAML, JSON, Python)
"""

import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import asdict

from models.test_scenario import TestScenario, TestStep, ScenarioCategory
from utils.logger import setup_logger


class ScenarioLoader:
    """Loads and manages test scenarios"""
    
    def __init__(self):
        self.logger = setup_logger('scenario_loader')
        self.scenarios: Dict[str, TestScenario] = {}
        
    def load_from_yaml(self, file_path: Path) -> List[TestScenario]:
        """Load scenarios from YAML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            scenarios = []
            for scenario_data in data.get('scenarios', []):
                scenario = self._parse_scenario_data(scenario_data)
                scenarios.append(scenario)
                self.scenarios[scenario.id] = scenario
            
            self.logger.info(f"Loaded {len(scenarios)} scenarios from {file_path}")
            return scenarios
            
        except Exception as e:
            self.logger.error(f"Failed to load scenarios from {file_path}: {str(e)}")
            return []
    
    def load_from_json(self, file_path: Path) -> List[TestScenario]:
        """Load scenarios from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            scenarios = []
            for scenario_data in data.get('scenarios', []):
                scenario = self._parse_scenario_data(scenario_data)
                scenarios.append(scenario)
                self.scenarios[scenario.id] = scenario
            
            self.logger.info(f"Loaded {len(scenarios)} scenarios from {file_path}")
            return scenarios
            
        except Exception as e:
            self.logger.error(f"Failed to load scenarios from {file_path}: {str(e)}")
            return []
    
    def load_from_directory(self, directory: Path) -> List[TestScenario]:
        """Load all scenarios from directory"""
        all_scenarios = []
        
        # Load YAML files
        for yaml_file in directory.glob("*.yaml"):
            scenarios = self.load_from_yaml(yaml_file)
            all_scenarios.extend(scenarios)
        
        for yml_file in directory.glob("*.yml"):
            scenarios = self.load_from_yaml(yml_file)
            all_scenarios.extend(scenarios)
        
        # Load JSON files
        for json_file in directory.glob("*.json"):
            scenarios = self.load_from_json(json_file)
            all_scenarios.extend(scenarios)
        
        return all_scenarios
    
    def save_to_yaml(self, scenarios: List[TestScenario], file_path: Path):
        """Save scenarios to YAML file"""
        try:
            data = {
                'scenarios': [self._scenario_to_dict(scenario) for scenario in scenarios]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Saved {len(scenarios)} scenarios to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save scenarios to {file_path}: {str(e)}")
    
    def save_to_json(self, scenarios: List[TestScenario], file_path: Path):
        """Save scenarios to JSON file"""
        try:
            data = {
                'scenarios': [self._scenario_to_dict(scenario) for scenario in scenarios]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(scenarios)} scenarios to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save scenarios to {file_path}: {str(e)}")
    
    def get_scenario(self, scenario_id: str) -> Optional[TestScenario]:
        """Get scenario by ID"""
        return self.scenarios.get(scenario_id)
    
    def get_scenarios_by_category(self, category: ScenarioCategory) -> List[TestScenario]:
        """Get scenarios by category"""
        return [s for s in self.scenarios.values() if s.category == category]
    
    def get_scenarios_by_tags(self, tags: List[str]) -> List[TestScenario]:
        """Get scenarios that have any of the specified tags"""
        return [
            s for s in self.scenarios.values() 
            if any(tag in s.tags for tag in tags)
        ]
    
    def _parse_scenario_data(self, data: Dict[str, Any]) -> TestScenario:
        """Parse scenario data from dict"""
        # Parse steps
        steps = []
        for step_data in data.get('steps', []):
            step = TestStep(
                name=step_data['name'],
                action=step_data['action'],
                data=step_data.get('data'),
                expected_result=step_data.get('expected_result'),
                parameters=step_data.get('parameters', {}),
                delay_after=step_data.get('delay_after', 0)
            )
            steps.append(step)
        
        # Parse category
        category_str = data.get('category', 'basic')
        try:
            category = ScenarioCategory(category_str)
        except ValueError:
            category = ScenarioCategory.BASIC
        
        return TestScenario(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            category=category,
            tags=data.get('tags', []),
            steps=steps,
            expected_duration=data.get('expected_duration', 10.0),
            priority=data.get('priority', 'medium'),
            enabled=data.get('enabled', True)
        )
    
    def _scenario_to_dict(self, scenario: TestScenario) -> Dict[str, Any]:
        """Convert scenario to dictionary for serialization"""
        return {
            'id': scenario.id,
            'name': scenario.name,
            'description': scenario.description,
            'category': scenario.category.value,
            'tags': scenario.tags,
            'steps': [
                {
                    'name': step.name,
                    'action': step.action,
                    'data': step.data,
                    'expected_result': step.expected_result,
                    'parameters': step.parameters,
                    'delay_after': step.delay_after
                }
                for step in scenario.steps
            ],
            'expected_duration': scenario.expected_duration,
            'priority': scenario.priority,
            'enabled': scenario.enabled
        }


def create_default_scenarios() -> List[TestScenario]:
    """Create default test scenarios"""
    return [
        # Basic display test
        TestScenario(
            id="basic_display_test",
            name="Test d'Affichage de Base",
            description="Test simple d'affichage de texte",
            category=ScenarioCategory.BASIC,
            tags=["basic", "display"],
            steps=[
                TestStep(
                    name="Effacer l'afficheur",
                    action="clear",
                    expected_result={"is_empty": True}
                ),
                TestStep(
                    name="Afficher message simple",
                    action="send",
                    data="Hello World",
                    expected_result={"content_match": "Hello World"}
                ),
                TestStep(
                    name="Attendre 2 secondes",
                    action="wait",
                    parameters={"duration": 2000},
                    delay_after=2000
                )
            ],
            expected_duration=5.0,
            priority="high",
            enabled=True
        ),
        
        # Multi-line test
        TestScenario(
            id="multiline_display_test",
            name="Test d'Affichage Multi-lignes",
            description="Test d'affichage sur plusieurs lignes",
            category=ScenarioCategory.FUNCTIONAL,
            tags=["multiline", "display"],
            steps=[
                TestStep(
                    name="Effacer l'afficheur",
                    action="clear",
                    expected_result={"is_empty": True}
                ),
                TestStep(
                    name="Afficher ligne 1",
                    action="send",
                    data="Ligne 1",
                    expected_result={"content_match": ["Ligne 1"]}
                ),
                TestStep(
                    name="Afficher ligne 2",
                    action="send",
                    data="Ligne 2",
                    expected_result={"content_match": ["Ligne 1", "Ligne 2"]}
                )
            ],
            expected_duration=3.0,
            priority="medium",
            enabled=True
        ),
        
        # Performance test
        TestScenario(
            id="performance_test",
            name="Test de Performance",
            description="Test de performance et latence",
            category=ScenarioCategory.PERFORMANCE,
            tags=["performance", "latency"],
            steps=[
                TestStep(
                    name="Envoi rapide de messages",
                    action="send",
                    data="Performance Test",
                    parameters={"repeat": 10, "interval": 100},
                    expected_result={"response_time": 50}
                )
            ],
            expected_duration=5.0,
            priority="medium",
            enabled=True
        ),
        
        # USB display test
        TestScenario(
            id="usb_display_test",
            name="Test d'Afficheur USB",
            description="Test spécifique pour afficheur USB",
            category=ScenarioCategory.HARDWARE,
            tags=["usb", "hardware"],
            steps=[
                TestStep(
                    name="Vérifier connexion USB",
                    action="validate",
                    expected_result={"status": "active"}
                ),
                TestStep(
                    name="Test message USB",
                    action="send",
                    data="USB Display OK",
                    expected_result={"content_match": "USB Display OK"}
                )
            ],
            expected_duration=3.0,
            priority="high",
            enabled=True
        )
    ]


def save_default_scenarios(output_dir: Path):
    """Save default scenarios to files"""
    scenarios = create_default_scenarios()
    loader = ScenarioLoader()
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as YAML
    loader.save_to_yaml(scenarios, output_dir / "default_scenarios.yaml")
    
    # Save as JSON
    loader.save_to_json(scenarios, output_dir / "default_scenarios.json")
    
    # Save by category
    for category in ScenarioCategory:
        category_scenarios = [s for s in scenarios if s.category == category]
        if category_scenarios:
            loader.save_to_yaml(
                category_scenarios, 
                output_dir / f"{category.value}_scenarios.yaml"
            )