FROM python:latest

# Install PostgreSQL command-line tools
RUN apt-get update && apt-get install -y postgresql-client
RUN pip install psycopg2-binary requests

# Copy the ELT script 
COPY elt_script.py .

# Set the default command to run the ELT script
CMD ["python", "elt_script.py"]