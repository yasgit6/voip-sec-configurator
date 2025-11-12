# VoIP Security Configurator 🔒

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11%2B-green)
![License](https://img.shields.io/badge/license-MIT-orange)

A specialized security tool for generating customized protection settings for VoIP servers (Asterisk/FreeSWITCH) against cyberattacks.

## 🎯 The Problem We Solve

VoIP servers are vulnerable to frequent attacks such as:

- Brute Force Attacks
- Port Scanning
- SIP Flood Attacks
- Penetration Attempts via Unsecured Ports

## ✨ Features

### 🆓 Free Version
- Generates basic **iptables/nftables** rules
- Configures **fail2ban** for primary ports
- Downloadable configuration files
- Detailed application documentation

### 💰 Paid Version (Coming Soon)
- Advanced rules for detecting complex attacks
- Automatic system log analysis
- Advanced IPv6 security settings
- Dedicated technical support

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker (Optional)

### Local Run

```bash
# Clone the repository
`git clone https://github.com/yourusername/voip-sec-configurator.git
`cd voip-sec-configurator
`# Build and run using Docker
`docker build -t voip-sec-config .
`docker run -p 8000:8000 voip-sec-config`
