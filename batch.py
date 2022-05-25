import pymysql
import requests.exceptions

import database
import botcommands
import pandas
import dotenv

if __name__ == '__main__':
    fl = pandas.read_csv(r"log.csv")
    config = dotenv.dotenv_values(".env")
    db = database.connect(config)
    print("Connected to db...")
    cursor = db.cursor()
    cnt = 0
    for i, log_link in enumerate(fl["link"]):
        print("Inserting {}".format(log_link))
        try:
            botcommands.upload_log(log_link, cursor)
            cnt += 1
            if i % 5 == 0 or i + 1 == len(fl["link"]):
                db.commit()

        except requests.exceptions.ConnectionError as e:
            print("Error when requesting log: ", e)
            with open("failed_logs.txt", "a") as f:
                f.write(log_link + "\n")
        except pymysql.Error as e:
            print("Error with DB transaction ", e)
            print("Reconnecting to DB...")
            db = database.connect(config)
            cursor = db.cursor()
            with open("failed_logs.txt", "a") as f:
                f.write(log_link + "\n")
        except Exception as e:
            print("Error occurred when uploading log: ", e)
            with open("failed_logs.txt", "a") as f:
                f.write(log_link + "\n")

    print("Done")
    print("Number of logs: {}".format(cnt))

    db.commit()
    db.close()
