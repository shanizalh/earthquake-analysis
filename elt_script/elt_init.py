import subprocess
import time
import requests
import json
import psycopg2


def wait_for_postgres(host, max_retries=5, delay_seconds=5):
    """Wait for PostgreSQL to become available."""
    retries = 0
    while retries < max_retries:
        try:
            result = subprocess.run(
                ["pg_isready", "-h", host], check=True, capture_output=True, text=True)
            if "accepting connections" in result.stdout:
                print("Successfully connected to PostgreSQL!")
                return True
        except subprocess.CalledProcessError as e:
            print(f"Error connecting to PostgreSQL: {e}")
            retries += 1
            print(
                f"Retrying in {delay_seconds} seconds... (Attempt {retries}/{max_retries})")
            time.sleep(delay_seconds)
    print("Max retries reached. Exiting.")
    return False


# Use the function before running the ELT process
if not wait_for_postgres(host="source_postgres"):
    exit(1)

print("Starting ELT script...")

# # Configuration for the source PostgreSQL database
# source_config = {
#     'dbname': 'source_db',
#     'user': 'postgres',
#     'password': 'secret',
#     # Use the service name from docker-compose as the hostname
#     'host': 'source_postgres',
#     'port': '5432'
# }

# # Configuration for the destination PostgreSQL database
# bi_config = {
#     'dbname': 'bi_db',
#     'user': 'postgres',
#     'password': 'secret',
#     # Use the service name from docker-compose as the hostname
#     'host': 'bi_postgres'
# }

# # Fetch data from USGS Earthquake API
# url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson'
# response = requests.get(url)
# data = response.json()

# conn = psycopg2.connect(
#     dbname=source_config['dbname'],
#     user=source_config['user'],
#     password=source_config['password'],
#     host=source_config['host'],
#     port=source_config['port']
# )

# cur = conn.cursor()

# # Insert data into PostgreSQL
# for feature in data['features']:
#     properties = feature['properties']
#     insert_query = """
#     INSERT INTO earthquakes (place, mag, time, updated, tz, url, detail, felt, cdi, mmi, alert, status, tsunami, sig, net, code, ids, sources, types, nst, dmin, rms, gap, magType, type, title)
#     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#     """
#     values = (
#         properties.get('place'),
#         properties.get('mag'),
#         properties.get('time'),
#         properties.get('updated'),
#         properties.get('tz'),
#         properties.get('url'),
#         properties.get('detail'),
#         properties.get('felt'),
#         properties.get('cdi'),
#         properties.get('mmi'),
#         properties.get('alert'),
#         properties.get('status'),
#         properties.get('tsunami'),
#         properties.get('sig'),
#         properties.get('net'),
#         properties.get('code'),
#         properties.get('ids'),
#         properties.get('sources'),
#         properties.get('types'),
#         properties.get('nst'),
#         properties.get('dmin'),
#         properties.get('rms'),
#         properties.get('gap'),
#         properties.get('magType'),
#         properties.get('type'),
#         properties.get('title')
#     )
    
#     cur.execute(insert_query, values)

# # Commit and close connection
# conn.commit()
# cur.close()
# conn.close()

# print("Data fetched and inserted successfully!")

# Configuration for the source PostgreSQL database
source_config = {
    'dbname': 'source_db',
    'user': 'postgres',
    'password': 'secret',
    # Use the service name from docker-compose as the hostname
    'host': 'source_postgres'
}

# Configuration for the destination PostgreSQL database
bi_config = {
    'dbname': 'bi_db',
    'user': 'postgres',
    'password': 'secret',
    # Use the service name from docker-compose as the hostname
    'host': 'bi_postgres'
}

# Use pg_dump to dump the source database to a SQL file
dump_command = [
    'pg_dump',
    '-h', source_config['host'],
    '-U', source_config['user'],
    '-d', source_config['dbname'],
    '-f', 'data_dump.sql',
    '-w'  # Do not prompt for password
]

# Set the PGPASSWORD environment variable to avoid password prompt
subprocess_env = dict(PGPASSWORD=source_config['password'])

# Execute the dump command
subprocess.run(dump_command, env=subprocess_env, check=True)

# Use psql to load the dumped SQL file into the destination database
load_command = [
    'psql',
    '-h', bi_config['host'],
    '-U', bi_config['user'],
    '-d', bi_config['dbname'],
    '-a', '-f', 'data_dump.sql'
]

# Set the PGPASSWORD environment variable for the destination database
subprocess_env = dict(PGPASSWORD=bi_config['password'])

# Execute the load command
subprocess.run(load_command, env=subprocess_env, check=True)

print("Ending ELT script...")