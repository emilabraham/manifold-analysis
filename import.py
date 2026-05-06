import json
import sqlite3

SRC = "data/manifold-contracts-20240706.json"
DB = "data/manifold.db"

CREATE = """
CREATE TABLE IF NOT EXISTS contracts (
    id                      TEXT PRIMARY KEY,
    slug                    TEXT,
    question                TEXT,
    creator_id              TEXT,
    creator_name            TEXT,
    creator_username        TEXT,
    creator_avatar_url      TEXT,
    creator_created_time    INTEGER,

    outcome_type            TEXT,
    mechanism               TEXT,
    market_tier             TEXT,
    visibility              TEXT,
    resolution              TEXT,
    resolver_id             TEXT,
    is_resolved             INTEGER,
    non_predictive          INTEGER,
    is_ranked               INTEGER,
    is_subsidized           INTEGER,
    is_twitch_contract      INTEGER,
    is_spice_payout         INTEGER,
    is_politics             INTEGER,
    deleted                 INTEGER,

    created_time            INTEGER,
    close_time              INTEGER,
    resolution_time         INTEGER,
    last_bet_time           INTEGER,
    last_comment_time       INTEGER,
    last_updated_time       INTEGER,
    cfmm_conversion_time    INTEGER,

    p                       REAL,
    prob                    REAL,
    initial_probability     REAL,
    resolution_probability  REAL,

    pool_yes                REAL,
    pool_no                 REAL,
    dpm_pool_yes            REAL,
    dpm_pool_no             REAL,
    start_pool_yes          REAL,
    start_pool_no           REAL,
    total_bets_yes          REAL,
    total_bets_no           REAL,
    total_shares_yes        REAL,
    total_shares_no         REAL,
    phantom_shares_yes      REAL,
    phantom_shares_no       REAL,

    volume                  REAL,
    volume_24h              REAL,
    total_liquidity         REAL,
    subsidy_pool            REAL,
    real_ante               REAL,
    elasticity              REAL,

    fee_creator             REAL,
    fee_platform            REAL,
    fee_liquidity           REAL,

    prob_change_day         REAL,
    prob_change_week        REAL,
    prob_change_month       REAL,

    unique_bettor_count     INTEGER,
    unique_bettor_count_day INTEGER,
    liked_by_user_count     INTEGER,
    follower_count          INTEGER,
    view_count              INTEGER,
    unique_view_count       INTEGER,
    close_emails_sent       INTEGER,
    mana_limit_per_user     INTEGER,

    popularity_score        REAL,
    daily_score             REAL,
    importance_score        REAL,
    freshness_score         REAL,
    conversion_score        REAL,

    lover_user_id1          TEXT,
    lover_user_id2          TEXT,
    unlisted_by_id          TEXT,
    cover_image_url         TEXT,
    username                TEXT,

    group_slugs             TEXT,
    group_links             TEXT,
    description             TEXT
)
"""

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_resolution      ON contracts(resolution)",
    "CREATE INDEX IF NOT EXISTS idx_is_resolved     ON contracts(is_resolved)",
    "CREATE INDEX IF NOT EXISTS idx_created_time    ON contracts(created_time)",
    "CREATE INDEX IF NOT EXISTS idx_close_time      ON contracts(close_time)",
    "CREATE INDEX IF NOT EXISTS idx_resolution_time ON contracts(resolution_time)",
    "CREATE INDEX IF NOT EXISTS idx_creator_id      ON contracts(creator_id)",
    "CREATE INDEX IF NOT EXISTS idx_market_tier     ON contracts(market_tier)",
    "CREATE INDEX IF NOT EXISTS idx_volume          ON contracts(volume)",
    "CREATE INDEX IF NOT EXISTS idx_prob            ON contracts(prob)",
]

def g(r, *keys, default=None):
    for k in keys:
        if k in r:
            return r[k]
    return default

def bool_col(r, key):
    v = r.get(key)
    if v is None:
        return None
    return 1 if v else 0

