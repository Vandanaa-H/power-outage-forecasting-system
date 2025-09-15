from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import numpy as np

from src.api.models import WhatIfRequest, PredictionRequest
from src.utils.feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)


class ScenarioAnalyzer:
    """Analyzes what-if scenarios and parameter sensitivity."""
    
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        
    async def apply_modifications(self, 
                                base_scenario: PredictionRequest, 
                                modifications: Dict[str, Any]) -> PredictionRequest:
        """Apply parameter modifications to base scenario."""
        try:
            # Create a copy of the base scenario
            modified_scenario = base_scenario.copy(deep=True)
            
            # Apply modifications
            for param_path, new_value in modifications.items():
                self._set_nested_value(modified_scenario, param_path, new_value)
            
            return modified_scenario
            
        except Exception as e:
            logger.error(f"Scenario modification error: {str(e)}")
            return base_scenario
    
    async def analyze_impact(self, 
                           baseline_result: Dict[str, Any],
                           modified_result: Dict[str, Any],
                           modifications: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the impact of parameter changes."""
        try:
            risk_change = modified_result['risk_score'] - baseline_result['risk_score']
            
            analysis = {
                "risk_change": risk_change,
                "risk_change_percentage": (risk_change / max(baseline_result['risk_score'], 1)) * 100,
                "direction": "increase" if risk_change > 0 else "decrease" if risk_change < 0 else "no_change",
                "magnitude": self._categorize_change_magnitude(abs(risk_change)),
                "modified_parameters": modifications,
                "impact_breakdown": self._analyze_parameter_impacts(modifications, risk_change),
                "confidence_change": self._analyze_confidence_change(baseline_result, modified_result),
                "risk_level_change": self._analyze_risk_level_change(baseline_result, modified_result)
            }
            
            # Add interpretation
            analysis["interpretation"] = self._generate_impact_interpretation(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Impact analysis error: {str(e)}")
            return {"error": str(e)}
    
    async def analyze_batch_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze results from batch what-if simulations."""
        try:
            if not results:
                return {"error": "No results to analyze"}
            
            risk_changes = [r.risk_change for r in results]
            baseline_risks = [r.base_prediction.risk_score for r in results]
            modified_risks = [r.modified_prediction.risk_score for r in results]
            
            summary = {
                "total_simulations": len(results),
                "average_risk_change": np.mean(risk_changes),
                "max_risk_change": max(risk_changes),
                "min_risk_change": min(risk_changes),
                "risk_change_std": np.std(risk_changes),
                "scenarios_increasing_risk": len([r for r in risk_changes if r > 0]),
                "scenarios_decreasing_risk": len([r for r in risk_changes if r < 0]),
                "most_impactful_scenario": self._find_most_impactful_scenario(results),
                "correlation_analysis": self._analyze_parameter_correlations(results)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Batch analysis error: {str(e)}")
            return {"error": str(e)}
    
    async def calculate_sensitivity_metrics(self, 
                                          parameter: str,
                                          parameter_values: List[float],
                                          results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate sensitivity metrics for parameter analysis."""
        try:
            risk_scores = [r['risk_score'] for r in results]
            
            # Calculate sensitivity coefficient
            param_range = max(parameter_values) - min(parameter_values)
            risk_range = max(risk_scores) - min(risk_scores)
            sensitivity = risk_range / param_range if param_range > 0 else 0
            
            # Calculate correlation
            correlation = np.corrcoef(parameter_values, risk_scores)[0, 1] if len(parameter_values) > 1 else 0
            
            # Find threshold values
            threshold_analysis = self._find_risk_thresholds(parameter_values, risk_scores)
            
            metrics = {
                "sensitivity_coefficient": sensitivity,
                "correlation": correlation,
                "parameter_elasticity": self._calculate_elasticity(parameter_values, risk_scores),
                "threshold_analysis": threshold_analysis,
                "risk_gradient": self._calculate_risk_gradient(parameter_values, risk_scores),
                "optimal_range": self._find_optimal_parameter_range(parameter_values, risk_scores)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Sensitivity metrics error: {str(e)}")
            return {"error": str(e)}
    
    def _set_nested_value(self, obj: Any, path: str, value: Any):
        """Set nested attribute value using dot notation."""
        parts = path.split('.')
        current = obj
        
        for part in parts[:-1]:
            if hasattr(current, part):
                current = getattr(current, part)
            else:
                raise ValueError(f"Invalid parameter path: {path}")
        
        setattr(current, parts[-1], value)
    
    def _categorize_change_magnitude(self, change: float) -> str:
        """Categorize the magnitude of risk change."""
        if change < 5:
            return "minimal"
        elif change < 15:
            return "moderate"
        elif change < 30:
            return "significant"
        else:
            return "major"
    
    def _analyze_parameter_impacts(self, 
                                 modifications: Dict[str, Any], 
                                 total_change: float) -> Dict[str, Any]:
        """Analyze individual parameter impacts."""
        impacts = {}
        
        for param, value in modifications.items():
            # Estimate individual parameter contribution
            if "rainfall" in param.lower():
                impact_factor = min(float(value) / 50.0, 1.0)  # Normalize by 50mm
            elif "wind_speed" in param.lower():
                impact_factor = min(float(value) / 100.0, 1.0)  # Normalize by 100 km/h
            elif "temperature" in param.lower():
                impact_factor = min(abs(float(value) - 25) / 20.0, 1.0)  # Deviation from 25°C
            elif "load_factor" in param.lower():
                impact_factor = float(value)
            else:
                impact_factor = 0.5  # Default for unknown parameters
            
            estimated_contribution = total_change * impact_factor * 0.7  # Conservative estimate
            
            impacts[param] = {
                "estimated_contribution": estimated_contribution,
                "impact_factor": impact_factor,
                "parameter_value": value
            }
        
        return impacts
    
    def _analyze_confidence_change(self, 
                                 baseline: Dict[str, Any], 
                                 modified: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze changes in prediction confidence."""
        baseline_ci = baseline.get('confidence_interval', {})
        modified_ci = modified.get('confidence_interval', {})
        
        baseline_width = baseline_ci.get('upper', 0) - baseline_ci.get('lower', 0)
        modified_width = modified_ci.get('upper', 0) - modified_ci.get('lower', 0)
        
        return {
            "confidence_width_change": modified_width - baseline_width,
            "uncertainty_change": "increased" if modified_width > baseline_width else "decreased",
            "baseline_uncertainty": baseline_width,
            "modified_uncertainty": modified_width
        }
    
    def _analyze_risk_level_change(self, 
                                 baseline: Dict[str, Any], 
                                 modified: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze risk level category changes."""
        def get_risk_level(score):
            if score >= 80:
                return "critical"
            elif score >= 60:
                return "high"
            elif score >= 30:
                return "medium"
            else:
                return "low"
        
        baseline_level = get_risk_level(baseline['risk_score'])
        modified_level = get_risk_level(modified['risk_score'])
        
        return {
            "baseline_level": baseline_level,
            "modified_level": modified_level,
            "level_changed": baseline_level != modified_level,
            "escalation": modified_level != baseline_level and modified['risk_score'] > baseline['risk_score']
        }
    
    def _generate_impact_interpretation(self, analysis: Dict[str, Any]) -> str:
        """Generate natural language interpretation of impact."""
        risk_change = analysis['risk_change']
        magnitude = analysis['magnitude']
        direction = analysis['direction']
        
        if direction == "no_change":
            return "The parameter changes had negligible impact on outage risk."
        
        direction_text = "increased" if direction == "increase" else "decreased"
        
        interpretation = f"The modifications {direction_text} outage risk by {abs(risk_change):.1f} points, "
        interpretation += f"representing a {magnitude} change. "
        
        if analysis.get('risk_level_change', {}).get('level_changed'):
            baseline_level = analysis['risk_level_change']['baseline_level']
            modified_level = analysis['risk_level_change']['modified_level']
            interpretation += f"Risk level changed from {baseline_level} to {modified_level}. "
        
        # Add parameter-specific insights
        modified_params = analysis['modified_parameters']
        if 'weather_data.rainfall' in modified_params:
            rainfall = modified_params['weather_data.rainfall']
            if rainfall > 25:
                interpretation += "Heavy rainfall is a major contributing factor. "
        
        if 'weather_data.wind_speed' in modified_params:
            wind = modified_params['weather_data.wind_speed']
            if wind > 50:
                interpretation += "Strong winds significantly impact grid stability. "
        
        return interpretation
    
    def _find_most_impactful_scenario(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find the scenario with the highest impact."""
        if not results:
            return {}
        
        max_impact_scenario = max(results, key=lambda x: abs(x.risk_change))
        
        return {
            "scenario_name": max_impact_scenario.scenario_name,
            "risk_change": max_impact_scenario.risk_change,
            "impact_type": "increase" if max_impact_scenario.risk_change > 0 else "decrease"
        }
    
    def _analyze_parameter_correlations(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze correlations between parameters and risk changes."""
        # This would perform more sophisticated correlation analysis
        # For now, return basic analysis
        return {
            "strong_correlations": [],
            "weak_correlations": [],
            "analysis_note": "Detailed correlation analysis requires more data points"
        }
    
    def _find_risk_thresholds(self, 
                            parameter_values: List[float], 
                            risk_scores: List[float]) -> Dict[str, Any]:
        """Find parameter values that cross risk thresholds."""
        thresholds = {"low_to_medium": 30, "medium_to_high": 60, "high_to_critical": 80}
        threshold_crossings = {}
        
        for threshold_name, threshold_value in thresholds.items():
            crossings = []
            for i, risk in enumerate(risk_scores):
                if i > 0:
                    prev_risk = risk_scores[i-1]
                    if (prev_risk < threshold_value <= risk) or (prev_risk > threshold_value >= risk):
                        crossings.append({
                            "parameter_value": parameter_values[i],
                            "risk_score": risk,
                            "crossing_direction": "up" if risk > prev_risk else "down"
                        })
            
            threshold_crossings[threshold_name] = crossings
        
        return threshold_crossings
    
    def _calculate_elasticity(self, 
                            parameter_values: List[float], 
                            risk_scores: List[float]) -> float:
        """Calculate parameter elasticity of risk."""
        if len(parameter_values) < 2:
            return 0.0
        
        # Calculate percentage changes
        param_changes = []
        risk_changes = []
        
        for i in range(1, len(parameter_values)):
            if parameter_values[i-1] != 0 and risk_scores[i-1] != 0:
                param_pct_change = (parameter_values[i] - parameter_values[i-1]) / parameter_values[i-1]
                risk_pct_change = (risk_scores[i] - risk_scores[i-1]) / risk_scores[i-1]
                
                if param_pct_change != 0:
                    elasticity = risk_pct_change / param_pct_change
                    param_changes.append(param_pct_change)
                    risk_changes.append(elasticity)
        
        return np.mean(risk_changes) if risk_changes else 0.0
    
    def _calculate_risk_gradient(self, 
                               parameter_values: List[float], 
                               risk_scores: List[float]) -> List[float]:
        """Calculate risk gradient (rate of change)."""
        if len(parameter_values) < 2:
            return []
        
        gradients = []
        for i in range(1, len(parameter_values)):
            param_diff = parameter_values[i] - parameter_values[i-1]
            risk_diff = risk_scores[i] - risk_scores[i-1]
            
            gradient = risk_diff / param_diff if param_diff != 0 else 0
            gradients.append(gradient)
        
        return gradients
    
    def _find_optimal_parameter_range(self, 
                                    parameter_values: List[float], 
                                    risk_scores: List[float]) -> Dict[str, Any]:
        """Find parameter range that minimizes risk."""
        if not parameter_values:
            return {}
        
        min_risk_idx = np.argmin(risk_scores)
        optimal_value = parameter_values[min_risk_idx]
        min_risk = risk_scores[min_risk_idx]
        
        # Find range within 10% of minimum risk
        tolerance = min_risk * 0.1
        optimal_range = []
        
        for i, risk in enumerate(risk_scores):
            if risk <= min_risk + tolerance:
                optimal_range.append(parameter_values[i])
        
        return {
            "optimal_value": optimal_value,
            "minimum_risk": min_risk,
            "optimal_range": {
                "min": min(optimal_range) if optimal_range else optimal_value,
                "max": max(optimal_range) if optimal_range else optimal_value
            },
            "risk_reduction_potential": max(risk_scores) - min_risk
        }
