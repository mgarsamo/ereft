"""
Custom SMTP email backend for Python 3.13 compatibility
Fixes the issue where starttls() doesn't accept keyfile/certfile arguments
"""

from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend
import ssl
import sys


class CompatibleSMTPEmailBackend(SMTPEmailBackend):
    """
    Custom SMTP email backend that works with Python 3.13
    Fixes the starttls() keyfile/certfile issue
    """
    
    def open(self):
        """
        Open an SMTP connection with Python 3.13 compatibility
        """
        if self.connection:
            return False
        
        try:
            # Create SMTP connection
            self.connection = self.connection_class(
                self.host, self.port, timeout=self.timeout
            )
            
            # Use TLS if configured
            if self.use_tls:
                # Python 3.13's starttls() doesn't accept keyfile/certfile
                # Always use SSL context for compatibility across Python versions
                context = ssl.create_default_context()
                
                # Load cert/key if provided
                if self.ssl_certfile and self.ssl_keyfile:
                    try:
                        context.load_cert_chain(
                            self.ssl_certfile,
                            self.ssl_keyfile
                        )
                    except Exception as cert_error:
                        # If cert loading fails, continue with default context
                        print(f"⚠️ Could not load SSL cert/key: {cert_error}")
                
                # Call starttls with context (works for all Python versions)
                # Python 3.13 requires context, older versions accept it too
                self.connection.starttls(context=context)
            
            # Authenticate if credentials are provided
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            
            return True
        except Exception:
            if not self.fail_silently:
                raise
            return False

