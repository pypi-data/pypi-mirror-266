"""

SQLite database class with common, basic functionality for table creation, deletion, read and writes

Contains the following core functionality:

__init__(self, db, dbpath):
    Constructor method for the Database class, initializes the database name (db) and path (dbpath).

getConnection(self):
    Gets a new connection and cursor, making both objects available to the rest of the class.

list_tables(self, booleanNamesOnly=True):
    Lists the tables in the SQLite database. Returns a list of table names by default, but can return a list of tuples with table names and types if booleanNamesOnly is set to False.

write(self, table, data):
    Writes data to the specified table in the database.

list_columns(self, table, VERBOSE=False, booleanColumnsOnly=True):
    Lists the columns in a table. Returns a list of column names by default, but can return a list of tuples with column names and types if booleanColumnsOnly is set to False.

read(self, table, query='SELECT * FROM {}'):
    Reads all data from the specified table using the provided query or a default query.

add_column(self, table, columnname):
    Adds a column to the specified table.

add_table(self, tablename, columns):
    Adds a table with an alphanumeric name to the database if it doesn't already exist.

validate_table_exists(self, table, min_columns=None):
    Validates that the specified table exists in the database.
    Optionally, checks if the tables has a minimum number of columns.

replace_rows(self, table, start_index, end_index, new_data):
    Takes a target table, start and end indices, and replaces data at these index positions with a pandas dataframe.

"""


### Imports ###

## Class-specific critical imports necessary for instantiation of the class
try:
    import sqlite3
except NameError:
    # Pylint error log goes here


    # Warn user at console/cmd level
    print('Could not import sqlite3! Please check environment packages')

    # Generate cache of currently stored project packages when this error occurred.


## Full library imports for class functionality
import pandas as pd

## Partial library imports


### End of Imports ###


### Function Definition ###

