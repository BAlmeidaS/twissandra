from cassandra.cluster import Cluster
from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        cluster = Cluster(['127.0.0.1'])
        session = cluster.connect()


        session.execute("DROP KEYSPACE twissandra")

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

        session.execute("""
            CREATE TYPE Verb (
                id text,
                display map<text, text>
            )
            """)

        session.execute("""
            CREATE TYPE Definition (
                name map<text, text>,
                description map<text, text>
            )
            """)  
        
        session.execute("""
            CREATE TYPE Object (
                definition frozen<Definition>,
                id text,
                objectType text
            )
            """)  
        session.execute("""
            CREATE TYPE Actor (
                mbox text,
                name text,
                objectType text
            )
            """)      
        session.execute("""
            CREATE TYPE Authority (
                mbox text,
                name text,
                objectType text
            )
            """)      
        

        session.execute("""
            CREATE TABLE statements2 (
                idlrs int PRIMARY KEY,
                verb frozen<Verb>,
                version text,
                timestamp text,
                object frozen<Object>,
                actor frozen<Actor>,
                stored text,
                authority frozen<Authority>,
                id text
            )
            """)
            


        print 'All done!'
