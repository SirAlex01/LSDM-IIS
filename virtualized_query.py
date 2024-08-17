import csv
import psycopg2

# Define a function to read a CSV file and extract a specific field
def read_csv(file_path, field_name, encoding_list=['utf-8', 'latin1', 'iso-8859-1']):
    data_set = set()
    
    # Try reading the file with different encodings until it works
    for encoding in encoding_list:
        try:
            with open(file_path, mode='r', encoding=encoding) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Add the value of the specified field to the set (converted to lowercase)
                    data_set.add(row[field_name].lower())
            break  # If successful, exit the loop
        except Exception as e:
            print(f"Failed to read {file_path} with encoding {encoding}: {e}")
    
    return data_set

# Define a function to read a CSV file with a condition on another field
def read_csv_with_condition(file_path, field_name, condition_field, condition_value, encoding_list=['utf-8', 'latin1', 'iso-8859-1']):
    data_set = set()
    
    # Try reading the file with different encodings until it works
    for encoding in encoding_list:
        try:
            with open(file_path, mode='r', encoding=encoding) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Check if the condition is met
                    if condition_value in row[condition_field].lower():
                        # Add the value of the specified field to the set (converted to lowercase)
                        data_set.add(row[field_name].lower())
            break  # If successful, exit the loop
        except Exception as e:
            print(f"Failed to read {file_path} with encoding {encoding}: {e}")
    
    return data_set

# Define a function to fetch albums from a PostgreSQL database
def fetch_albums_from_db():
    data_set = set()
    try:
        # Connect to your PostgreSQL database
        conn = psycopg2.connect(
            dbname="demo",
            user="postgres",
            password="password",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        
        # Execute the query
        cursor.execute("SELECT name FROM album")
        
        # Fetch all results and add to the set (converted to lowercase)
        rows = cursor.fetchall()
        for row in rows:
            data_set.add(row[0].lower())  # row[0] because we are selecting one column
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Failed to fetch data from database: {e}")
    
    return data_set

# Read the albums from T3.csv
t3_albums = read_csv('../T3.csv', 'album')

# Read the albums from T4.csv where Album_type contains "album"
t4_albums = read_csv_with_condition('../T4.csv', 'Album', 'Album_type', 'album')

# Fetch the albums from the PostgreSQL database
album_db_albums = fetch_albums_from_db()

# Calculate the union of albums from T3.csv and T4.csv
union_t3_t4 = t3_albums.union(t4_albums)

# Calculate the difference in both directions
diff_t3_t4_not_in_db = sorted(union_t3_t4.difference(album_db_albums))
diff_db_not_in_t3_t4 = sorted(album_db_albums.difference(union_t3_t4))

# Print the results side by side
print(f"{'T3/T4 but not in DB':<40} | {'DB but not in T3/T4':<40}")
print("-" * 80)
for t3_t4, db in zip(diff_t3_t4_not_in_db, diff_db_not_in_t3_t4):
    print(f"{t3_t4:<40} | {db:<40}")

# Handle case where one list is longer than the other
if len(diff_t3_t4_not_in_db) > len(diff_db_not_in_t3_t4):
    for t3_t4 in diff_t3_t4_not_in_db[len(diff_db_not_in_t3_t4):]:
        print(f"{t3_t4:<40} | {'':<40}")
elif len(diff_db_not_in_t3_t4) > len(diff_t3_t4_not_in_db):
    for db in diff_db_not_in_t3_t4[len(diff_t3_t4_not_in_db):]:
        print(f"{'':<40} | {db:<40}")

# Print the count of differences
print(f"Number of albums in T3/T4: {len(union_t3_t4)}, Number of albums in DB: {len(album_db_albums)}")
print(f"\nNumber of albums in T3/T4 but not in DB: {len(diff_t3_t4_not_in_db)}")
print(f"Number of albums in DB but not in T3/T4: {len(diff_db_not_in_t3_t4)}")
