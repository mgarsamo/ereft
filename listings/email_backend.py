"""
Custom SMTP email backend for Python 3.13 compatibility
Fixes the issue where starttls() doesn't accept keyfile/certfile arguments
"""

from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend
import ssl


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
                # We need to call it without those arguments
                if hasattr(self.connection, 'starttls'):
                    # Create SSL context if we have cert/key files
                    context = None
                    if self.ssl_certfile or self.ssl_keyfile:
                        context = ssl.create_default_context()
                        if self.ssl_certfile:
                            context.load_cert_chain(
                                self.ssl_certfile, 
                                self.ssl_keyfile
                            )
                    
                    # Call starttls without keyfile/certfile for Python 3.13+
                    try:
                        if context:
                            self.connection.starttls(context=context)
                        else:
                            self.connection.starttls()
                    except TypeError:
                        # Fallback for older Python versions
                        if self.ssl_keyfile or self.ssl_certfile:
                            self.connection.starttls(
                                keyfile=self.ssl_keyfile,
                                certfile=self.ssl_certfile
                            )
                        else:
                            self.connection.starttls()
            
            # Authenticate if credentials are provided
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            
            return True
        except Exception:
            if not self.fail_silently:
                raise
            return False

