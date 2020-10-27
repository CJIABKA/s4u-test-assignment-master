from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from transfer.models import ScheduledPayment

class Command(BaseCommand):
    help = 'Periodic payment task'
    #Add this task in cron
    def handle(self, *args, **options):
        current_day = datetime.now().day
        for payment in ScheduledPayment.objects.filter(pay_day=current_day):
            payment.do_transfer()
        self.stdout.write('Task Done')
