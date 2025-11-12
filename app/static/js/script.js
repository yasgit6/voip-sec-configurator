// VoIP Security Configurator - Frontend JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('configForm');
    const submitBtn = form.querySelector('button[type="submit"]');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Show loading state
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating Configurations...';
        submitBtn.disabled = true;
        
        try {
            const formData = new FormData(form);
            
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            // Create download link for the ZIP file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `voip_security_configs_${new Date().toISOString().slice(0,10)}.zip`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            
            // Show success message
            showAlert('Configuration generated successfully! Check your downloads.', 'success');
            
        } catch (error) {
            console.error('Error:', error);
            showAlert('Error generating configurations. Please try again.', 'danger');
        } finally {
            // Reset button state
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    });
    
    // Real-time validation
    const inputs = form.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('change', validateForm);
    });
    
    function validateForm() {
        const sipPort = parseInt(form.sip_port.value);
        const rtpStart = parseInt(form.rtp_start.value);
        const rtpEnd = parseInt(form.rtp_end.value);
        
        let isValid = true;
        
        // Validate RTP range
        if (rtpStart >= rtpEnd) {
            showFieldError(form.rtp_start, 'RTP start must be less than RTP end');
            isValid = false;
        } else {
            clearFieldError(form.rtp_start);
        }
        
        // Validate ports
        if (sipPort < 1 || sipPort > 65535) {
            showFieldError(form.sip_port, 'SIP port must be between 1 and 65535');
            isValid = false;
        } else {
            clearFieldError(form.sip_port);
        }
        
        submitBtn.disabled = !isValid;
        return isValid;
    }
    
    function showFieldError(field, message) {
        clearFieldError(field);
        field.classList.add('is-invalid');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }
    
    function clearFieldError(field) {
        field.classList.remove('is-invalid');
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    }
    
    function showAlert(message, type) {
        // Remove existing
