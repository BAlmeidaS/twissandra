from cassandra.cluster import Cluster
from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        cluster = Cluster(['127.0.0.1'])
        session = cluster.connect()


        #session.execute("DROP KEYSPACE twissandra")

        session.execute("""
            CREATE KEYSPACE twissandra
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}
            """)

        # create tables
        session.set_keyspace("twissandra")

        session.execute("""
            CREATE TABLE querries (
                type text PRIMARY KEY, 
                qtd int 
            )
            """)

        session.execute("""
            CREATE TABLE statements (
                id int PRIMARY KEY,
                json text
            )
            """)


        print 'All done!'