def row(r):
    pool        = r.get("pool") or {}
    dpm         = r.get("dpmPool") or {}
    start       = r.get("startPool") or {}
    bets        = r.get("totalBets") or {}
    shares      = r.get("totalShares") or {}
    phantom     = r.get("phantomShares") or {}
    fees        = r.get("collectedFees") or {}
    prob_ch     = r.get("probChanges") or {}
    group_slugs = r.get("groupSlugs") or r.get("groupLinks") and None  # handled below
    group_links = r.get("groupLinks")

    return (
        r.get("id"),
        r.get("slug"),
        r.get("question"),
        r.get("creatorId"),
        r.get("creatorName"),
        r.get("creatorUsername"),
        r.get("creatorAvatarUrl"),
        r.get("creatorCreatedTime"),

        r.get("outcomeType"),
        r.get("mechanism"),
        r.get("marketTier"),
        r.get("visibility"),
        r.get("resolution"),
        r.get("resolverId"),
        bool_col(r, "isResolved"),
        bool_col(r, "nonPredictive"),
        bool_col(r, "isRanked"),
        g(r, "isSubsidized", "isSubsidised", default=None),
        bool_col(r, "isTwitchContract"),
        bool_col(r, "isSpicePayout"),
        bool_col(r, "isPolitics"),
        bool_col(r, "deleted"),

        r.get("createdTime"),
        r.get("closeTime"),
        r.get("resolutionTime"),
        r.get("lastBetTime"),
        r.get("lastCommentTime"),
        r.get("lastUpdatedTime"),
        r.get("cfmmConversionTime"),

        r.get("p"),
        r.get("prob"),
        r.get("initialProbability"),
        r.get("resolutionProbability"),

        pool.get("YES"),
        pool.get("NO"),
        dpm.get("YES"),
        dpm.get("NO"),
        start.get("YES"),
        start.get("NO"),
        bets.get("YES"),
        bets.get("NO"),
        shares.get("YES"),
        shares.get("NO"),
        phantom.get("YES"),
        phantom.get("NO"),

        r.get("volume"),
        r.get("volume24Hours"),
        r.get("totalLiquidity"),
        r.get("subsidyPool"),
        r.get("realAnte"),
        r.get("elasticity"),

        fees.get("creatorFee"),
        fees.get("platformFee"),
        fees.get("liquidityFee"),

        prob_ch.get("day"),
        prob_ch.get("week"),
        prob_ch.get("month"),

        r.get("uniqueBettorCount"),
        r.get("uniqueBettorCountDay"),
        r.get("likedByUserCount"),
        r.get("followerCount"),
        r.get("viewCount"),
        r.get("uniqueViewCount"),
        r.get("closeEmailsSent"),
        r.get("manaLimitPerUser"),

        r.get("popularityScore"),
        r.get("dailyScore"),
        r.get("importanceScore"),
        r.get("freshnessScore"),
        r.get("conversionScore"),

        r.get("loverUserId1"),
        r.get("loverUserId2"),
        r.get("unlistedById"),
        r.get("coverImageUrl"),
        r.get("username"),

        json.dumps(r.get("groupSlugs")) if r.get("groupSlugs") is not None else None,
        json.dumps(group_links) if group_links is not None else None,
        json.dumps(r.get("description")) if r.get("description") else None,
    )

N_COLS = len([ln for ln in CREATE.splitlines() if ln.strip() and not ln.strip().startswith(("CREATE", ")"))])
INSERT = "INSERT OR REPLACE INTO contracts VALUES ({})".format(",".join(["?"] * N_COLS))

print("Loading JSON...")
with open(SRC) as f:
    data = json.load(f)

binary = [r for r in data if r.get("outcomeType") == "BINARY"]
print(f"Binary markets: {len(binary)}")

print("Writing DB...")
con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute(CREATE)

batch = [row(r) for r in binary]
cur.executemany(INSERT, batch)

for idx in INDEXES:
    cur.execute(idx)

con.commit()
con.close()
print(f"Done. Rows written: {len(batch)}")
