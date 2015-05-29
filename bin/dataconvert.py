import getopt
import sys
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import DataError, OperationalError


def make_session(connection_string):
    engine = create_engine(connection_string, echo=False, convert_unicode=True)
    Session = sessionmaker(bind=engine, autoflush=False)
    return Session(), engine


def pull_data(from_db, to_db):
    source, sengine = make_session(from_db)
    smeta = MetaData(bind=sengine)
    destination, dengine = make_session(to_db)

    meta = MetaData()
    meta.reflect(bind=sengine)
    tables = [t.name for t in meta.sorted_tables if not t.name.lower().startswith('sqlite') and t.name not in ['alembic_version', 'monitorlog']]

    print "Creating tables:"
    for table_name in tables:
        print '  ', table_name.ljust(20),
        table = Table(table_name, smeta, autoload=True)
        print '  done.'.rjust(15)
        table.metadata.create_all(dengine)
    print "Tables done.\n"

    print 'Transferring records:'
    errors = []
    for table_name in tables:
        table = Table(table_name, smeta, autoload=True)
        NewRecord = quick_mapper(table)
        columns = table.columns.keys()
        print "  ", table_name.ljust(20),
        r = 0
        for record in source.query(table).all():
            data = dict([(str(column), getattr(record, column)) for column in columns])
            try:
                destination.merge(NewRecord(**data))
                destination.commit()
            except (DataError, OperationalError) as e:
                destination.rollback()
                errors.append(e)
            r += 1
        print '({}) done.'.format(r).rjust(15)
    print '\nimport done.'
    print '\nErrors ({}):'.format(len(errors))
    for e in errors:
        print "  ", e
    destination.commit()


def print_usage():
    print """
Usage: %s -f source_server -t destination_server table [table ...]
    -f, -t = driver://user[:password]@host[:port]/database

Example: %s -f oracle://someuser:PaSsWd@db1/TSH1 \\
    -t mysql://root@db2:3307/reporting table_one table_two
    """ % (sys.argv[0], sys.argv[0])


def quick_mapper(table):
    Base = declarative_base()

    class GenericMapper(Base):
        __table__ = table
    return GenericMapper


if __name__ == '__main__':
    optlist, tables = getopt.getopt(sys.argv[1:], 'f:t:')

    options = dict(optlist)
    if '-f' not in options or '-t' not in options:
        print_usage()
        raise SystemExit

    pull_data(options['-f'], options['-t'])
