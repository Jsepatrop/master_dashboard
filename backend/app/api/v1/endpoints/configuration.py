# backend/app/api/v1/endpoints/configuration.py
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import asyncio
import smtplib
import ssl
from email.mime.text import MIMEText
import aiohttp
import paho.mqtt.client as mqtt

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.configuration import SystemConfiguration as ConfigModel
from app.schemas.configuration import (
    SystemConfiguration, SystemConfigurationUpdate, 
    ConfigurationTest, ConfigurationTestResult
)

router = APIRouter()

@router.get("/", response_model=SystemConfiguration)
async def get_configuration(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current system configuration"""
    config = db.query(ConfigModel).first()
    if not config:
        # Create default configuration
        config = ConfigModel()
        db.add(config)
        db.commit()
        db.refresh(config)
    
    return config

@router.put("/", response_model=SystemConfiguration)
async def update_configuration(
    config_update: SystemConfigurationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update system configuration"""
    config = db.query(ConfigModel).first()
    if not config:
        config = ConfigModel()
        db.add(config)
    
    # Update configuration fields
    update_data = config_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(config, field):
            setattr(config, field, value)
    
    config.updated_by = current_user.get("sub", "admin")
    
    db.commit()
    db.refresh(config)
    
    return config

@router.post("/test", response_model=ConfigurationTestResult)
async def test_configuration(
    test_config: ConfigurationTest,
    current_user: dict = Depends(get_current_user)
):
    """Test external service configuration"""
    service = test_config.service
    config = test_config.config
    
    try:
        if service == "influxdb":
            return await test_influxdb_connection(config)
        elif service == "mqtt":
            return await test_mqtt_connection(config)
        elif service == "email":
            return await test_email_configuration(config)
        elif service == "slack":
            return await test_slack_webhook(config)
        elif service == "webhook":
            return await test_webhook_url(config)
        else:
            return ConfigurationTestResult(
                service=service,
                success=False,
                message="Unknown service type"
            )
    except Exception as e:
        return ConfigurationTestResult(
            service=service,
            success=False,
            message=f"Test failed: {str(e)}"
        )

async def test_influxdb_connection(config: Dict[str, Any]) -> ConfigurationTestResult:
    """Test InfluxDB connection"""
    try:
        import influxdb_client
        from influxdb_client.client.write_api import SYNCHRONOUS
        
        client = influxdb_client.InfluxDBClient(
            url=config.get("url"),
            token=config.get("token"),
            org=config.get("org")
        )
        
        # Test connection by querying buckets
        buckets_api = client.buckets_api()
        buckets = buckets_api.find_buckets()
        
        client.close()
        
        return ConfigurationTestResult(
            service="influxdb",
            success=True,
            message="Connection successful",
            details={"buckets_count": len(buckets.buckets)}
        )
    except Exception as e:
        return ConfigurationTestResult(
            service="influxdb",
            success=False,
            message=f"Connection failed: {str(e)}"
        )

async def test_mqtt_connection(config: Dict[str, Any]) -> ConfigurationTestResult:
    """Test MQTT broker connection"""
    try:
        def on_connect(client, userdata, flags, rc):
            userdata['connected'] = rc == 0
        
        client = mqtt.Client()
        client.on_connect = on_connect
        
        userdata = {'connected': False}
        client.user_data_set(userdata)
        
        if config.get("username") and config.get("password"):
            client.username_pw_set(config.get("username"), config.get("password"))
        
        client.connect(config.get("broker"), config.get("port", 1883), 60)
        client.loop_start()
        
        # Wait for connection
        await asyncio.sleep(2)
        
        client.loop_stop()
        client.disconnect()
        
        if userdata['connected']:
            return ConfigurationTestResult(
                service="mqtt",
                success=True,
                message="MQTT connection successful"
            )
        else:
            return ConfigurationTestResult(
                service="mqtt",
                success=False,
                message="MQTT connection failed"
            )
    except Exception as e:
        return ConfigurationTestResult(
            service="mqtt",
            success=False,
            message=f"MQTT test failed: {str(e)}"
        )

async def test_email_configuration(config: Dict[str, Any]) -> ConfigurationTestResult:
    """Test email SMTP configuration"""
    try:
        server = smtplib.SMTP(config.get("smtp_host"), config.get("smtp_port", 587))
        
        if config.get("smtp_tls", True):
            context = ssl.create_default_context()
            server.starttls(context=context)
        
        if config.get("smtp_username") and config.get("smtp_password"):
            server.login(config.get("smtp_username"), config.get("smtp_password"))
        
        server.quit()
        
        return ConfigurationTestResult(
            service="email",
            success=True,
            message="Email configuration valid"
        )
    except Exception as e:
        return ConfigurationTestResult(
            service="email",
            success=False,
            message=f"Email test failed: {str(e)}"
        )

async def test_slack_webhook(config: Dict[str, Any]) -> ConfigurationTestResult:
    """Test Slack webhook"""
    try:
        webhook_url = config.get("slack_webhook")
        if not webhook_url:
            return ConfigurationTestResult(
                service="slack",
                success=False,
                message="Slack webhook URL is required"
            )
        
        test_payload = {
            "text": "Master Dashboard Revolutionary - Configuration Test",
            "username": "Master Dashboard",
            "icon_emoji": ":robot_face:"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=test_payload) as response:
                if response.status == 200:
                    return ConfigurationTestResult(
                        service="slack",
                        success=True,
                        message="Slack webhook test successful"
                    )
                else:
                    return ConfigurationTestResult(
                        service="slack",
                        success=False,
                        message=f"Slack webhook returned status {response.status}"
                    )
    except Exception as e:
        return ConfigurationTestResult(
            service="slack",
            success=False,
            message=f"Slack webhook test failed: {str(e)}"
        )

async def test_webhook_url(config: Dict[str, Any]) -> ConfigurationTestResult:
    """Test generic webhook URL"""
    try:
        webhook_url = config.get("webhook_url")
        headers = config.get("webhook_headers", {})
        
        test_payload = {
            "test": True,
            "service": "Master Dashboard Revolutionary",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=test_payload, headers=headers) as response:
                return ConfigurationTestResult(
                    service="webhook",
                    success=response.status < 400,
                    message=f"Webhook returned status {response.status}",
                    details={"status_code": response.status}
                )
    except Exception as e:
        return ConfigurationTestResult(
            service="webhook",
            success=False,
            message=f"Webhook test failed: {str(e)}"
        )

@router.post("/backup")
async def backup_configuration(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create configuration backup"""
    config = db.query(ConfigModel).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found"
        )
    
    from datetime import datetime
    backup_data = {
        "version": config.version,
        "backup_date": datetime.utcnow().isoformat(),
        "influxdb_config": config.influxdb_config,
        "mqtt_config": config.mqtt_config,
        "alert_config": config.alert_config,
        "ui_config": config.ui_config,
        "monitoring_config": config.monitoring_config,
        "security_config": config.security_config
    }
    
    config.last_backup_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": "Configuration backup created",
        "backup_data": backup_data
    }

@router.post("/restore")
async def restore_configuration(
    backup_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Restore configuration from backup"""
    config = db.query(ConfigModel).first()
    if not config:
        config = ConfigModel()
        db.add(config)
    
    # Restore configuration sections
    if "influxdb_config" in backup_data:
        config.influxdb_config = backup_data["influxdb_config"]
    if "mqtt_config" in backup_data:
        config.mqtt_config = backup_data["mqtt_config"]
    if "alert_config" in backup_data:
        config.alert_config = backup_data["alert_config"]
    if "ui_config" in backup_data:
        config.ui_config = backup_data["ui_config"]
    if "monitoring_config" in backup_data:
        config.monitoring_config = backup_data["monitoring_config"]
    if "security_config" in backup_data:
        config.security_config = backup_data["security_config"]
    
    config.updated_by = current_user.get("sub", "admin")
    
    db.commit()
    db.refresh(config)
    
    return {
        "message": "Configuration restored successfully",
        "restored_version": backup_data.get("version", "unknown")
    }