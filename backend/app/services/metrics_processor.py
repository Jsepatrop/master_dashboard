# backend/app/services/metrics_processor.py
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import json

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.metrics import MetricData as MetricModel, MetricType
from app.models.machine import Machine as MachineModel
from app.models.configuration import SystemConfiguration as ConfigModel

logger = logging.getLogger(__name__)

class MetricsProcessor:
    def __init__(self):
        self.is_running = False
        self.processor_task = None
        self.aggregated_data: Dict[str, Dict] = {}
        self.processing_queue = asyncio.Queue()
        
    async def start(self):
        """Start the metrics processor"""
        if self.is_running:
            return
            
        self.is_running = True
        logger.info("Starting metrics processor...")
        
        # Start processing loop
        self.processor_task = asyncio.create_task(self._processing_loop())
        
        logger.info("Metrics processor started")
    
    async def stop(self):
        """Stop the metrics processor"""
        self.is_running = False
        
        if self.processor_task:
            self.processor_task.cancel()
            try:
                await self.processor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Metrics processor stopped")
    
    async def _processing_loop(self):
        """Main metrics processing loop"""
        while self.is_running:
            try:
                await self._process_metrics_batch()
                await self._cleanup_old_metrics()
                await self._update_machine_health_scores()
                await asyncio.sleep(60)  # Process every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics processing loop: {e}")
                await asyncio.sleep(10)
    
    async def _process_metrics_batch(self):
        """Process batch of metrics for analysis"""
        db = SessionLocal()
        try:
            # Get recent metrics (last 5 minutes)
            cutoff_time = datetime.utcnow() - timedelta(minutes=5)
            
            recent_metrics = db.query(MetricModel).filter(
                MetricModel.timestamp >= cutoff_time
            ).all()
            
            if not recent_metrics:
                return
            
            # Group metrics by machine and type
            metrics_by_machine = defaultdict(lambda: defaultdict(list))
            
            for metric in recent_metrics:
                machine_id = str(metric.machine_id)
                metrics_by_machine[machine_id][metric.metric_type].append(metric)
            
            # Process each machine's metrics
            for machine_id, machine_metrics in metrics_by_machine.items():
                await self._analyze_machine_metrics(machine_id, machine_metrics)
            
            logger.debug(f"Processed metrics for {len(metrics_by_machine)} machines")
            
        except Exception as e:
            logger.error(f"Error processing metrics batch: {e}")
        finally:
            db.close()
    
    async def _analyze_machine_metrics(self, machine_id: str, metrics: Dict[MetricType, List[MetricModel]]):
        """Analyze metrics for a single machine"""
        analysis = {
            "machine_id": machine_id,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics_summary": {},
            "anomalies": [],
            "health_score": 100,
            "recommendations": []
        }
        
        for metric_type, metric_list in metrics.items():
            if not metric_list:
                continue
            
            values = [m.value for m in metric_list]
            
            # Calculate statistics
            metric_stats = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": statistics.mean(values),
                "latest": values[-1] if values else 0,
                "trend": self._calculate_trend(values)
            }
            
            if len(values) > 1:
                metric_stats["stddev"] = statistics.stdev(values)
            
            analysis["metrics_summary"][metric_type.value] = metric_stats
            
            # Detect anomalies
            anomalies = self._detect_anomalies(metric_type, values)
            if anomalies:
                analysis["anomalies"].extend(anomalies)
            
            # Update health score based on metric values
            health_impact = self._calculate_health_impact(metric_type, metric_stats)
            analysis["health_score"] -= health_impact
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)
        
        # Store analysis results
        self.aggregated_data[machine_id] = analysis
        
        # Send to external systems if configured
        await self._export_analysis(analysis)
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for metric values"""
        if len(values) < 2:
            return "stable"
        
        # Simple trend calculation using first and last values
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        if not first_half or not second_half:
            return "stable"
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        diff_percent = ((second_avg - first_avg) / first_avg) * 100 if first_avg != 0 else 0
        
        if diff_percent > 5:
            return "increasing"
        elif diff_percent < -5:
            return "decreasing"
        else:
            return "stable"
    
    def _detect_anomalies(self, metric_type: MetricType, values: List[float]) -> List[Dict[str, Any]]:
        """Detect anomalies in metric values"""
        anomalies = []
        
        if len(values) < 3:
            return anomalies
        
        # Calculate basic statistics
        mean_val = statistics.mean(values)
        stdev_val = statistics.stdev(values) if len(values) > 1 else 0
        
        # Define thresholds based on metric type
        thresholds = {
            MetricType.CPU_USAGE: {"warning": 80, "critical": 95},
            MetricType.MEMORY_USAGE: {"warning": 85, "critical": 95},
            MetricType.GPU_USAGE: {"warning": 90, "critical": 98},
            MetricType.CPU_TEMPERATURE: {"warning": 70, "critical": 85},
            MetricType.GPU_TEMPERATURE: {"warning": 80, "critical": 90},
            MetricType.DISK_USAGE: {"warning": 90, "critical": 95},
        }
        
        threshold = thresholds.get(metric_type, {"warning": 80, "critical": 95})
        
        # Check for threshold violations
        latest_value = values[-1]
        if latest_value >= threshold["critical"]:
            anomalies.append({
                "type": "critical_threshold",
                "metric_type": metric_type.value,
                "value": latest_value,
                "threshold": threshold["critical"],
                "severity": "critical"
            })
        elif latest_value >= threshold["warning"]:
            anomalies.append({
                "type": "warning_threshold",
                "metric_type": metric_type.value,
                "value": latest_value,
                "threshold": threshold["warning"],
                "severity": "warning"
            })
        
        # Check for statistical anomalies (values beyond 2 standard deviations)
        if stdev_val > 0:
            for value in values[-3:]:  # Check last 3 values
                if abs(value - mean_val) > 2 * stdev_val:
                    anomalies.append({
                        "type": "statistical_anomaly",
                        "metric_type": metric_type.value,
                        "value": value,
                        "mean": mean_val,
                        "stddev": stdev_val,
                        "severity": "warning"
                    })
        
        return anomalies
    
    def _calculate_health_impact(self, metric_type: MetricType, stats: Dict[str, Any]) -> float:
        """Calculate health score impact based on metric"""
        latest_value = stats["latest"]
        
        # Define impact factors for different metrics
        impact_factors = {
            MetricType.CPU_USAGE: {
                "ranges": [(0, 50, 0), (50, 80, 5), (80, 95, 15), (95, 100, 25)],
                "weight": 1.0
            },
            MetricType.MEMORY_USAGE: {
                "ranges": [(0, 60, 0), (60, 85, 5), (85, 95, 15), (95, 100, 25)],
                "weight": 1.0
            },
            MetricType.CPU_TEMPERATURE: {
                "ranges": [(0, 60, 0), (60, 75, 5), (75, 85, 15), (85, 100, 30)],
                "weight": 1.5
            },
            MetricType.GPU_TEMPERATURE: {
                "ranges": [(0, 70, 0), (70, 85, 5), (85, 95, 15), (95, 120, 25)],
                "weight": 1.2
            },
            MetricType.DISK_USAGE: {
                "ranges": [(0, 80, 0), (80, 90, 3), (90, 95, 10), (95, 100, 20)],
                "weight": 0.8
            }
        }
        
        if metric_type not in impact_factors:
            return 0
        
        factor = impact_factors[metric_type]
        impact = 0
        
        for min_val, max_val, penalty in factor["ranges"]:
            if min_val <= latest_value < max_val:
                impact = penalty * factor["weight"]
                break
        
        return impact
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        metrics = analysis["metrics_summary"]
        anomalies = analysis["anomalies"]
        
        # CPU recommendations
        if "cpu_usage" in metrics:
            cpu_stats = metrics["cpu_usage"]
            if cpu_stats["latest"] > 90:
                recommendations.append("CPU usage is critically high. Consider scaling resources or optimizing workloads.")
            elif cpu_stats["latest"] > 80:
                recommendations.append("CPU usage is elevated. Monitor for sustained high usage.")
            
            if cpu_stats.get("trend") == "increasing":
                recommendations.append("CPU usage is trending upward. Plan for capacity expansion.")
        
        # Memory recommendations
        if "memory_usage" in metrics:
            mem_stats = metrics["memory_usage"]
            if mem_stats["latest"] > 90:
                recommendations.append("Memory usage is critically high. Consider adding more RAM or optimizing memory usage.")
            elif mem_stats["latest"] > 80:
                recommendations.append("Memory usage is elevated. Monitor for memory leaks.")
        
        # Temperature recommendations
        if "cpu_temperature" in metrics:
            temp_stats = metrics["cpu_temperature"]
            if temp_stats["latest"] > 80:
                recommendations.append("CPU temperature is high. Check cooling system and airflow.")
            elif temp_stats["latest"] > 70:
                recommendations.append("CPU temperature is elevated. Monitor cooling performance.")
        
        # Disk recommendations
        if "disk_usage" in metrics:
            disk_stats = metrics["disk_usage"]
            if disk_stats["latest"] > 90:
                recommendations.append("Disk usage is critically high. Clean up files or expand storage.")
            elif disk_stats["latest"] > 80:
                recommendations.append("Disk usage is elevated. Plan for storage expansion.")
        
        # General anomaly recommendations
        critical_anomalies = [a for a in anomalies if a.get("severity") == "critical"]
        if critical_anomalies:
            recommendations.append("Critical anomalies detected. Immediate attention required.")
        
        return recommendations
    
    async def _cleanup_old_metrics(self):
        """Clean up old metrics based on retention policy"""
        db = SessionLocal()
        try:
            # Get retention settings
            cutoff_date = datetime.utcnow() - timedelta(days=settings.METRICS_RETENTION_DAYS)
            
            # Delete old metrics
            deleted_count = db.query(MetricModel).filter(
                MetricModel.timestamp < cutoff_date
            ).delete()
            
            if deleted_count > 0:
                db.commit()
                logger.info(f"Cleaned up {deleted_count} old metrics")
            
        except Exception as e:
            logger.error(f"Error cleaning up old metrics: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def _update_machine_health_scores(self):
        """Update health scores for all machines"""
        db = SessionLocal()
        try:
            machines = db.query(MachineModel).all()
            
            for machine in machines:
                machine_id = str(machine.id)
                if machine_id in self.aggregated_data:
                    analysis = self.aggregated_data[machine_id]
                    health_score = max(0, min(100, analysis["health_score"]))
                    
                    # Update machine's hardware_info with health data
                    if not machine.hardware_info:
                        machine.hardware_info = {}
                    
                    machine.hardware_info.update({
                        "health_score": health_score,
                        "last_analysis": analysis["timestamp"],
                        "anomaly_count": len(analysis["anomalies"]),
                        "recommendations_count": len(analysis["recommendations"])
                    })
                    
                    machine.updated_at = datetime.utcnow()
            
            db.commit()
            logger.debug("Updated machine health scores")
            
        except Exception as e:
            logger.error(f"Error updating machine health scores: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def _export_analysis(self, analysis: Dict[str, Any]):
        """Export analysis to external systems"""
        db = SessionLocal()
        try:
            config = db.query(ConfigModel).first()
            if not config:
                return
            
            # Export to InfluxDB if configured
            influxdb_config = config.influxdb_config
            if influxdb_config.get("enabled", False):
                await self._export_to_influxdb(analysis, influxdb_config)
            
            # Export to MQTT if configured
            mqtt_config = config.mqtt_config
            if mqtt_config.get("enabled", False):
                await self._export_to_mqtt(analysis, mqtt_config)
            
        except Exception as e:
            logger.error(f"Error exporting analysis: {e}")
        finally:
            db.close()
    
    async def _export_to_influxdb(self, analysis: Dict[str, Any], config: Dict[str, Any]):
        """Export analysis to InfluxDB"""
        try:
            import influxdb_client
            from influxdb_client.client.write_api import SYNCHRONOUS
            
            client = influxdb_client.InfluxDBClient(
                url=config.get("url"),
                token=config.get("token"),
                org=config.get("org")
            )
            
            write_api = client.write_api(write_options=SYNCHRONOUS)
            
            # Create data points
            points = []
            machine_id = analysis["machine_id"]
            
            # Health score point
            points.append(
                influxdb_client.Point("machine_health")
                .tag("machine_id", machine_id)
                .field("health_score", analysis["health_score"])
                .field("anomaly_count", len(analysis["anomalies"]))
                .time(datetime.utcnow())
            )
            
            # Metrics summary points
            for metric_type, stats in analysis["metrics_summary"].items():
                points.append(
                    influxdb_client.Point("metrics_analysis")
                    .tag("machine_id", machine_id)
                    .tag("metric_type", metric_type)
                    .field("avg", stats["avg"])
                    .field("min", stats["min"])
                    .field("max", stats["max"])
                    .field("latest", stats["latest"])
                    .time(datetime.utcnow())
                )
            
            write_api.write(bucket=config.get("bucket"), record=points)
            client.close()
            
            logger.debug(f"Exported analysis to InfluxDB for machine {machine_id}")
            
        except Exception as e:
            logger.error(f"Error exporting to InfluxDB: {e}")
    
    async def _export_to_mqtt(self, analysis: Dict[str, Any], config: Dict[str, Any]):
        """Export analysis to MQTT"""
        try:
            import paho.mqtt.client as mqtt
            
            client = mqtt.Client()
            
            if config.get("username") and config.get("password"):
                client.username_pw_set(config.get("username"), config.get("password"))
            
            client.connect(config.get("broker"), config.get("port", 1883), config.get("keepalive", 60))
            
            # Publish analysis data
            topic_prefix = config.get("topic_prefix", "master_dashboard")
            machine_id = analysis["machine_id"]
            
            # Publish health score
            client.publish(
                f"{topic_prefix}/machines/{machine_id}/health_score",
                json.dumps({"health_score": analysis["health_score"], "timestamp": analysis["timestamp"]}),
                qos=config.get("qos", 1)
            )
            
            # Publish anomalies
            if analysis["anomalies"]:
                client.publish(
                    f"{topic_prefix}/machines/{machine_id}/anomalies",
                    json.dumps(analysis["anomalies"]),
                    qos=config.get("qos", 1)
                )
            
            client.disconnect()
            
            logger.debug(f"Exported analysis to MQTT for machine {machine_id}")
            
        except Exception as e:
            logger.error(f"Error exporting to MQTT: {e}")
    
    def get_machine_analysis(self, machine_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis data for a specific machine"""
        return self.aggregated_data.get(machine_id)
    
    def get_all_analyses(self) -> Dict[str, Dict[str, Any]]:
        """Get all machine analyses"""
        return self.aggregated_data.copy()
    
    def get_processor_stats(self) -> Dict[str, Any]:
        """Get processor statistics"""
        return {
            "is_running": self.is_running,
            "machines_analyzed": len(self.aggregated_data),
            "queue_size": self.processing_queue.qsize(),
            "last_analysis": max([
                analysis.get("timestamp") for analysis in self.aggregated_data.values()
            ], default=None)
        }