# DataBase class
class Database:

    # Class method to instantiate the Database with credentials stored in the AuthorityResolution.controlFile
    def __init__(self, db, dbpath):
        '''
        This is the constructor of Database class.

        Parameters:
        -----------
        - db: str
            The name of the database.
        - dbpath: str
            The path to the database.
        '''

        # Checks whether the dbpath has a trailing slash, and adds it if not
        if dbpath[-1] != '/':
            dbpath = dbpath + '/'

        # Reference the values contained within the project credentials as internal class data for Class functions.
        self.db = db
        self.dbpath = dbpath


    # Gets a new connection and cursor and makes both objects available to the rest of the class
    def getConnection(self):

        # Connect to the DB
        conn = sqlite3.connect(self.dbpath + self.db)

        '''
        A cursor is necessary to operate on the database, but what is a cursor?
        In the context of Python's Database API (PEP 249), a cursor is an object associated with a database connection. 
            https://peps.python.org/pep-0249/

        The cursor is a tool / pointer that allows you to interact with a database. 
        The cursor is an interface or an object that facilitates communication between Python code and the database. 
        The cursor keeps track of the result set of a query and provides methods to fetch and manipulate the data.

        In summary, the cursor acts as a mediator, helping sending queries to the database and receiving the results. 
        The cursor tracks of where we are in the database, fetches data, and performs various operations.
        When we establish a connection to a database, we create a cursor to execute SQL queries. 

        '''
        c = conn.cursor()

        # Make the new conn and cursor available to the rest of the class
        self.conn = conn
        self.c = c


    # Gets a list of tables from the SQLite database specified in the controlFile
    def list_tables(self, booleanNamesOnly=True):
        '''
        This function lists the tables in the SQLite database defined in AuthorityResolution.controlFile.
        '''

        # Get a connection to the SQLite database
        self.getConnection()

        # Create the query, execute it, and return the results from running the query
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        self.c.execute(query)
        res = self.c.fetchall()

        # Close connection now that we have retrieved the tables
        self.conn.close()

        """
        The result will be a list of tuples, with the table name and type.
        The format will be like res = [('table1', 'type1'), ('table2', 'str'), ('table3', 'int32')]
        By default, we return only the names. 
        We can return the list of tuples + types, by calling someDataBaseInstance.list_tables(booleanNamesOnly=False)
        """
        if booleanNamesOnly:
            res = [i[0] for i in res]
            return res
        else:
            return res


    # Writes data to the target table
    def write(self, table, data):
        '''
        This function writes the provided data to the specified database table

        Parameters:
        -----------
        table: str
            The table to write to.
        data: dataframe
            The data to write.
        '''

        # Check for table existence. Will
        self.validate_table_exists(table)

        # Make sure that the columns in the data are the same as the columns in the table
        # Ensure columns in the data match those in the table. Uses set comparison
        if set(self.table_columns) != set(data.columns):

            """
            Unordered Collection: 
                Sets in Python are unordered collections of unique elements.
                When you compare two sets, the order of elements doesn't matter. 
                Only the presence or absence of elements matters.

            They are designed to represent the mathematical concept of a set.
            https://en.wikipedia.org/wiki/Set_theory

            Column Equality: 
                Set comparison ensures table_columns and data_columns contain the same elements.
                If true, both columns are the same.
            """

            raise ValueError("Columns in the data do not match the columns in the table.")

        self.getConnection()

        # Get columns
        cols = data.columns
        # Get values
        vals = data.values
        # Get number of columns
        n_cols = len(cols)

        # Create the query that will insert into the table
        query = "INSERT INTO {} VALUES ({})".format(table, ",".join(["?" for i in range(n_cols)]))

        # Execute the query
        self.c.executemany(query, vals)
        self.conn.commit()
        self.conn.close()


    # List all the columns in a target table. By default, do not print columns and do not return column types as well.
    def list_columns(self, table, VERBOSE=False, booleanColumnsOnly=True):
        '''
        This function lists the columns in a table.

        Parameters:
        -----------
        table: str
            The table to get the columns from.
        '''

        # Validates that the table exists
        self.validate_table_exists(table)

        # Get a live connection and update connection objects
        self.getConnection()

        # Query to get the names of all columns in the table
        self.c.execute("PRAGMA table_info({})".format(table))
        data = self.c.fetchall()
        self.conn.close()

        # If we overrode the default VERBOSE, print the columns.
        if VERBOSE:
            print("The columns in the table {} are:".format(table))
            for col in data:
                # Print the column name only, not the type
                print(col[1])

        """
        The result will be a list of tuples, with the table columns and type.
        The format will be like res = [('page', 'str'), ('html', 'object'), ('length', 'int32')]
        By default, we return only the names. 
        We can return the list of tuples, with data types, by calling someDataBaseInstance.list_columns(b)
        """
        if booleanColumnsOnly:
            data = [columnData[0] for columnData in data]
            return data
        else:
            return data


    def read(self, table, query='SELECT * FROM {}'):
        '''
        This function reads EVERYTHING from the specified table.

        Override the query in the call to this function if more optimised selects are desired.

        Parameters:
        -----------
        table: str
            The table to read from.
        query: str
            The query to execute.
        '''

        # Validates that the table exists
        self.validate_table_exists(table)

        # Get new connection and cursor objects
        self.getConnection()

        # Execute the query, return results, close the connections
        self.c.execute(query.format(table))
        res = self.c.fetchall()
        self.conn.close()

        # Convert the results we retrieved into a pandas dataframe with the DB column names as dataframe.cols
        df = pd.DataFrame(res, columns=self.list_columns(table))
        return df


    # Adds a column to the table
    def add_column(self, table, columnname):
        '''
        This function adds a column to the specified table.

        Parameters:
        -----------
        table: str
            The table to add the column to.
        columnname: str
            The name of the column to add.
        '''
        # Validates that the table exists
        self.validate_table_exists(table)

        # Get new connection and database cursor
        self.getConnection()

        # Query: add a column to the table
        self.c.execute("ALTER TABLE {} ADD COLUMN {}".format(table, columnname))
        self.conn.commit()
        self.conn.close()


    # Adds a table with an alphanumeric name to the database if not already exists.
    def add_table(self, tablename, columns):
        '''
        This function adds a table to the database.

        Parameters:
        -----------
        tablename: str
            The name of the table to add.
        columns: list
            The columns to add to the table.
        '''

        # Make sure that 'tablename' is a string containing only alphanumeric characters or '_'
        import re
        if not re.match("^[a-zA-Z0-9_]*$", tablename):
            raise Exception("The table name can only contain alphanumerical characters or '_'.")

        # Use db_list_tables to check if the table already exists
        if tablename in self.list_tables():
            raise Exception("The table {} already exists.".format(tablename))

        # Get a new DB connection.
        self.getConnection()

        # Query: add a table to the database
        self.c.execute("CREATE TABLE {} ({})".format(tablename, ",".join(columns)))
        self.conn.commit()
        self.conn.close()


    # Check existence of a table in the SQLite database table list.
    def validate_table_exists(self, table, min_columns=None):
        '''
        This function validates that the specified table exists in the database.

        Parameters:
        -----------
        table: str
            The table to validate.
        min_columns: int
            The minimum number of columns that the table should have.
        '''

        # List currently available tables, so we can check whether our table exists in the DB
        tables = self.list_tables()

        # Check if the table exists
        if table not in tables:
            raise ValueError(f"The table {table} does not exist! \
                Add a new table by calling Database().add_table({table}, yourListOfColumns)"
                             )

        # Check if the table has the minimum number of columns
        if min_columns is not None:
            # Throw a ValueError is the target table has less columns that user specified/expected.
            if len(self.list_columns(table)) < min_columns:
                raise ValueError(f"The table, {table}, does not have the minimum number of columns.")

    # Replaces rows in a table in the db at a given index range with new data from a Pandas DataFrame
    def replace_rows(self, table, start_index, end_index, new_data):
        """
        Replace rows X to Y in the specified database table with data from a Pandas DataFrame.

        Parameters:
        -----------
        table: str
            The table in the database to replace rows.
        start_index: int
            The starting index of rows to be replaced.
        end_index: int
            The ending index of rows to be replaced.
        new_data: dataframe
            The new data to replace the specified rows.

        Facilitates the replacement of a range of rows (from X to Y) in table.
        Assumes data from a Pandas DataFrame.
        Ensures that the DataFrame structure aligns with the target table's structure.
        Handles the deletion and insertion operations within a transaction to maintain data integrity.

        Parameters:

            table (str): The name of the target database table.
            start_index (int): The starting index of the rows to be replaced.
            end_index (int): The ending index of the rows to be replaced.
            new_data (DataFrame): The Pandas DataFrame containing the new data for replacement.

        # Example usage:
        # Replace rows 2 to 4 in the "example_table" with data from a new DataFrame
        db_instance = Database(db='example.db', dbpath='path/to/db')
        new_data = pd.DataFrame({'column1': [11, 12, 13], 'column2': ['A', 'B', 'C']})
        db_instance.replace_rows(table='example_table', start_index=1, end_index=3, new_data=new_data)
        """

        # Validate that the table exists
        self.validate_table_exists(table)

        # Validate that the DataFrame has the same columns as the table
        existing_columns = set(self.list_columns(table, booleanColumnsOnly=False))
        new_columns = set(new_data.columns)

        if existing_columns != new_columns:
            raise ValueError("Columns in the new data do not match the columns in the table.")

        # Get a connection to the SQLite database
        self.getConnection()

        # Check if the end_index is within the bounds of the existing data
        existing_data = self.read(table)
        max_index = len(existing_data) - 1

        if end_index > max_index:
            raise ValueError(f"End index ({end_index}) exceeds the maximum index ({max_index}) in the table.")

        # Update the specified rows in the table
        try:
            self.c.execute("DELETE FROM {} WHERE ROWID BETWEEN ? AND ?".format(table),
                           (start_index + 1, end_index + 1))
            self.conn.commit()

            new_values = new_data.values.tolist()
            query = "INSERT INTO {} VALUES ({})".format(table,
                                                        ",".join(["?" for _ in range(len(existing_columns))]))

            self.c.executemany(query, new_values)
            self.conn.commit()

        # Rollback any changes if there was an error, and warn the user at console/cmd level
        except sqlite3.Error as e:
            # Handle the error, e.g., rollback changes
            print("Error:", str(e))
            self.conn.rollback()

        # Finally, close the connection to the db, regardless of whether data was committed to the db successfully
        finally:
            # Close the connection
            self.conn.close()


