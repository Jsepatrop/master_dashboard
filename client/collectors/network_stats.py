"""
Network statistics collector for Master Dashboard Agent
Collects comprehensive network interface statistics and connection information
"""
import asyncio
import psutil
import socket
import time
import logging
from typing import Dict, Any, List
import netifaces
import platform

class NetworkStatsCollector:
    """Collects network statistics and interface information"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.system = platform.system().lower()
        self._previous_stats = {}
        self._last_collection_time = 0
        
    async def collect(self) -> Dict[str, Any]:
        """Collect all network statistics"""
        try:
            current_time = time.time()
            stats = {
                'timestamp': current_time,
                'interfaces': await self._collect_interface_stats(),
                'connections': await self._collect_connections(),
                'routing': await self._collect_routing_info(),
                'dns': await self._collect_dns_info()
            }
            
            # Calculate rates if we have previous data
            if self._previous_stats and self._last_collection_time:
                time_delta = current_time - self._last_collection_time
                stats['rates'] = self._calculate_rates(stats, time_delta)
            
            self._previous_stats = stats.copy()
            self._last_collection_time = current_time
            
            return stats
        except Exception as e:
            self.logger.error(f"Error collecting network stats: {e}")
            return {'error': str(e)}
    
    async def _collect_interface_stats(self) -> Dict[str, Any]:
        """Collect network interface statistics"""
        interfaces = {}
        
        try:
            # Get interface statistics from psutil
            net_io = psutil.net_io_counters(pernic=True)
            
            # Get interface addresses
            net_addrs = psutil.net_if_addrs()
            
            # Get interface status
            net_stats = psutil.net_if_stats()
            
            for interface, io_stats in net_io.items():
                interface_info = {
                    'io_stats': {
                        'bytes_sent': io_stats.bytes_sent,
                        'bytes_recv': io_stats.bytes_recv,
                        'packets_sent': io_stats.packets_sent,
                        'packets_recv': io_stats.packets_recv,
                        'errin': io_stats.errin,
                        'errout': io_stats.errout,
                        'dropin': io_stats.dropin,
                        'dropout': io_stats.dropout
                    }
                }
                
                # Add address information
                if interface in net_addrs:
                    addresses = []
                    for addr in net_addrs[interface]:
                        addr_info = {
                            'family': str(addr.family),
                            'address': addr.address
                        }
                        if addr.netmask:
                            addr_info['netmask'] = addr.netmask
                        if addr.broadcast:
                            addr_info['broadcast'] = addr.broadcast
                        addresses.append(addr_info)
                    interface_info['addresses'] = addresses
                
                # Add interface status
                if interface in net_stats:
                    stats = net_stats[interface]
                    interface_info['status'] = {
                        'isup': stats.isup,
                        'duplex': str(stats.duplex),
                        'speed': stats.speed,  # Mbps
                        'mtu': stats.mtu
                    }
                
                # Add additional interface details using netifaces
                try:
                    if interface in netifaces.interfaces():
                        gws = netifaces.gateways()
                        if 'default' in gws and netifaces.AF_INET in gws['default']:
                            default_gw = gws['default'][netifaces.AF_INET]
                            if default_gw[1] == interface:
                                interface_info['is_default'] = True
                except Exception:
                    pass
                
                interfaces[interface] = interface_info
                
        except Exception as e:
            self.logger.debug(f"Error collecting interface stats: {e}")
        
        return interfaces
    
    async def _collect_connections(self) -> Dict[str, Any]:
        """Collect network connections"""
        connections = {
            'tcp': [],
            'udp': [],
            'tcp6': [],
            'udp6': [],
            'stats': {
                'total': 0,
                'established': 0,
                'listening': 0
            }
        }
        
        try:
            # Get all network connections
            for kind in ['tcp', 'udp', 'tcp6', 'udp6']:
                try:
                    conns = psutil.net_connections(kind=kind)
                    for conn in conns:
                        conn_info = {
                            'fd': conn.fd,
                            'family': str(conn.family),
                            'type': str(conn.type),
                            'local': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                            'remote': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                            'status': conn.status,
                            'pid': conn.pid
                        }
                        
                        # Get process name if available
                        if conn.pid:
                            try:
                                process = psutil.Process(conn.pid)
                                conn_info['process_name'] = process.name()
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                        
                        connections[kind].append(conn_info)
                        connections['stats']['total'] += 1
                        
                        if conn.status == 'ESTABLISHED':
                            connections['stats']['established'] += 1
                        elif conn.status == 'LISTEN':
                            connections['stats']['listening'] += 1
                            
                except Exception as e:
                    self.logger.debug(f"Error collecting {kind} connections: {e}")
                    
        except Exception as e:
            self.logger.debug(f"Error collecting connections: {e}")
        
        return connections
    
    async def _collect_routing_info(self) -> Dict[str, Any]:
        """Collect routing table information"""
        routing = {
            'default_gateway': None,
            'routes': []
        }
        
        try:
            gateways = netifaces.gateways()
            
            # Get default gateway
            if 'default' in gateways:
                default = gateways['default']
                if netifaces.AF_INET in default:
                    gateway_info = default[netifaces.AF_INET]
                    routing['default_gateway'] = {
                        'gateway': gateway_info[0],
                        'interface': gateway_info[1]
                    }
            
            # Get all gateways
            for family, gw_list in gateways.items():
                if family != 'default' and isinstance(gw_list, list):
                    for gw_info in gw_list:
                        if len(gw_info) >= 2:
                            routing['routes'].append({
                                'family': str(family),
                                'gateway': gw_info[0],
                                'interface': gw_info[1]
                            })
                            
        except Exception as e:
            self.logger.debug(f"Error collecting routing info: {e}")
        
        return routing
    
    async def _collect_dns_info(self) -> Dict[str, Any]:
        """Collect DNS configuration"""
        dns_info = {
            'nameservers': [],
            'search_domains': []
        }
        
        try:
            if self.system == 'linux':
                # Read /etc/resolv.conf
                try:
                    with open('/etc/resolv.conf', 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith('nameserver'):
                                ns = line.split()[1]
                                dns_info['nameservers'].append(ns)
                            elif line.startswith('search'):
                                domains = line.split()[1:]
                                dns_info['search_domains'].extend(domains)
                except Exception:
                    pass
            
            elif self.system == 'windows':
                # Use subprocess to get DNS servers
                try:
                    import subprocess
                    result = subprocess.run([
                        'netsh', 'interface', 'ip', 'show', 'dns'
                    ], capture_output=True, text=True)
                    
                    for line in result.stdout.split('\n'):
                        if 'DNS servers configured' in line:
                            # Parse DNS servers from netsh output
                            pass
                except Exception:
                    pass
            
            elif self.system == 'darwin':
                # Use scutil on macOS
                try:
                    import subprocess
                    result = subprocess.run([
                        'scutil', '--dns'
                    ], capture_output=True, text=True)
                    
                    # Parse DNS configuration
                    for line in result.stdout.split('\n'):
                        if 'nameserver' in line:
                            parts = line.split()
                            if len(parts) >= 3:
                                dns_info['nameservers'].append(parts[2])
                except Exception:
                    pass
                    
        except Exception as e:
            self.logger.debug(f"Error collecting DNS info: {e}")
        
        return dns_info
    
    def _calculate_rates(self, current_stats: Dict, time_delta: float) -> Dict[str, Any]:
        """Calculate data transfer rates"""
        rates = {}
        
        try:
            if 'interfaces' in current_stats and 'interfaces' in self._previous_stats:
                rates['interfaces'] = {}
                
                for interface, current_data in current_stats['interfaces'].items():
                    if interface in self._previous_stats['interfaces']:
                        prev_data = self._previous_stats['interfaces'][interface]
                        
                        if 'io_stats' in current_data and 'io_stats' in prev_data:
                            current_io = current_data['io_stats']
                            prev_io = prev_data['io_stats']
                            
                            bytes_sent_rate = (current_io['bytes_sent'] - prev_io['bytes_sent']) / time_delta
                            bytes_recv_rate = (current_io['bytes_recv'] - prev_io['bytes_recv']) / time_delta
                            
                            rates['interfaces'][interface] = {
                                'bytes_sent_per_sec': max(0, bytes_sent_rate),
                                'bytes_recv_per_sec': max(0, bytes_recv_rate),
                                'packets_sent_per_sec': max(0, (current_io['packets_sent'] - prev_io['packets_sent']) / time_delta),
                                'packets_recv_per_sec': max(0, (current_io['packets_recv'] - prev_io['packets_recv']) / time_delta)
                            }
                            
        except Exception as e:
            self.logger.debug(f"Error calculating network rates: {e}")
        
        return rates