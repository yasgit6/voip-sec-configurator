def generate_fail2ban(port, max_attempts):
    filter_conf = f"""[Definition]
failregex = .*INVITE.*|.*REGISTER.*  # مثال عام
"""
    jail_conf = f"""
[asterisk-{port}]
enabled = true
filter = asterisk-{port}
port    = {port}
maxretry = {max_attempts}
bantime = 3600
"""
    return filter_conf, jail_conf

def generate_iptables(port):
    return f"""#!/bin/sh
iptables -A INPUT -p udp --dport {port} -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -p udp --dport {port} -j DROP
"""

def generate_configs(port, max_attempts):
    filter_conf, jail_conf = generate_fail2ban(port, max_attempts)
    iptables_script = generate_iptables(port)
    return {
        f"filters/asterisk-{port}.conf": filter_conf,
        f"jails/asterisk-{port}.conf": jail_conf,
        "iptables/voip_rules.sh": iptables_script
    }
