def validate_config_input(server_type, sip_port, rtp_start, rtp_end, max_attempts, ban_time):
    """
    Validate configuration inputs
    """
    errors = []
    
    # Server type validation
    valid_servers = ["asterisk", "freeswitch", "opensips"]
    if server_type not in valid_servers:
        errors.append(f"Server type must be one of: {', '.join(valid_servers)}")
    
    # Port validation
    if not (1 <= sip_port <= 65535):
        errors.append("SIP port must be between 1 and 65535")
    
    if not (1024 <= rtp_start <= 65535):
        errors.append("RTP start port must be between 1024 and 65535")
    
    if not (1024 <= rtp_end <= 65535):
        errors.append("RTP end port must be between 1024 and 65535")
    
    if rtp_start >= rtp_end:
        errors.append("RTP start port must be less than RTP end port")
    
    # Security settings validation
    if not (1 <= max_attempts <= 10):
        errors.append("Max attempts must be between 1 and 10")
    
    if not (60 <= ban_time <= 86400):  # 1 minute to 24 hours
        errors.append("Ban time must be between 60 and 86400 seconds")
    
    if errors:
        return {
            "valid": False,
            "message": "; ".join(errors)
        }
    
    return {"valid": True, "message": "Validation successful"}
