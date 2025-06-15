# backend/app/services/alert_manager.py
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiohttp
import json

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.alerts import Alert as AlertModel, AlertRule as AlertRuleModel, AlertSeverity, AlertStatus, ComparisonOperator
from app.models.metrics import MetricData as MetricModel, MetricType
from app.models.machine import Machine as MachineModel
from app.models.configuration import SystemConfiguration as ConfigModel

logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self):
        self.is_running = False
        self.alert_task = None
        self.active_alerts: Dict[str, AlertModel] = {}
        self.last_evaluations: Dict[str, datetime] = {}
        self.cooldown_periods: Dict[str, datetime] = {}
        
    async def start(self):
        """Start the alert manager"""
        if self.is_running:
            return
            
        self.is_running = True
        logger.info("Starting alert manager...")
        
        # Start alert evaluation loop
        self.alert_task = asyncio.create_task(self._alert_loop())
        
        logger.info("Alert manager started")
    
    async def stop(self):
        """Stop the alert manager"""
        self.is_running = False
        
        if self.alert_task:
            self.alert_task.cancel()
            try:
                await self.alert_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Alert manager stopped")
    
    async def _alert_loop(self):
        """Main alert evaluation loop"""
        while self.is_running:
            try:
                await self._evaluate_alert_rules()
                await asyncio.sleep(settings.ALERT_CHECK_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in alert loop: {e}")
                await asyncio.sleep(5)
    
    async def _evaluate_alert_rules(self):
        """Evaluate all active alert rules"""
        db = SessionLocal()
        try:
            # Get all enabled alert rules
            rules = db.query(AlertRuleModel).filter(AlertRuleModel.enabled == True).all()
            
            for rule in rules:
                try:
                    await self._evaluate_rule(db, rule)
                except Exception as e:
                    logger.error(f"Error evaluating rule {rule.id}: {e}")
            
        except Exception as e:
            logger.error(f"Error in alert evaluation: {e}")
        finally:
            db.close()
    
    async def _evaluate_rule(self, db, rule: AlertRuleModel):
        """Evaluate a single alert rule"""
        rule_key = str(rule.id)
        current_time = datetime.utcnow()
        
        # Check if rule is in cooldown period
        if rule_key in self.cooldown_periods:
            if current_time < self.cooldown_periods[rule_key]:
                return
        
        # Check if enough time has passed since last evaluation
        if rule_key in self.last_evaluations:
            if (current_time - self.last_evaluations[rule_key]).seconds < rule.evaluation_interval:
                return
        
        # Get latest metric for this rule
        latest_metric = db.query(MetricModel).filter(
            MetricModel.machine_id == rule.machine_id,
            MetricModel.metric_type == rule.metric_type
        ).order_by(MetricModel.timestamp.desc()).first()
        
        if not latest_metric:
            return
        
        # Check if metric is recent enough (within 2x collection interval)
        if (current_time - latest_metric.timestamp).seconds > 120:
            return
        
        # Evaluate condition
        condition_met = self._evaluate_condition(
            latest_metric.value,
            rule.threshold_value,
            rule.comparison_operator
        )
        
        self.last_evaluations[rule_key] = current_time
        
        if condition_met:
            # Check if alert already exists for this rule
            existing_alert = db.query(AlertModel).filter(
                AlertModel.rule_id == rule.id,
                AlertModel.status == AlertStatus.ACTIVE
            ).first()
            
            if not existing_alert:
                # Create new alert
                await self._create_alert(db, rule, latest_metric)
                # Set cooldown period
                self.cooldown_periods[rule_key] = current_time + timedelta(seconds=rule.cooldown_period)
        else:
            # Check if there's an active alert to resolve
            active_alert = db.query(AlertModel).filter(
                AlertModel.rule_id == rule.id,
                AlertModel.status == AlertStatus.ACTIVE
            ).first()
            
            if active_alert:
                # Auto-resolve alert
                active_alert.status = AlertStatus.RESOLVED
                active_alert.resolved_at = current_time
                active_alert.resolved_by = "system"
                active_alert.notes = "Auto-resolved: condition no longer met"
                db.commit()
                
                logger.info(f"Auto-resolved alert {active_alert.id}")
    
    def _evaluate_condition(self, current_value: float, threshold: float, operator: ComparisonOperator) -> bool:
        """Evaluate alert condition"""
        if operator == ComparisonOperator.GREATER_THAN:
            return current_value > threshold
        elif operator == ComparisonOperator.LESS_THAN:
            return current_value < threshold
        elif operator == ComparisonOperator.EQUAL:
            return abs(current_value - threshold) < 0.001
        elif operator == ComparisonOperator.GREATER_EQUAL:
            return current_value >= threshold
        elif operator == ComparisonOperator.LESS_EQUAL:
            return current_value <= threshold
        elif operator == ComparisonOperator.NOT_EQUAL:
            return abs(current_value - threshold) >= 0.001
        return False
    
    async def _create_alert(self, db, rule: AlertRuleModel, metric: MetricModel):
        """Create new alert"""
        # Get machine info
        machine = db.query(MachineModel).filter(MachineModel.id == rule.machine_id).first()
        if not machine:
            return
        
        # Create alert message
        title = f"{rule.name} - {machine.name}"
        message = f"Alert triggered for {machine.name}\n"
        message += f"Metric: {rule.metric_type}\n"
        message += f"Current value: {metric.value} {metric.unit or ''}\n"
        message += f"Threshold: {rule.threshold_value}\n"
        message += f"Condition: {rule.comparison_operator.value}\n"
        message += f"Component: {metric.component_name or 'N/A'}\n"
        message += f"Time: {metric.timestamp.isoformat()}"
        
        # Create alert record
        alert = AlertModel(
            rule_id=rule.id,
            machine_id=rule.machine_id,
            component_id=rule.component_id,
            title=title,
            message=message,
            severity=rule.severity,
            metric_type=rule.metric_type,
            current_value=metric.value,
            threshold_value=rule.threshold_value,
            metadata={
                "component_name": metric.component_name,
                "unit": metric.unit,
                "evaluation_time": datetime.utcnow().isoformat()
            }
        )
        
        db.add(alert)
        db.commit()
        db.refresh(alert)
        
        logger.info(f"Created alert: {title} (Severity: {rule.severity})")
        
        # Send notifications
        await self._send_notifications(alert, rule, machine)
    
    async def _send_notifications(self, alert: AlertModel, rule: AlertRuleModel, machine: MachineModel):
        """Send alert notifications"""
        # Get system configuration
        db = SessionLocal()
        try:
            config = db.query(ConfigModel).first()
            if not config:
                return
            
            alert_config = config.alert_config
            
            # Send notifications based on configured channels
            for channel in rule.notification_channels:
                try:
                    if channel == "email" and alert_config.get("email_enabled", False):
                        await self._send_email_notification(alert, alert_config)
                    elif channel == "slack" and alert_config.get("slack_enabled", False):
                        await self._send_slack_notification(alert, alert_config)
                    elif channel == "webhook" and alert_config.get("webhook_enabled", False):
                        await self._send_webhook_notification(alert, alert_config)
                except Exception as e:
                    logger.error(f"Error sending {channel} notification: {e}")
        
        finally:
            db.close()
    
    async def _send_email_notification(self, alert: AlertModel, config: Dict[str, Any]):
        """Send email notification"""
        try:
            smtp_host = config.get("smtp_host")
            smtp_port = config.get("smtp_port", 587)
            smtp_username = config.get("smtp_username")
            smtp_password = config.get("smtp_password")
            smtp_tls = config.get("smtp_tls", True)
            from_email = config.get("from_email")
            to_emails = config.get("to_emails", [])
            
            if not all([smtp_host, smtp_username, smtp_password, from_email, to_emails]):
                logger.warning("Email configuration incomplete, skipping email notification")
                return
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = ", ".join(to_emails)
            msg['Subject'] = f"[{alert.severity.upper()}] {alert.title}"
            
            # Email body
            body = f"""
Master Dashboard Revolutionary - Alert Notification

Alert Details:
- Title: {alert.title}
- Severity: {alert.severity.upper()}
- Machine: {alert.machine_id}
- Metric: {alert.metric_type}
- Current Value: {alert.current_value}
- Threshold: {alert.threshold_value}
- Triggered At: {alert.triggered_at}

Message:
{alert.message}

Please check the Master Dashboard for more details.
            """.strip()
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(smtp_host, smtp_port)
            if smtp_tls:
                context = ssl.create_default_context()
                server.starttls(context=context)
            server.login(smtp_username, smtp_password)
            server.sendmail(from_email, to_emails, msg.as_string())
            server.quit()
            
            logger.info(f"Email notification sent for alert {alert.id}")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    async def _send_slack_notification(self, alert: AlertModel, config: Dict[str, Any]):
        """Send Slack notification"""
        try:
            webhook_url = config.get("slack_webhook")
            if not webhook_url:
                return
            
            # Slack color based on severity
            color_map = {
                "low": "#36a64f",      # green
                "medium": "#ff9500",   # orange
                "high": "#ff4500",     # red-orange
                "critical": "#ff0000"  # red
            }
            
            color = color_map.get(alert.severity.value, "#808080")
            
            payload = {
                "username": "Master Dashboard",
                "icon_emoji": ":warning:",
                "attachments": [
                    {
                        "color": color,
                        "title": alert.title,
                        "text": alert.message,
                        "fields": [
                            {
                                "title": "Severity",
                                "value": alert.severity.upper(),
                                "short": True
                            },
                            {
                                "title": "Current Value",
                                "value": f"{alert.current_value}",
                                "short": True
                            },
                            {
                                "title": "Threshold",
                                "value": f"{alert.threshold_value}",
                                "short": True
                            },
                            {
                                "title": "Time",
                                "value": alert.triggered_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
                                "short": True
                            }
                        ],
                        "footer": "Master Dashboard Revolutionary",
                        "ts": int(alert.triggered_at.timestamp())
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Slack notification sent for alert {alert.id}")
                    else:
                        logger.error(f"Slack notification failed with status {response.status}")
        
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
    
    async def _send_webhook_notification(self, alert: AlertModel, config: Dict[str, Any]):
        """Send webhook notification"""
        try:
            webhook_url = config.get("webhook_url")
            webhook_headers = config.get("webhook_headers", {})
            
            if not webhook_url:
                return
            
            payload = {
                "alert_id": str(alert.id),
                "title": alert.title,
                "message": alert.message,
                "severity": alert.severity.value,
                "machine_id": str(alert.machine_id),
                "metric_type": alert.metric_type,
                "current_value": alert.current_value,
                "threshold_value": alert.threshold_value,
                "triggered_at": alert.triggered_at.isoformat(),
                "status": alert.status.value,
                "metadata": alert.metadata
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload, headers=webhook_headers) as response:
                    if response.status < 400:
                        logger.info(f"Webhook notification sent for alert {alert.id}")
                    else:
                        logger.error(f"Webhook notification failed with status {response.status}")
        
        except Exception as e:
            logger.error(f"Error sending webhook notification: {e}")
    
    async def create_default_alert_rules(self):
        """Create default alert rules for new machines"""
        db = SessionLocal()
        try:
            machines = db.query(MachineModel).all()
            
            for machine in machines:
                # Check if machine already has alert rules
                existing_rules = db.query(AlertRuleModel).filter(
                    AlertRuleModel.machine_id == machine.id
                ).count()
                
                if existing_rules == 0:
                    # Create default alert rules
                    default_rules = [
                        {
                            "name": f"High CPU Usage - {machine.name}",
                            "description": "CPU usage above threshold",
                            "metric_type": MetricType.CPU_USAGE.value,
                            "threshold_value": machine.cpu_threshold,
                            "comparison_operator": ComparisonOperator.GREATER_THAN,
                            "severity": AlertSeverity.HIGH,
                            "notification_channels": ["email", "slack"]
                        },
                        {
                            "name": f"High Memory Usage - {machine.name}",
                            "description": "Memory usage above threshold",
                            "metric_type": MetricType.MEMORY_USAGE.value,
                            "threshold_value": machine.memory_threshold,
                            "comparison_operator": ComparisonOperator.GREATER_THAN,
                            "severity": AlertSeverity.HIGH,
                            "notification_channels": ["email", "slack"]
                        },
                        {
                            "name": f"High Temperature - {machine.name}",
                            "description": "CPU temperature above threshold",
                            "metric_type": MetricType.CPU_TEMPERATURE.value,
                            "threshold_value": machine.temperature_threshold,
                            "comparison_operator": ComparisonOperator.GREATER_THAN,
                            "severity": AlertSeverity.CRITICAL,
                            "notification_channels": ["email", "slack", "webhook"]
                        },
                        {
                            "name": f"High Disk Usage - {machine.name}",
                            "description": "Disk usage above threshold",
                            "metric_type": MetricType.DISK_USAGE.value,
                            "threshold_value": machine.disk_threshold,
                            "comparison_operator": ComparisonOperator.GREATER_THAN,
                            "severity": AlertSeverity.MEDIUM,
                            "notification_channels": ["email"]
                        }
                    ]
                    
                    for rule_data in default_rules:
                        rule = AlertRuleModel(
                            machine_id=machine.id,
                            **rule_data,
                            created_by="system"
                        )
                        db.add(rule)
                    
                    logger.info(f"Created default alert rules for machine {machine.name}")
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error creating default alert rules: {e}")
            db.rollback()
        finally:
            db.close()
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary statistics"""
        return {
            "active_alerts": len(self.active_alerts),
            "last_evaluation": max(self.last_evaluations.values()) if self.last_evaluations else None,
            "cooldown_rules": len(self.cooldown_periods),
            "is_running": self.is_running
        }