### End of Function Definition ###


### Frozen Variables ###



### End of Frozen Variables ###



### Dynamic Logic ###



### End of Dynamic Logic ###



### Errata ###

"""

If we have the possibility of multiple applications writing concurrently to the same SQLite db, we want another system.
SQLite works best when it is embedded within an application.
For situations where we'd have concurrency, or we want to unify analytics, we should consider alternatives.

One approach might be to, by default, creating a cloud DB endpoint for analytics and logging data.
    If there are multiple applications writing, then at least the concurrency can be handled and the data is unified.
    This should prevent and writing issues and also make it possible to perform better analytics.

From https://www.sqlite.org/whentouse.html:

Appropriate Uses For SQLite
SQLite is not directly comparable to client/server SQL database engines such as MySQL, Oracle, PostgreSQL, or SQL Server since SQLite is trying to solve a different problem.

Client/server SQL database engines strive to implement a shared repository of enterprise data. They emphasize scalability, concurrency, centralization, and control. SQLite strives to provide local data storage for individual applications and devices. SQLite emphasizes economy, efficiency, reliability, independence, and simplicity.

SQLite does not compete with client/server databases. SQLite competes with fopen().

Situations Where SQLite Works Well
Embedded devices and the internet of things
Because an SQLite database requires no administration, it works well in devices that must operate without expert human support. SQLite is a good fit for use in cellphones, set-top boxes, televisions, game consoles, cameras, watches, kitchen appliances, thermostats, automobiles, machine tools, airplanes, remote sensors, drones, medical devices, and robots: the "internet of things".

Client/server database engines are designed to live inside a lovingly-attended datacenter at the core of the network. SQLite works there too, but SQLite also thrives at the edge of the network, fending for itself while providing fast and reliable data services to applications that would otherwise have dodgy connectivity.

Application file format

SQLite is often used as the on-disk file format for desktop applications such as version control systems, financial analysis tools, media cataloging and editing suites, CAD packages, record keeping programs, and so forth. The traditional File/Open operation calls sqlite3_open() to attach to the database file. Updates happen automatically as application content is revised so the File/Save menu option becomes superfluous. The File/Save_As menu option can be implemented using the backup API.

There are many benefits to this approach, including improved performance, reduced cost and complexity, and improved reliability. See technical notes "aff_short.html" and "appfileformat.html" and "fasterthanfs.html" for more information. This use case is closely related to the data transfer format and data container use cases below.

Websites

SQLite works great as the database engine for most low to medium traffic websites (which is to say, most websites). The amount of web traffic that SQLite can handle depends on how heavily the website uses its database. Generally speaking, any site that gets fewer than 100K hits/day should work fine with SQLite. The 100K hits/day figure is a conservative estimate, not a hard upper bound. SQLite has been demonstrated to work with 10 times that amount of traffic.

The SQLite website (https://www.sqlite.org/) uses SQLite itself, of course, and as of this writing (2015) it handles about 400K to 500K HTTP requests per day, about 15-20% of which are dynamic pages touching the database. Dynamic content uses about 200 SQL statements per webpage. This setup runs on a single VM that shares a physical server with 23 others and yet still keeps the load average below 0.1 most of the time.

See also: Hacker New discussion from 2022-12-13.

Data analysis

People who understand SQL can employ the sqlite3 command-line shell (or various third-party SQLite access programs) to analyze large datasets. Raw data can be imported from CSV files, then that data can be sliced and diced to generate a myriad of summary reports. More complex analysis can be done using simple scripts written in Tcl or Python (both of which come with SQLite built-in) or in R or other languages using readily available adaptors. Possible uses include website log analysis, sports statistics analysis, compilation of programming metrics, and analysis of experimental results. Many bioinformatics researchers use SQLite in this way.

The same thing can be done with an enterprise client/server database, of course. The advantage of SQLite is that it is easier to install and use and the resulting database is a single file that can be written to a USB memory stick or emailed to a colleague.

Cache for enterprise data

Many applications use SQLite as a cache of relevant content from an enterprise RDBMS. This reduces latency, since most queries now occur against the local cache and avoid a network round-trip. It also reduces the load on the network and on the central database server. And in many cases, it means that the client-side application can continue operating during network outages.

Server-side database

Systems designers report success using SQLite as a data store on server applications running in the datacenter, or in other words, using SQLite as the underlying storage engine for an application-specific database server.

With this pattern, the overall system is still client/server: clients send requests to the server and get back replies over the network. But instead of sending generic SQL and getting back raw table content, the client requests and server responses are high-level and application-specific. The server translates requests into multiple SQL queries, gathers the results, does post-processing, filtering, and analysis, then constructs a high-level reply containing only the essential information.

Developers report that SQLite is often faster than a client/server SQL database engine in this scenario. Database requests are serialized by the server, so concurrency is not an issue. Concurrency is also improved by "database sharding": using separate database files for different subdomains. For example, the server might have a separate SQLite database for each user, so that the server can handle hundreds or thousands of simultaneous connections, but each SQLite database is only used by one connection.

Data transfer format

Because an SQLite database is a single compact file in a well-defined cross-platform format, it is often used as a container for transferring content from one system to another. The sender gathers content into an SQLite database file, transfers that one file to the receiver, then the receiver uses SQL to extract the content as needed.

An SQLite database facilitates data transfer between systems even when the endpoints have different word sizes and/or byte orders. The data can be a complex mix of large binary blobs, text, and small numeric or boolean values. The data format can be easily extended by adding new tables and/or columns, without breaking legacy receivers. The SQL query language means that receivers are not required to parse the entire transfer all at once, but can instead query the received content as needed. The data format is "transparent" in the sense that it is easily decoded for human viewing using a variety of universally available, open-source tools, from multiple vendors.

File archive and/or data container

The SQLite Archive idea shows how SQLite can be used as a substitute for ZIP archives or Tarballs. An archive of files stored in SQLite is only very slightly larger, and in some cases actually smaller, than the equivalent ZIP archive. And an SQLite archive features incremental and atomic updating and the ability to store much richer metadata.

Fossil version 2.5 and later offers SQLite Archive files as a download format, in addition to traditional tarball and ZIP archive. The sqlite3.exe command-line shell version 3.22.0 and later will create, list, or unpack an SQL archiving using the .archive command.

SQLite is a good solution for any situation that requires bundling diverse content into a self-contained and self-describing package for shipment across a network. Content is encoded in a well-defined, cross-platform, and stable file format. The encoding is efficient, and receivers can extract small subsets of the content without having to read and parse the entire file.

SQL archives are useful as the distribution format for software or content updates that are broadcast to many clients. Variations on this idea are used, for example, to transmit TV programming guides to set-top boxes and to send over-the-air updates to vehicle navigation systems.

Replacement for ad hoc disk files

Many programs use fopen(), fread(), and fwrite() to create and manage files of data in home-grown formats. SQLite works particularly well as a replacement for these ad hoc data files. Contrary to intuition, SQLite can be faster than the filesystem for reading and writing content to disk.

Internal or temporary databases

For programs that have a lot of data that must be sifted and sorted in diverse ways, it is often easier and quicker to load the data into an in-memory SQLite database and use queries with joins and ORDER BY clauses to extract the data in the form and order needed rather than to try to code the same operations manually. Using an SQL database internally in this way also gives the program greater flexibility since new columns and indices can be added without having to recode every query.

Stand-in for an enterprise database during demos or testing

Client applications typically use a generic database interface that allows connections to various SQL database engines. It makes good sense to include SQLite in the mix of supported databases and to statically link the SQLite engine in with the client. That way the client program can be used standalone with an SQLite data file for testing or for demonstrations.

Education and Training

Because it is simple to setup and use (installation is trivial: just copy the sqlite3 or sqlite3.exe executable to the target machine and run it) SQLite makes a good database engine for use in teaching SQL. Students can easily create as many databases as they like and can email databases to the instructor for comments or grading. For more advanced students who are interested in studying how an RDBMS is implemented, the modular and well-commented and documented SQLite code can serve as a good basis.

Experimental SQL language extensions

The simple, modular design of SQLite makes it a good platform for prototyping new, experimental database language features or ideas.

Situations Where A Client/Server RDBMS May Work Better
Client/Server Applications

If there are many client programs sending SQL to the same database over a network, then use a client/server database engine instead of SQLite. SQLite will work over a network filesystem, but because of the latency associated with most network filesystems, performance will not be great. Also, file locking logic is buggy in many network filesystem implementations (on both Unix and Windows). If file locking does not work correctly, two or more clients might try to modify the same part of the same database at the same time, resulting in corruption. Because this problem results from bugs in the underlying filesystem implementation, there is nothing SQLite can do to prevent it.

A good rule of thumb is to avoid using SQLite in situations where the same database will be accessed directly (without an intervening application server) and simultaneously from many computers over a network.

High-volume Websites

SQLite will normally work fine as the database backend to a website. But if the website is write-intensive or is so busy that it requires multiple servers, then consider using an enterprise-class client/server database engine instead of SQLite.

Very large datasets

An SQLite database is limited in size to 281 terabytes (248 bytes, 256 tibibytes). And even if it could handle larger databases, SQLite stores the entire database in a single disk file and many filesystems limit the maximum size of files to something less than this. So if you are contemplating databases of this magnitude, you would do well to consider using a client/server database engine that spreads its content across multiple disk files, and perhaps across multiple volumes.

High Concurrency

SQLite supports an unlimited number of simultaneous readers, but it will only allow one writer at any instant in time. For many situations, this is not a problem. Writers queue up. Each application does its database work quickly and moves on, and no lock lasts for more than a few dozen milliseconds. But there are some applications that require more concurrency, and those applications may need to seek a different solution.

Checklist For Choosing The Right Database Engine
Is the data separated from the application by a network? → choose client/server

Relational database engines act as bandwidth-reducing data filters. So it is best to keep the database engine and the data on the same physical device so that the high-bandwidth engine-to-disk link does not have to traverse the network, only the lower-bandwidth application-to-engine link.

But SQLite is built into the application. So if the data is on a separate device from the application, it is required that the higher bandwidth engine-to-disk link be across the network. This works, but it is suboptimal. Hence, it is usually better to select a client/server database engine when the data is on a separate device from the application.

Nota Bene: In this rule, "application" means the code that issues SQL statements. If the "application" is an application server and if the content resides on the same physical machine as the application server, then SQLite might still be appropriate even though the end user is another network hop away.

Many concurrent writers? → choose client/server

If many threads and/or processes need to write the database at the same instant (and they cannot queue up and take turns) then it is best to select a database engine that supports that capability, which always means a client/server database engine.

SQLite only supports one writer at a time per database file. But in most cases, a write transaction only takes milliseconds and so multiple writers can simply take turns. SQLite will handle more write concurrency than many people suspect. Nevertheless, client/server database systems, because they have a long-running server process at hand to coordinate access, can usually handle far more write concurrency than SQLite ever will.

Big data? → choose client/server

If your data will grow to a size that you are uncomfortable or unable to fit into a single disk file, then you should select a solution other than SQLite. SQLite supports databases up to 281 terabytes in size, assuming you can find a disk drive and filesystem that will support 281-terabyte files. Even so, when the size of the content looks like it might creep into the terabyte range, it would be good to consider a centralized client/server database.

Otherwise → choose SQLite!

For device-local storage with low writer concurrency and less than a terabyte of content, SQLite is almost always a better solution. SQLite is fast and reliable and it requires no configuration or maintenance. It keeps things simple. SQLite "just works".

"""


### End of Errata - GNU Terry Pratchett ###