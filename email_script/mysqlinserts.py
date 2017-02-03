import pymysql

import configfile as conf
# If mails have been retrieved, establish connection to MySQL database:


def mysqlinserts(processed_mails):
    """Takes values from a dictionary and inserts into specified database.
    """
    try:
        dbconn = pymysql.connect(
            conf.DB_HOST, conf.DB_USER, conf.DB_PASSWORD, conf.DB_SCHEMA)

        cursor = dbconn.cursor()

        for mail in processed_mails:

            insert_query = '''INSERT INTO kudos_staging
                (kudos_from, kudos_to, kudos_reason, kudos_date)
                VALUES('{}','{}','{}','{}')'''

            insert_query = insert_query.format(
                mail['FROM'],
                mail['TO'],
                mail['REASON'],
                mail['DATE'])

            cursor.execute(insert_query)
            dbconn.commit()

        dbconn.close()

    except pymysql.ProgrammingError as e:
        print('Got error {!r}, errno is {}'.format(e, e.args[0]))
        print(e)

    except pymysql.IntegrityError as e:
        print("Integrity Error! Duplicate rows were not inserted.")
        print(e)

    except:
        print("Something bad Happened! We don't know what :-(")

    finally:
        print("\nscript closing now...\n")
        exit()
