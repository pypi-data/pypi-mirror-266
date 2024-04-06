from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from rawquery import RawQuery

from saleboxdjango.models import Analytic, CallbackStore, CheckoutStore, Event, SyncLog


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Cleaning old analytics")
        self.clean_analytics()

        print("Cleaning abandoned shopping baskets")
        self.clean_basket()

        print("Cleaning old sync logs")
        self.clean_synclogs()

        print("Cleaning callback store")
        self.clean_callbackstore()

        print("Cleaning checkout store")
        self.clean_checkoutstore()

        print("Cleaning old events")
        self.clean_events()

    # remove all analytics older than 7 days
    def clean_analytics(self):
        cutoff = now() - timedelta(days=7)
        Analytic.objects.filter(last_seen__lt=cutoff).delete()

    def clean_basket(self):
        rq = RawQuery()
        MAX_SESSIONS = 5000

        while True:
            oldest_sessions = rq.multiple_values(
                f"""
                SELECT      session
                FROM        saleboxdjango_basketwishlist
                WHERE       user_id IS NULL
                GROUP BY    session
                ORDER BY    MIN(last_update)
                LIMIT       {MAX_SESSIONS}
                """
            )

            active_sessions = rq.multiple_values(
                f"""
                SELECT      session_key
                FROM        django_session
                WHERE       session_key IN ({self._make_sql_list(oldest_sessions)})
                """
            )

            sessions_to_delete = [
                s for s in oldest_sessions if s not in active_sessions
            ]

            if len(sessions_to_delete) > 0:
                rq.run(
                    f"""
                    DELETE FROM     saleboxdjango_basketwishlist
                    WHERE           user_id IS NULL
                    AND             session IN ({self._make_sql_list(sessions_to_delete)})
                    """
                )
            else:
                break

    def clean_callbackstore(self):
        cutoff = now() - timedelta(days=90)
        CallbackStore.objects.filter(created__lt=cutoff).delete()

    def clean_checkoutstore(self):
        cutoff = now() - timedelta(days=90)
        CheckoutStore.objects.filter(last_updated__lt=cutoff).delete()

    def clean_events(self):
        cutoff = now() - timedelta(days=7)
        Event.objects.filter(created__lt=cutoff).filter(processed_flag=True).delete()

    def clean_synclogs(self):
        cutoff = now() - timedelta(days=7)
        SyncLog.objects.filter(created__lt=cutoff).delete()

    def _make_sql_list(self, id_list):
        return ",".join(["'" + s + "'" for s in id_list])
