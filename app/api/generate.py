import json
from datetime import datetime

def generate_iptables_rules(sip_port, rtp_start, rtp_end, enable_ssh, enable_ipv6):
    """Generate iptables firewall rules"""
    
    rules = [
        "#!/bin/bash",
        "# VoIP Security Firewall Rules",
        "# Generated automatically - Test before production use!",
        "#",
        "# WARNING: Applying these rules may disconnect you from the server",
        "# Recommended to apply via console or with caution",
        "",
        "# Flush existing rules (UNCOMMENT WITH CAUTION)",
        "# iptables -F",
        "# iptables -X",
        "",
        "# Set default policies",
        "iptables -P INPUT DROP",
        "iptables -P FORWARD DROP",
        "iptables -P OUTPUT ACCEPT",
        "",
        "# Allow loopback interface",
        "iptables -A INPUT -i lo -j ACCEPT",
        "iptables -A OUTPUT -o lo -j ACCEPT",
        "",
        "# Allow established connections",
        "iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT",
        "",
        "# Allow SSH (if enabled)",
    ]
    
    if enable_ssh:
        rules.extend([
            "iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT",
            ""
        ])
    
    rules.extend([
        "# VoIP SIP Rules",
        f"iptables -A INPUT -p udp --dport {sip_port} -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT",
        f"iptables -A INPUT -p tcp --dport {sip_port} -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT",
        "",
        "# VoIP RTP/Media Rules",
        f"iptables -A INPUT -p udp --dport {rtp_start}:{rtp_end} -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT",
        "",
        "# ICMP (Ping)",
        "iptables -A INPUT -p icmp --icmp-type echo-request -j ACCEPT",
        "",
        "# Save rules (adjust path for your system)",
        "# iptables-save > /etc/iptables/rules.v4",
        "",
        "# IPv6 Rules (if enabled)",
    ])
    
    if enable_ipv6:
        rules.extend([
            "ip6tables -P INPUT DROP",
            "ip6tables -P FORWARD DROP",
            "ip6tables -P OUTPUT ACCEPT",
            "ip6tables -A INPUT -i lo -j ACCEPT",
            "ip6tables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT",
            f"ip6tables -A INPUT -p udp --dport {sip_port} -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT",
            f"ip6tables -A INPUT -p tcp --dport {sip_port} -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT",
            f"ip6tables -A INPUT -p udp --dport {rtp_start}:{rtp_end} -j ACCEPT",
            "# ip6tables-save > /etc/iptables/rules.v6",
        ])
    
    return "\n".join(rules)

def generate_nftables_rules(sip_port, rtp_start, rtp_end, enable_ssh, enable_ipv6):
    """Generate nftables firewall rules"""
    
    rules = f"""#!/usr/sbin/nft -f

# VoIP Security NFTables Rules
# Generated automatically - Test before production use!

flush ruleset

table inet voip_filter {{
    chain input {{
        type filter hook input priority 0; policy drop;
        
        # Loopback interface
        iifname "lo" accept
        
        # Established connections
        ct state established,related accept
        
        # SSH (if enabled)
        {"tcp dport 22 ct state new,established accept" if enable_ssh else ""}
        
        # VoIP SIP
        udp dport {sip_port} ct state new,established accept
        tcp dport {sip_port} ct state new,established accept
        
        # VoIP RTP
        udp dport {rtp_start}-{rtp_end} ct state new,established accept
        
        # ICMP
        ip protocol icmp icmp type echo-request accept
    }}
    
    chain forward {{
        type filter hook forward priority 0; policy drop;
    }}
    
    chain output {{
        type filter hook output priority 0; policy accept;
    }}
}}
"""
    return rules

