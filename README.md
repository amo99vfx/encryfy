# adodbapi

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![PEP 249 Compliant](https://img.shields.io/badge/PEP-249-green.svg)](https://peps.python.org/pep-0249/)
[![License](https://img.shields.io/badge/license-LGPL%2FPSF-blue.svg)](LICENSE)

A pure-Python **PEP 249 (DB-API 2.0)** compliant interface to Microsoft ADO (ActiveX Data Objects). `adodbapi` enables Python applications to seamlessly interact with OLE DB and ODBC databases, including Microsoft SQL Server, Microsoft Access, SQLite, Oracle, and Excel files.

---

## Key Features

- **PEP 249 Compliance**: Complete implementation of standard Python DB-API 2.0 interfaces.
- **Broad Database Support**: Connects to Microsoft SQL Server, MS Access (`.mdb`/`.accdb`), Excel (`.xls`/`.xlsx`), MySQL, PostgreSQL, and Oracle via ADO/OLE DB providers.
- **Parametrized Queries**: Automatic translation of `?` parameter markers to prevent SQL injection.
- **Type Conversions**: Built-in mapping between Python data types (e.g., `datetime`, `decimal.Decimal`, `bytes`) and ADO data types.
- **Cross-Architecture**: Supports both 32-bit and 64-bit Python runtimes on Windows (and Linux via Wine COM emulation).

---

## Prerequisites & Requirements

- **Python**: 3.8 or higher
- **OS**: Windows (native support) or Linux/macOS with Wine/COM support
- **Dependencies**: `pywin32` (`win32com`)

---

## Installation

### Standard Installation

Install `adodbapi` via `pip`:

```bash
pip install adodbapi
Install from SourceBashgit clone [https://github.com/your-username/adodbapi.git](https://github.com/your-username/adodbapi.git)
cd adodbapi
pip install -e .
Getting Started1. Connecting to SQL ServerPythonimport adodbapi

# Define an OLE DB connection string
conn_str = (
    "Provider=MSOLEDBSQL;"
    "Data Source=localhost;"
    "Initial Catalog=MyDatabase;"
    "Integrated Security=SSPI;"
)

# Establish connection and cursor
with adodbapi.connect(conn_str) as conn:
    with conn.cursor() as cursor:
        # Execute query with parameters
        cursor.execute("SELECT ID, Name, CreatedAt FROM Users WHERE Status = ?", ["Active"])
        
        # Fetch results
        results = cursor.fetchall()
        for row in results:
            print(f"ID: {row.ID}, Name: {row.Name}, Created: {row.CreatedAt}")
2. Reading / Writing MS Access (.accdb)Pythonimport adodbapi

conn_str = r"Provider=Microsoft.ACE.OLEDB.12.0;Data Source=C:\data\mydb.accdb;"

conn = adodbapi.connect(conn_str)
cursor = conn.cursor()
cursor.execute("INSERT INTO Logs (Message) VALUES (?)", ["System Startup"])
conn.commit()
conn.close()
3. Querying Excel SpreadsheetsPythonimport adodbapi

conn_str = (
    r"Provider=Microsoft.ACE.OLEDB.12.0;"
    r"Data Source=C:\data\report.xlsx;"
    r'Extended Properties="Excel 12.0 Xml;HDR=YES";'
)

with adodbapi.connect(conn_str) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM [Sheet1$]")
    for row in cursor.fetchall():
        print(row)
Common Connection String Quick ReferenceDatabase EngineExample Provider / Connection StringSQL Server (OLE DB)Provider=MSOLEDBSQL;Data Source=SERVER;Initial Catalog=DB;Integrated Security=SSPI;SQL Server (ODBC)Provider=MSDASQL;Driver={SQL Server};Server=SERVER;Database=DB;Trusted_Connection=Yes;MS Access (.accdb)Provider=Microsoft.ACE.OLEDB.12.0;Data Source=C:\path\to\db.accdb;MS Access (.mdb)Provider=Microsoft.Jet.OLEDB.4.0;Data Source=C:\path\to\db.mdb;Excel (.xlsx)Provider=Microsoft.ACE.OLEDB.12.0;Data Source=C:\path\to\file.xlsx;Extended Properties="Excel 12.0 Xml;HDR=YES";Troubleshooting & FAQThis typically happens when there is an architecture mismatch between your Python environment and your OLE DB drivers:If running 64-bit Python, you must install 64-bit OLE DB drivers (e.g., 64-bit Access Database Engine or OLE DB Driver for SQL Server).If running 32-bit Python, use 32-bit drivers.Install the pywin32 package and register the COM components:Bashpip install pywin32
python -m pywin32_postinstall
Running Unit TestsTo run the internal test suite against your local database driver configurations:Bashpython -m unittest discover -s adodbapi/test
Project StructurePlaintextadodbapi/
├── adodbapi/               # Main package core
│   ├── __init__.py         # Public API entry point
│   ├── adodbapi.py         # DB-API implementation
│   ├── apibase.py          # Abstract base definitions & exception mapping
│   ├── schema.py           # ADO schema reflection tools
│   └── test/               # Unit and integration tests
├── examples/               # Sample scripts (Excel, SQL, Access)
├── LICENSE                 # License agreement
├── README.md               # Repository documentation
└── setup.py                # Package installation script
ContributingContributions are welcome! Please follow these steps:Fork the repository.Create a feature branch (git checkout -b feature/NewFeature).Commit your changes (git commit -m 'Add new feature').Push to the branch (git push origin feature/NewFeature).Open a Pull Request.LicenseThis project is licensed under the LGPL / Python Software Foundation License. See LICENSE for details.
