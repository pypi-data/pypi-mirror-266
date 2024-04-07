rawSQL = {

    # Append to and modify a table with existing data.
    'tableModification' : {
        # Append to an exist table.
        'INSERT' : ["INSERT INTO tablename ('Fred'', 'Worker', 12) VALUES (beaverName, beaverType, weight)",

                    "",
                    ],

        # Alter data
        'ALTER' : ["ALTER TABLE beaverCensus ADD employmentStatus VARCHAR(255)",

                   "ALTER TABLE beaverCensus MODIFY weight INT",
                   ],

        #
        'UPDATE' : ['',
                    ],
    }

    # Create or delete existing tables.
    'tableCreation' : {
        'CREATE' : ['CREATE DATABASE database_name',

                    """
                    CREATE TABLE beaverCensus ('
                    beaverName VARCHAR(255)
                    beaverType VARCHAR(255)
                    beaverWeight INT
                    )
                    """
                    ]

        'DELETE' : '',
    }

}


























