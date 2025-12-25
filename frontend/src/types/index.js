// Type definitions for TypeScript-like development

export const SEVERITY_LEVELS = {
  CRITICAL: 'critical',
  HIGH: 'high',
  MEDIUM: 'medium',
  LOW: 'low',
};

export const ALERT_STATUS = {
  OPEN: 'open',
  INVESTIGATING: 'investigating',
  RESOLVED: 'resolved',
  FALSE_POSITIVE: 'false_positive',
};

export const INCIDENT_STATUS = {
  OPEN: 'open',
  INVESTIGATING: 'investigating',
  CONTAINED: 'contained',
  RESOLVED: 'resolved',
};

export const EVENT_TYPES = {
  AUTH_FAILURE: 'authentication_failure',
  AUTH_SUCCESS: 'authentication_success',
  FIREWALL_BLOCK: 'firewall_block',
  FIREWALL_ALLOW: 'firewall_allow',
  INTRUSION: 'intrusion',
  MALWARE: 'malware',
  OTHER: 'other',
};

export const RULE_TYPES = {
  SIGNATURE: 'signature',
  BEHAVIORAL: 'behavioral',
  CORRELATION: 'correlation',
};
