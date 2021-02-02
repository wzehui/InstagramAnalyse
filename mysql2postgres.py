import mysql.connector
import psycopg2

#defining connection configuration for the mySQL and postgreSQL server connection
config_m = {
    'user': 'root',  # mysql username connection
    'password': 'St_rsql1504!',  # mysql password
    'host': '127.0.0.1',  # local adress
    'database': 'instagram',  # db schema name
}
config_p = {
    'user': 'postgres',  # postgres username connection
    'password': 'Starten136!',  # postgres password
    'host': '127.0.0.1',  # local adress
    'port': '5432',
    'database': 'Instagram' # db schema name
}

def read_table(table_name):
    # read data from mySQL databank
    db = cur = None  # declaring database and cursor variables
    try:
        db = mysql.connector.connect(**config_m)  # assigning connection with defined configuration
    except mysql.connector.Error as err:
        print(err)  # in case an error occurs print a notification
    else:
        cur = db.cursor()  # assigning a cursor
        cur.execute('select * from table_name;')
        data = cur.fetchall()
        cur.execute('SHOW COLUMNS FROM photodata')
        column_name = cur.fetchall()
        cur.close()
    db.close()
    return column_name, data

def write_table(table_name,column_name,data):
    # write data into postgreSQL
    db = cur = None  # declaring database and cursor variables
    db = psycopg2.connect(**config_p)
    with db:
        cur = db.cursor()
        for row in data:
            # assigns respective Data to variables
            cur.execute(
                "insert into table_name values (%s,%s,%s,%s,%s,%s,%s,%s,%s,"
                "%s,%s) on conflict(userid) do nothing", data)
        db.commit()
        cur.close()


# process Table: phtotdata
# read data from mySQL databank
db = cur = None  # declaring database and cursor variables
try:
    db = mysql.connector.connect(**config_m)  # assigning connection with defined configuration
except mysql.connector.Error as err:
    print(err)  # in case an error occurs print a notification
else:
    cur = db.cursor()  # assigning a cursor
    cur.execute('select * from photodata;')
    data = cur.fetchall()
cur.close()
db.close()

# write data into postgreSQL
db = cur = None  # declaring database and cursor variables
db = psycopg2.connect(**config_p)
with db:
    cur = db.cursor()
    for row in data:
        # assigns respective Data to variables
        userid = row[0]
        server = row[1]
        owner = row[2]
        title = row[3]
        datetaken = row[4]
        datetakenunknown = row[5]
        dateupload = row[6]
        views = row[7]
        latitude = row[8]
        longitude = row[9]
        url_l = row[10]
        cur.execute(
            "insert into photodata values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on conflict(userid) do nothing",
            (userid,server,owner,title,datetaken,datetakenunknown,dateupload,views,latitude,longitude,url_l))
    db.commit()
    cur.close()

# process Table: userdata
# read data from mySQL databank
db = cur = None  # declaring database and cursor variables
try:
    db = mysql.connector.connect(**config_m)  # assigning connection with defined configuration
except mysql.connector.Error as err:
    print(err)  # in case an error occurs print a notification
else:
    cur = db.cursor()  # assigning a cursor
    cur.execute('select * from userdata;')
    data_m = cur.fetchall()
cur.close()
db.close()

# write data into postgreSQL
db = cur = None  # declaring database and cursor variables
db = psycopg2.connect(**config_p)
with db:
    cur = db.cursor()
    cur.execute('select * from userdata;')
    data_p = cur.fetchall()
    db.commit()
    cur.close()

# extract data into two dictionary
userdata_m = {}
for i in range(len(data_m)):
    userdata_m[data_m[i][0]] = data_m[i][1]
userdata_p = {}
for i in range(len(data_p)):
    userdata_p[data_p[i][0]] = data_p[i][1]

# find out the duplicate owner
ownerID_m = []
ownerID_p = []
for i in range(len(data_m)):
    ownerID_m.append(data_m[i][0])
for i in range(len(data_p)):
    ownerID_p.append(data_p[i][0])
same_ownerid = [x for x in ownerID_m if x in ownerID_p]
#print(same_ownerid)

# replace unspecified with specific location, if conflict occurs, keep the location information latest
update = {}
for j in range(len(same_ownerid)):
    if userdata_m[same_ownerid[j]] != userdata_p[same_ownerid[j]]:
        print("old location: %s" % userdata_m[same_ownerid[j]])
        print("new location: %s" % userdata_p[same_ownerid[j]])
        print("\n")
        if userdata_p[same_ownerid[j]] == 'unspecified':
            update[same_ownerid[j]] = userdata_m[same_ownerid[j]]
        else:
            update[same_ownerid[j]] = userdata_p[same_ownerid[j]]

# write data into postgreSQL
db = cur = None  # declaring database and cursor variables
db = psycopg2.connect(**config_p)
with db:
    cur = db.cursor()
    for row in data_m:
        # assigns respective Data to variables
        ownerid = row[0]
        location = row[1]
        cur.execute("insert into userdata values (%s,%s) on conflict(ownerid) do nothing", (ownerid,location))
    for item in update:
       cur.execute("update userdata set location='%s' where ownerid='%s'" %(update[item], item))
    db.commit()
    cur.close()

# process Table: ownermaxdatetaken
# read data from mySQL databank
db = cur = None  # declaring database and cursor variables
try:
    db = mysql.connector.connect(**config_m)  # assigning connection with defined configuration
except mysql.connector.Error as err:
    print(err)  # in case an error occurs print a notification
else:
    cur = db.cursor()  # assigning a cursor
    cur.execute('select * from ownermaxdatetaken;')
    data_m = cur.fetchall()
cur.close()
db.close()

# write data into postgreSQL
db = cur = None  # declaring database and cursor variables
db = psycopg2.connect(**config_p)
with db:
    cur = db.cursor()
    for row in data_m:
        # assigns respective Data to variables
        owner = row[0]
        date = row[1]
        cur.execute("insert into ownermaxdatetaken values (%s,%s) on conflict(owner) do nothing", (owner,date))
    db.commit()
    cur.close()

# process Table: ownermindatetaken
# read data from mySQL databank
db = cur = None  # declaring database and cursor variables
try:
    db = mysql.connector.connect(**config_m)  # assigning connection with defined configuration
except mysql.connector.Error as err:
    print(err)  # in case an error occurs print a notification
else:
    cur = db.cursor()  # assigning a cursor
    cur.execute('select * from ownermindatetaken;')
    data_m = cur.fetchall()
cur.close()
db.close()

# write data into postgreSQL
db = cur = None  # declaring database and cursor variables
db = psycopg2.connect(**config_p)
with db:
    cur = db.cursor()
    for row in data_m:
        # assigns respective Data to variables
        owner = row[0]
        date = row[1]
        cur.execute("insert into ownermindatetaken values (%s,%s) on conflict(owner) do nothing", (owner,date))
    db.commit()
    cur.close()