def generate_fail2ban_config(server_type, sip_port, max_attempts, ban_time):
    """Generate fail2ban configuration"""
    
    if server_type == "asterisk":
        filter_conf = f"""[Definition]
# Asterisk SIP Security Filter
failregex = ^.*NOTICE.* .*: Registration from '.*' failed for '.*' - Wrong password$
            ^.*NOTICE.* .*: Registration from '.*' failed for '.*' - No matching peer found$
            ^.*NOTICE.* .*: Registration from '.*' failed for '.*' - Username/auth name mismatch$
            ^.*NOTICE.* .*: Failed to authenticate (user|device) .*$
            ^.*WARNING.* .*: .*: Received (invite|register) from .* failed (MD5|auth) challenge$

ignoreregex =
"""
    elif server_type == "freeswitch":
        filter_conf = f"""[Definition]
# FreeSWITCH SIP Security Filter
failregex = ^.*WARNING.* .*: .*: (Failed|Challenge) (SIP|auth) (auth|request).*$
            ^.*ERROR.* .*: .*: (Failed|Challenge) (SIP|auth) (auth|request).*$
            ^.*ERR.* .*: .*: (Failed|Challenge) (SIP|auth) (auth|request).*$

ignoreregex =
"""
    else:  # opensips
        filter_conf = f"""[Definition]
# OpenSIPS SIP Security Filter
failregex = ^.*: ERROR: : tcp_read_req: read error: Connection reset by peer$
            ^.*: ERROR: : tcp_read_req: read error: .*$
            ^.*: ERROR: : tls_tcp_read_req: read error: .*$

ignoreregex =
"""
    
    jail_conf = f"""[voip-{server_type}-{sip_port}]
enabled = true
filter = voip-{server_type}-{sip_port}
port = {sip_port}
logpath = /var/log/{server_type}/{server_type}.log
maxretry = {max_attempts}
bantime = {ban_time}
findtime = 600
protocol = udp,tcp
action = iptables-allports[name=voip_{server_type}, protocol=all]
         sendmail-whois[name=VoIP_{server_type.capitalize()}, dest=admin@yourdomain.com]
backend = auto
"""
    
    return filter_conf, jail_conf

def generate_application_config(server_type, sip_port, rtp_start, rtp_end):
    """Generate VoIP application-specific configuration"""
    
    if server_type == "asterisk":
        config = f"""; Asterisk Security Configuration
; Generated automatically - Apply to sip.conf or pjsip.conf

[security]
; SIP Security Settings
allowguest=no
alwaysauthreject=yes
sipdeny=0.0.0.0/0.0.0.0
sippermit=your_trusted_network/24

; RTP Settings
rtpstart={rtp_start}
rtpend={rtp_end}

; Rate Limiting
limitonpeers=yes
maxcallnumbers=100
"""
    
    elif server_type == "freeswitch":
        config = f"""; FreeSWITCH Security Configuration
; Generated automatically - Apply to sofia.conf

<configuration name="sofia.conf" description="Client Profile">
  <profiles>
    <profile name="secure-profile">
      <settings>
        <!-- SIP Security -->
        <param name="apply-inbound-acl" value="your_trusted_network"/>
        <param name="log-auth-failures" value="true"/>
        
        <!-- RTP Settings -->
        <param name="rtp-start-port" value="{rtp_start}"/>
        <param name="rtp-end-port" value="{rtp_end}"/>
        
        <!-- Anti-flood protection -->
        <param name="max-register-threads" value="4"/>
        <param name="max-register-seconds" value="60"/>
      </settings>
    </profile>
  </profiles>
</configuration>
"""
    
    else:  # opensips
        config = f"""; OpenSIPS Security Configuration
; Generated automatically

# RTP Media Settings
listen=udp:your_server_ip:{sip_port}
rtp_proxy_url="udp:localhost:2223"

mp_rtp_port={rtp_start}
mp_rtp_port={rtp_end}

# Anti-flood Protection
modparam("mi_fifo", "fifo_name", "/tmp/opensips_fifo")
"""
    
    return config

def generate_readme(server_type, sip_port, rtp_start, rtp_end, max_attempts, ban_time):
    """Generate comprehensive README file"""
    
    readme = f"""# VoIP Security Configuration
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Server Type: {server_type.upper()}
- SIP Port: {sip_port}
- RTP Port Range: {rtp_start}-{rtp_end}
- Max Attempts: {max_attempts}
- Ban Time: {ban_time} seconds

## Files Included:
1. `iptables_rules.sh` - IPv4 firewall rules
2. `nftables_rules.conf` - Modern firewall rules
3. `fail2ban_filter.conf` - Fail2ban filter
4. `fail2ban_jail.conf` - Fail2ban jail configuration
5. `{server_type}_security.conf` - Application security config

## Installation Steps:

### 1. FIREWALL RULES (Choose one method)

#### Method A: iptables (Legacy)
```bash
chmod +x iptables_rules.sh
# Review the script first!
nano iptables_rules.sh
# Apply rules:
./iptables_rules.sh
# Apply nftables rules (Recommended):
nft -f nftables_rules.conf
