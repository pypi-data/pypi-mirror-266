Usage
+++++

In the following examples shows you how you can use

.. code-block:: python

    from tabulato import colorful_tabulate, TableRowStyle

    headers = ["Name", "Student Number", "DOB", "Email Address"]

    data = [
        ["John Doe", "S12345", "1995-07-15", "john@example.com"],
        ["Alice Smith", "S67890", "1998-03-22", "alice@example.com"],
        ["Bob Johnson", "S54321", "1997-11-10", "bob@example.com"],
        ["Emma Brown", "S98765", "1996-09-18", "emma@example.com"],
        ["Michael Lee", "S24680", "1999-05-30", "michael@example.com"],
        ["Sophia Wang", "S13579", "1994-12-05", "sophia@example.com"],
        ["David Chen", "S75310", "1992-04-08", "david@example.com"],
        ["Olivia Kim", "S36924", "1993-10-25", "olivia@example.com"],
    ]

    colorful_tabulate(
        data=data,
        column_widths=[20, 20, 20, 30],
    )


.. note:: The above function will result in the following table being created in the terminal.

.. rst-class:: my-table

+----------------------+----------------------+----------------------+--------------------------------+
| name                 | student number       | dob                  | email                          |
+======================+======================+======================+================================+
| John Doe             | S12345               | 1995-07-15           | john@example.com               |
+----------------------+----------------------+----------------------+--------------------------------+
| Alice Smith          | S67890               | 1998-03-22           | alice@example.com              |
+----------------------+----------------------+----------------------+--------------------------------+
| Bob Johnson          | S54321               | 1997-11-10           | bob@example.com                |
+----------------------+----------------------+----------------------+--------------------------------+
| Emma Brown           | S98765               | 1996-09-18           | emma@example.com               |
+----------------------+----------------------+----------------------+--------------------------------+
| Michael Lee          | S24680               | 1999-05-30           | michael@example.com            |
+----------------------+----------------------+----------------------+--------------------------------+
| Sophia Wang          | S13579               | 1994-12-05           | sophia@example.com             |
+----------------------+----------------------+----------------------+--------------------------------+
| David Chen           | S75310               | 1992-04-08           | david@example.com              |
+----------------------+----------------------+----------------------+--------------------------------+
| Olivia Kim           | S36924               | 1993-10-25           | olivia@example.com             |
+----------------------+----------------------+----------------------+--------------------------------+



The colorful table will look as follows:

.. image:: https://github.com/CrispenGari/tabulato/blob/main/images/0.jpg?raw=true
   :align: center
   :width: 400


However you can style the rows of the table using the ``TableRowStyle`` class by specifying the options as follows:

.. code-block:: python

    colorful_tabulate(
        data=data,
        column_widths=[20, 20, 20, 30],
        header_style=TableRowStyle(
            bold=True,
            italic=False,
            color="BLUE",
            background="BG_BLUE",
        ),
        even_row_style=TableRowStyle(
            bold=False,
            italic=False,
            color="GREEN",
            underline=True,
        ),
        odd_row_style=TableRowStyle(
            bold=False,
            italic=False,
            color="YELLOW",
            strikethrough=True,
        ),
    )

.. image:: https://github.com/CrispenGari/tabulato/blob/main/images/1.jpg?raw=true
   :align: center
   :width: 400

The table data can also be a list of python dictionaries. Here is an example of using a list of python dictionaries to generate a table.

.. code-block:: python


    data = [
        {
            "name": "John Doe",
            "student number": "S12345",
            "dob": "1995-07-15",
            "email": "john@example.com",
        },
        {
            "name": "Alice Smith",
            "student number": "S67890",
            "dob": "1998-03-22",
            "email": "alice@example.com",
        },
        {
            "name": "Bob Johnson",
            "student number": "S54321",
            "dob": "1997-11-10",
            "email": "bob@example.com",
        },
        {
            "name": "Emma Brown",
            "student number": "S98765",
            "dob": "1996-09-18",
            "email": "emma@example.com",
        },
        {
            "name": "Michael Lee",
            "student number": "S24680",
            "dob": "1999-05-30",
            "email": "michael@example.com",
        },
        {
            "name": "Sophia Wang",
            "student number": "S13579",
            "dob": "1994-12-05",
            "email": "sophia@example.com",
        },
        {
            "name": "David Chen",
            "student number": "S75310",
            "dob": "1992-04-08",
            "email": "david@example.com",
        },
        {
            "name": "Olivia Kim",
            "student number": "S36924",
            "dob": "1993-10-25",
            "email": "olivia@example.com",
        },
    ]

    colorful_tabulate(
        data=data,
        column_widths=[20, 20, 20, 30],
    )


