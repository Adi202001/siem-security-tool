from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.rule import DetectionRule
from app.models.alert import Alert
from app.schemas.alert import AlertCreate


class RuleEngine:
    """Rule-based threat detection engine"""

    def __init__(self):
        self.active_rules: List[DetectionRule] = []

    async def load_rules(self, db: AsyncSession):
        """Load active detection rules from database"""
        result = await db.execute(
            select(DetectionRule).where(DetectionRule.is_active == True)
        )
        self.active_rules = list(result.scalars().all())

    async def evaluate_log(
        self,
        log_data: Dict[str, Any],
        db: AsyncSession
    ) -> List[AlertCreate]:
        """
        Evaluate a log against all active rules
        Returns list of alerts to create
        """
        alerts = []

        for rule in self.active_rules:
            if self._check_rule(log_data, rule.conditions):
                alert = AlertCreate(
                    alert_type="rule-based",
                    severity=rule.severity,
                    title=f"Rule triggered: {rule.name}",
                    description=f"Detection rule '{rule.name}' was triggered. {rule.description}",
                    source=log_data.get('source_ip'),
                    destination=log_data.get('destination_ip'),
                    rule_id=rule.id,
                )
                alerts.append(alert)

                # Update rule statistics
                rule.last_triggered = datetime.utcnow()
                rule.trigger_count += 1
                await db.commit()

        return alerts

    def _check_rule(self, log_data: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
        """
        Check if log data matches rule conditions
        Supports various condition types
        """
        try:
            # Simple field matching
            if 'field_matches' in conditions:
                for field, expected_value in conditions['field_matches'].items():
                    if log_data.get(field) != expected_value:
                        return False

            # Field contains
            if 'field_contains' in conditions:
                for field, substring in conditions['field_contains'].items():
                    field_value = str(log_data.get(field, ''))
                    if substring.lower() not in field_value.lower():
                        return False

            # Severity threshold
            if 'min_severity' in conditions:
                severity_levels = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
                log_severity = severity_levels.get(log_data.get('severity', 'low'), 1)
                min_severity = severity_levels.get(conditions['min_severity'], 1)
                if log_severity < min_severity:
                    return False

            # Port range
            if 'port_range' in conditions:
                port = log_data.get('destination_port')
                if port:
                    min_port = conditions['port_range'].get('min', 0)
                    max_port = conditions['port_range'].get('max', 65535)
                    if not (min_port <= port <= max_port):
                        return False

            # IP blacklist
            if 'ip_blacklist' in conditions:
                source_ip = log_data.get('source_ip')
                if source_ip and source_ip in conditions['ip_blacklist']:
                    return True  # Immediate match for blacklisted IPs

            # Multiple failed attempts (requires session state - simplified here)
            if 'failed_attempts' in conditions:
                # This would need to track state across logs
                # For now, just check if it's a failed auth event
                if log_data.get('event_type') == 'authentication_failure':
                    return True

            # Protocol check
            if 'protocol' in conditions:
                if log_data.get('protocol') != conditions['protocol']:
                    return False

            # Custom regex pattern
            if 'regex_pattern' in conditions:
                import re
                pattern = conditions['regex_pattern']
                text = log_data.get('message', '') + ' ' + log_data.get('raw_log', '')
                if not re.search(pattern, text, re.IGNORECASE):
                    return False

            # All conditions passed
            return True

        except Exception as e:
            # Log error and don't trigger rule on evaluation errors
            print(f"Error evaluating rule: {e}")
            return False


# Global instance
rule_engine = RuleEngine()
