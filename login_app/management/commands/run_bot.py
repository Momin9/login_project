from django.core.management.base import BaseCommand
from login_app.bot import start_bot

class Command(BaseCommand):
    help = 'Run the Telegram bot'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🤖 Starting Telegram Bot...'))
        start_bot()