The ``colorful_tabulate`` is a useful function for visually enhancing tabulated data in terminal output by applying colors and styling. The following are the parameters that this function takes.

.. rst-class:: my-table

+------------------+---------------------------------------+-----------------+----------------------------------------------------------------------------+----------+
| Parameter        | Description                           | Type            | Default                                                                    | Required |
+==================+=======================================+=================+============================================================================+==========+
|  data            | The list of data to be displayed.     |  list           |  -                                                                         |  Yes     |
+------------------+---------------------------------------+-----------------+----------------------------------------------------------------------------+----------+
|  headers         | The list of column headers.           |  list           |  None                                                                      |  No      |
+------------------+---------------------------------------+-----------------+----------------------------------------------------------------------------+----------+
|  colorful        | Whether to display the table in color.|  bool           |  True                                                                      |  No      |
+------------------+---------------------------------------+-----------------+----------------------------------------------------------------------------+----------+
|  bold_header     | Whether to display the header in bold.|  bool           |  True                                                                      |  No      |
+------------------+---------------------------------------+-----------------+----------------------------------------------------------------------------+----------+
|  header_style    | Style for the header row.             |  TableRowStyle  |  TableRowStyle(bold=True, italic=False, color="BLUE", background=None)     |  No      |
+------------------+---------------------------------------+-----------------+----------------------------------------------------------------------------+----------+
|  even_row_style  | Style for even-numbered rows.         |  TableRowStyle  |  TableRowStyle(bold=False, italic=False, color="GREEN", background=None)   |  No      |
+------------------+---------------------------------------+-----------------+----------------------------------------------------------------------------+----------+
|  odd_row_style   | Style for odd-numbered rows.          |  TableRowStyle  |  TableRowStyle(bold=False, italic=False, color="YELLOW", background=None)  |  No      |
+------------------+---------------------------------------+-----------------+----------------------------------------------------------------------------+----------+
|  column_widths   | List of column widths.                |  list           |  []                                                                        |  No      |
+------------------+---------------------------------------+-----------------+----------------------------------------------------------------------------+----------+

The following are the color literals that can be passed to the ``color`` and ``background`` respectively.

.. rst-class:: my-table

+-----------+-------------+
| Color     | Description |
+===========+=============+
| "BLACK"   | Black       |
+-----------+-------------+
| "RED"     | Red         |
+-----------+-------------+
| "GREEN"   | Green       |
+-----------+-------------+
| "YELLOW"  | Yellow      |
+-----------+-------------+
| "BLUE"    | Blue        |
+-----------+-------------+
| "PURPLE"  | Purple      |
+-----------+-------------+
| "CYAN"    | Cyan        |
+-----------+-------------+
| "WHITE"   | White       |
+-----------+-------------+

.. rst-class:: my-table
    
+--------------+-------------------+
| Background   | Description       |
+==============+===================+
| "BG_BLACK"   | Black background  |
+--------------+-------------------+
| "BG_RED"     | Red background    |
+--------------+-------------------+
| "BG_GREEN"   | Green background  |
+--------------+-------------------+
| "BG_BLUE"    | Blue background   |
+--------------+-------------------+
| "BG_PURPLE"  | Purple background |
+--------------+-------------------+
| "BG_CYAN"    | Cyan background   |
+--------------+-------------------+
| "BG_WHITE"   | White background  |
+--------------+-------------------+
| "BG_YELLOW"  | Yellow background |
+--------------+-------------------+

