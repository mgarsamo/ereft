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
                # Python 3.13's starttls() doesn't accept keyfile/certfile directly
                # We need to use SSL context instead
                try:
                    # Check Python version - Python 3.13+ requires context
                    if sys.version_info >= (3, 13):
                        # For Python 3.13+, always use SSL context
                        context = ssl.create_default_context()
                        if self.ssl_certfile and self.ssl_keyfile:
                            context.load_cert_chain(
                                self.ssl_certfile,
                                self.ssl_keyfile
                            )
                        self.connection.starttls(context=context)
                    else:
                        # For older Python versions, try with keyfile/certfile
                        if self.ssl_keyfile or self.ssl_certfile:
                            self.connection.starttls(
                                keyfile=self.ssl_keyfile,
                                certfile=self.ssl_certfile
                            )
                        else:
                            self.connection.starttls()
                except (TypeError, AttributeError) as e:
                    # Fallback: try without any arguments
                    try:
                        context = ssl.create_default_context()
                        self.connection.starttls(context=context)
                    except:
                        self.connection.starttls()
            
            # Authenticate if credentials are provided
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            
            return True
        except Exception:
            if not self.fail_silently:
                raise
            return False

