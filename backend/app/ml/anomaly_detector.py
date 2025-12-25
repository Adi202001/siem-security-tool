import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta


class AnomalyDetector:
    """ML-based anomaly detection for security logs"""

    def __init__(self, model_path: str = "models/anomaly_detector.pkl"):
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            'source_port', 'destination_port', 'hour', 'day_of_week',
            'log_length', 'ip_entropy'
        ]

        # Load model if exists
        if os.path.exists(model_path):
            self.load_model()
        else:
            self._initialize_model()

    def _initialize_model(self):
        """Initialize a new Isolation Forest model"""
        self.model = IsolationForest(
            contamination=0.1,  # Expect 10% anomalies
            random_state=42,
            n_estimators=100
        )

    def extract_features(self, logs: List[Dict[str, Any]]) -> pd.DataFrame:
        """Extract features from raw logs for ML processing"""
        features = []

        for log in logs:
            timestamp = log.get('timestamp', datetime.utcnow())
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

            feature_dict = {
                'source_port': log.get('source_port', 0) or 0,
                'destination_port': log.get('destination_port', 0) or 0,
                'hour': timestamp.hour,
                'day_of_week': timestamp.weekday(),
                'log_length': len(log.get('message', '')),
                'ip_entropy': self._calculate_ip_entropy(log.get('source_ip', ''))
            }
            features.append(feature_dict)

        return pd.DataFrame(features)

    def _calculate_ip_entropy(self, ip: str) -> float:
        """Calculate entropy of IP address octets"""
        if not ip:
            return 0.0

        octets = ip.split('.')
        if len(octets) != 4:
            return 0.0

        try:
            values = [int(o) for o in octets]
            # Simple entropy calculation
            entropy = sum(v / 255.0 for v in values) / 4.0
            return entropy
        except ValueError:
            return 0.0

    def train(self, logs: List[Dict[str, Any]]):
        """Train the anomaly detection model on historical logs"""
        if len(logs) < 100:
            raise ValueError("Need at least 100 logs for training")

        df = self.extract_features(logs)
        X = df[self.feature_columns].values

        # Fit scaler and transform data
        X_scaled = self.scaler.fit_transform(X)

        # Train model
        self.model.fit(X_scaled)

        # Save model
        self.save_model()

    def predict(self, logs: List[Dict[str, Any]]) -> List[Tuple[bool, float]]:
        """
        Predict anomalies in logs
        Returns list of (is_anomaly, anomaly_score) tuples
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded")

        df = self.extract_features(logs)
        X = df[self.feature_columns].values

        # Transform data
        X_scaled = self.scaler.transform(X)

        # Predict anomalies (-1 for anomaly, 1 for normal)
        predictions = self.model.predict(X_scaled)

        # Get anomaly scores (lower is more anomalous)
        scores = self.model.score_samples(X_scaled)

        # Normalize scores to 0-1 range (higher is more anomalous)
        normalized_scores = 1 - (scores - scores.min()) / (scores.max() - scores.min() + 1e-10)

        results = []
        for pred, score in zip(predictions, normalized_scores):
            is_anomaly = pred == -1
            results.append((is_anomaly, float(score)))

        return results

    def predict_single(self, log: Dict[str, Any]) -> Tuple[bool, float]:
        """Predict anomaly for a single log"""
        results = self.predict([log])
        return results[0]

    def save_model(self):
        """Save model and scaler to disk"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns
        }, self.model_path)

    def load_model(self):
        """Load model and scaler from disk"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        data = joblib.load(self.model_path)
        self.model = data['model']
        self.scaler = data['scaler']
        self.feature_columns = data['feature_columns']


# Global instance
anomaly_detector = AnomalyDetector()
