import json
import sqlite3

SRC = "data/bets.json"
DB  = "data/manifold.db"

CREATE = """
CREATE TABLE IF NOT EXISTS bets (
    id              TEXT PRIMARY KEY,
    contract_id     TEXT NOT NULL REFERENCES contracts(id),
    user_id         TEXT,
    outcome         TEXT,
    amount          REAL,
    shares          REAL,
    prob_before     REAL,
    prob_after      REAL,
    prob_average    REAL,
    loan_amount     REAL,
    order_amount    REAL,
    limit_prob      REAL,
    dpm_shares      REAL,
    dpm_weight      REAL,
    created_time    INTEGER,
    expires_at      INTEGER,
    is_api          INTEGER,
    is_filled       INTEGER,
    is_cancelled    INTEGER,
    is_sold         INTEGER,
    bet_group_id    TEXT,
    answer_id       TEXT,
    fee_creator     REAL,
    fee_platform    REAL,
    fee_liquidity   REAL,
    fills           TEXT,
    sale            TEXT,
    comment         TEXT
)
"""

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_bets_contract_id  ON bets(contract_id)",
    "CREATE INDEX IF NOT EXISTS idx_bets_user_id      ON bets(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_bets_created_time ON bets(created_time)",
    "CREATE INDEX IF NOT EXISTS idx_bets_outcome      ON bets(outcome)",
]

N_COLS = len([ln for ln in CREATE.splitlines() if ln.strip() and not ln.strip().startswith(("CREATE", ")"))])
INSERT = "INSERT OR REPLACE INTO bets VALUES ({})".format(",".join(["?"] * N_COLS))

def bool_col(b, key):
    v = b.get(key)
    if v is None:
        return None
    return 1 if v else 0

def row(b):
    fees = b.get("fees") or {}
    sale = b.get("sale")
    fills = b.get("fills")
    return (
        b.get("id"),
        b.get("contractId"),
        b.get("userId"),
        b.get("outcome"),
        b.get("amount"),
        b.get("shares"),
        b.get("probBefore"),
        b.get("probAfter"),
        b.get("probAverage"),
        b.get("loanAmount"),
        b.get("orderAmount"),
        b.get("limitProb"),
        b.get("dpmShares"),
        b.get("dpmWeight"),
        b.get("createdTime"),
        b.get("expiresAt"),
        bool_col(b, "isApi"),
        bool_col(b, "isFilled"),
        bool_col(b, "isCancelled"),
        bool_col(b, "isSold"),
        b.get("betGroupId"),
        b.get("answerId"),
        fees.get("creatorFee"),
        fees.get("platformFee"),
        fees.get("liquidityFee"),
        json.dumps(fills) if fills is not None else None,
        json.dumps(sale) if sale is not None else None,
        json.dumps(b["comment"]) if isinstance(b.get("comment"), dict) else b.get("comment"),
    )

print("Loading binary contract IDs...")
con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute("SELECT id FROM contracts")
valid_ids = {r[0] for r in cur.fetchall()}
print(f"  {len(valid_ids)} binary contracts loaded")

cur.execute(CREATE)
for idx in INDEXES:
    cur.execute(idx)

print("Loading bets.json (6.4GB, this may take a minute)...")
with open(SRC) as f:
    data = json.load(f)
print(f"  {len(data)} total bets")

print("Filtering and inserting...")
BATCH = 50_000
batch = []
kept = skipped = 0

for b in data:
    if b.get("contractId") not in valid_ids:
        skipped += 1
        continue
    batch.append(row(b))
    kept += 1
    if len(batch) >= BATCH:
        cur.executemany(INSERT, batch)
        con.commit()
        batch = []
        print(f"  {kept:,} inserted, {skipped:,} skipped...", end="\r")

if batch:
    cur.executemany(INSERT, batch)
    con.commit()

con.close()
print(f"\nDone. Inserted: {kept:,}  Skipped (non-binary): {skipped:,}")
