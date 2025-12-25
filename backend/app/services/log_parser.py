import re
from typing import Dict, Any, Optional
from datetime import datetime


class LogParser:
    """Parse various log formats into structured data"""

    def __init__(self):
        # Common log patterns
        self.patterns = {
            'syslog': re.compile(
                r'(?P<timestamp>\w+ \d+ \d+:\d+:\d+) (?P<hostname>\S+) '
                r'(?P<process>\S+?)(\[(?P<pid>\d+)\])?: (?P<message>.+)'
            ),
            'apache': re.compile(
                r'(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] '
                r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>\S+)" '
                r'(?P<status>\d+) (?P<size>\S+)'
            ),
            'firewall': re.compile(
                r'(?P<action>ACCEPT|DENY|DROP) (?P<protocol>\S+) '
                r'(?P<src_ip>\S+):(?P<src_port>\d+) -> '
                r'(?P<dst_ip>\S+):(?P<dst_port>\d+)'
            ),
            'auth': re.compile(
                r'(?P<timestamp>.*?) (?P<hostname>\S+) .*?'
                r'(?P<event>Failed password|Accepted password|Invalid user) '
                r'for (?P<user>\S+) from (?P<ip>\S+)'
            ),
        }

    def parse(self, raw_log: str, log_format: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse a raw log string into structured data
        If log_format is not specified, tries to auto-detect
        """
        if log_format and log_format in self.patterns:
            return self._parse_with_pattern(raw_log, log_format)

        # Try to auto-detect format
        for format_name, pattern in self.patterns.items():
            match = pattern.search(raw_log)
            if match:
                return self._parse_with_pattern(raw_log, format_name)

        # If no pattern matches, return basic parsing
        return self._parse_generic(raw_log)

    def _parse_with_pattern(self, raw_log: str, format_name: str) -> Dict[str, Any]:
        """Parse log with a specific pattern"""
        pattern = self.patterns[format_name]
        match = pattern.search(raw_log)

        if not match:
            return self._parse_generic(raw_log)

        data = match.groupdict()
        data['log_format'] = format_name

        # Standardize fields
        parsed = {
            'raw_log': raw_log,
            'log_format': format_name,
        }

        # Map fields to standard names
        if 'ip' in data:
            parsed['source_ip'] = data['ip']
        if 'src_ip' in data:
            parsed['source_ip'] = data['src_ip']
        if 'dst_ip' in data:
            parsed['destination_ip'] = data['dst_ip']
        if 'src_port' in data:
            parsed['source_port'] = int(data['src_port'])
        if 'dst_port' in data:
            parsed['destination_port'] = int(data['dst_port'])
        if 'protocol' in data:
            parsed['protocol'] = data['protocol']
        if 'hostname' in data:
            parsed['hostname'] = data['hostname']
        if 'user' in data:
            parsed['user'] = data['user']
        if 'action' in data:
            parsed['action'] = data['action'].lower()
        if 'event' in data:
            parsed['event_type'] = self._categorize_event(data['event'])
        if 'message' in data:
            parsed['message'] = data['message']

        # Determine severity
        parsed['severity'] = self._determine_severity(raw_log, data)

        # Additional parsed data
        parsed['parsed_data'] = data

        return parsed

    def _parse_generic(self, raw_log: str) -> Dict[str, Any]:
        """Generic parsing for unrecognized formats"""
        # Try to extract IP addresses
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ips = re.findall(ip_pattern, raw_log)

        # Try to extract common keywords
        severity = self._determine_severity(raw_log, {})

        return {
            'raw_log': raw_log,
            'log_format': 'generic',
            'message': raw_log,
            'severity': severity,
            'source_ip': ips[0] if len(ips) > 0 else None,
            'destination_ip': ips[1] if len(ips) > 1 else None,
            'event_type': 'unknown',
            'parsed_data': {'ips_found': ips}
        }

    def _categorize_event(self, event_string: str) -> str:
        """Categorize event based on keywords"""
        event_lower = event_string.lower()

        if 'failed' in event_lower or 'invalid' in event_lower:
            return 'authentication_failure'
        elif 'accepted' in event_lower or 'success' in event_lower:
            return 'authentication_success'
        elif 'deny' in event_lower or 'drop' in event_lower:
            return 'firewall_block'
        elif 'accept' in event_lower or 'allow' in event_lower:
            return 'firewall_allow'
        else:
            return 'other'

    def _determine_severity(self, raw_log: str, parsed_data: Dict[str, Any]) -> str:
        """Determine severity level based on content"""
        log_lower = raw_log.lower()

        # Critical indicators
        if any(word in log_lower for word in ['critical', 'emergency', 'fatal', 'panic']):
            return 'critical'

        # High severity indicators
        if any(word in log_lower for word in ['error', 'fail', 'denied', 'attack', 'breach', 'unauthorized']):
            return 'high'

        # Medium severity indicators
        if any(word in log_lower for word in ['warning', 'warn', 'suspicious', 'unusual']):
            return 'medium'

        # Check action
        if 'action' in parsed_data:
            action = parsed_data['action'].lower()
            if action in ['deny', 'drop', 'reject']:
                return 'medium'

        # Default to low
        return 'low'


# Global instance
log_parser = LogParser()
