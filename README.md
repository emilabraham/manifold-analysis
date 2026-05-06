# Manfiold Analysis/Backtesting

This sets up some DBs that contain historical manifold markets data.
The data can be pulled from [here](https://docs.manifold.markets/data).
The import scripts are setup to only support `BINARY` contracts since that's what I cared about.

## File structure

- `data` folder: Where the sqlite3 db and all the extracted data lives
- `import.py`: The script to import all the `BINARY` contracts
- `import_bets.py`: The script to import all the bets for those `BINARY` contracts
- `THOUGHTS.md`: My thoughts and analysis

## Setup

1. Download the [data](https://docs.manifold.markets/data) for contracts and bets and place them in the `data` folder
2. Unzip them
3. edit the `import.py` file so that the `SRC` variable points to the extracted contracts JSON
4. Run `python3 import.py` to create the `manifold.db` file and `contracts` table
5. edit the `import_bets.py` file so that the `SRC` variable points to the extracted bets JSON
6. Run `python3 import_bets.py` to create the `manifold.db` file and `bets` table

After this process, the table should be set up with all the `BINARY` contracts with their respective bets.
The bets have a foreign key relationship with the contract.
