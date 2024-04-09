import mysql.connector as sql
import os
import base64
import colorama
from colorama import Back, Fore, Style
import imghdr
from PIL import Image
from io import BytesIO
import sys

colorama.init(autoreset=True)


def make_connection(host, user, password, database):
    Db = sql.connect(host=host, user=user,
                     password=password, database=database)
    l1 = [Db.is_connected(), Db, database]
    return l1


def insert_image(status, img_path, tablename, correspond_field, correspond_value):
    if status[0] == True:

        image_path = img_path
        ext = imghdr.what(image_path)
        file_size = os.path.getsize(image_path)
        if ext != None:

            if file_size < 64000:
                img = open(image_path, 'rb').read()
                # We must encode the file to get base64 string
                codec = base64.b64encode(img)
                image = codec

                # Adding image to the database in BLOB Encrypted format
                # create cursor
                curssor = status[1].cursor(buffered=True)

                select_image_query = f"SELECT * FROM {tablename} WHERE {correspond_field} = '{correspond_value}'"
                # Execute the query using the cursor
                curssor.execute(select_image_query)

                # Fetch the result
                result = curssor.fetchone()

                if result:
                    pass

                else:
                    print(F'{Fore.RED}{Style.BRIGHT}Error: Either Corresponding field or value does not exist')
                    sys.exit()

                # Query the information schema to check if the Img_ext column exists
                check_ext_query = (
                    # f"SELECT COUNT(*) FROM information_schema.columns WHERE table_name = '{tablename}' AND column_name = 'Img_ext' "

                    f"SHOW COLUMNS from `{tablename}` LIKE 'Img_ext';"
                )

                # Execute the query
                curssor.execute(check_ext_query)

                # Fetch the result
                ext_exists = curssor.fetchone()

                if ext_exists:
                    pass

                else:
                    # Add 'Extension' column
                    curssor.execute(f"ALTER TABLE {tablename} ADD COLUMN Img_ext VARCHAR(5)")
                    # Commit the changes to the database
                    status[1].commit()

                # Query the information schema to check if the ImageFile column exists
                check_column_query = (
                    # f"SELECT COUNT(*) FROM information_schema.columns WHERE table_name = '{tablename}' AND column_name = 'ImageFile' "

                    f"SHOW COLUMNS from `{tablename}` LIKE 'ImageFile';"
                )

                # Execute the query
                curssor.execute(check_column_query)

                # Fetch the result
                column_exists = curssor.fetchone()

                print(column_exists)

                if column_exists:
                    name = correspond_value

                    update_query = f"UPDATE {tablename} SET ImageFile = %s, Img_ext = %s WHERE {correspond_field} = %s"
                    curssor.execute(update_query, (image, ext, name))
                    # Commit the changes to the database
                    status[1].commit()
                    print(F'{Fore.GREEN}{Style.BRIGHT}Success: Image has been inserted for a particular entry')

                else:
                    # Define the ALTER TABLE query
                    alter_table_query = f"ALTER TABLE {tablename} ADD COLUMN ImageFile BLOB"

                    # Execute the ALTER TABLE query
                    curssor.execute(alter_table_query)

                    # Commit the changes to the database
                    status[1].commit()

                    # Adding image
                    name = correspond_value

                    update_query = f"UPDATE {tablename} SET ImageFile = %s, Img_ext = %s WHERE {correspond_field} = %s"
                    curssor.execute(update_query, (image, ext, name))
                    # Commit the changes to the database
                    status[1].commit()
                    print(F'{Fore.GREEN}{Style.BRIGHT}Success: Image has been inserted for a particular entry')


            else:
                print(F'{Fore.YELLOW}{Style.BRIGHT}Warning: File size must be less than 64 KB')

        else:
            print(F'{Fore.RED}{Style.BRIGHT}Error: Not a image file')




    else:
        print(F'{Fore.RED}{Style.BRIGHT}Error: Connection not established Try Again to connect')


def get_image(status, tablename, correspond_field, correspond_value, path=os.getcwd()):
    if status[0] == True:

        # Define Cursor Object
        curssor = status[1].cursor(buffered=True)

        # Check that ImageFile and Image Extension column exist in table or not
        selectt_image_query = f'SELECT ImageFile "File",  Img_ext "extension" FROM {tablename}'
        # Execute the query using the cursor
        try:
            curssor.execute(selectt_image_query)

        except:
            print(
                F'{Fore.RED}{Style.BRIGHT}Error: Images have not inserted in the table {tablename} of database {status[2]}')
            sys.exit()

        select_image_query = f"SELECT ImageFile,Img_ext FROM {tablename} WHERE {correspond_field} = '{correspond_value}'"
        # Execute the query using the cursor
        curssor.execute(select_image_query)

        # Fetch the result
        result = curssor.fetchone()

        if result:
            img_file, extension = result
            # Decode the string
            if img_file == None:
                print(F'{Fore.RED}{Style.BRIGHT}Error: Image have not been inserted for this entry in the database')
                sys.exit()
            binary_data = base64.b64decode(img_file + b'==')
            image = Image.open(BytesIO(binary_data))

            image.save(f"{path}/{correspond_field}_{correspond_value}.{extension}")
            print(F'{Fore.BLUE}{Style.BRIGHT}Saved: Your image has been saved Successfully')


        else:
            print(F'{Fore.RED}{Style.BRIGHT}Error: Either Corresponding field or value does not exist')

    else:
        print(F'{Fore.RED}{Style.BRIGHT}Error: Connection not established Try Again to connect')
