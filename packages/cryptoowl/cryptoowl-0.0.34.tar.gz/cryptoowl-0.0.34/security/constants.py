SOCIAL_INTELLIGENCE_DB_SECRET_ID = "social-intelligence-db"
QUICK_INTEL_API_KEY_SECRET_ID = "quick-intel-api-key"

HONEYPOT_FINDER_URL = "https://api.honeypot.is/legacy/aws/isHoneypot?chain={chain_id}&token={token_id}"
GO_PLUS_URL = "https://api.gopluslabs.io/api/v1/token_security/{chain_id}?contract_addresses={token_id}"
GET_QUICK_AUDIT_URL = "https://api.quickintel.io/v1/getquickiauditfull"

INSERT_OR_UPDATE_ETH_SECURITY_DATA_QUERY = """
INSERT INTO social.token_properties (token_id, is_honeypot, sell_tax, buy_tax)
VALUES (%s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
is_honeypot=VALUES(is_honeypot), sell_tax=VALUES(sell_tax), buy_tax=VALUES(buy_tax)
"""

UPDATE_OTHER_CHAIN_SECURITY_DATA_QUERY = """
UPDATE blockchains.tokens
SET is_honeypot = %s, sell_tax = %s, buy_tax = %s, holders_count = %s, updated_at = %s
WHERE address = %s
"""

UPDATE_OTHER_CHAIN_SECURITY_DATA_FROM_QUICK_INTEL_QUERY = """
UPDATE blockchains.tokens
SET is_honeypot = %s, sell_tax = %s, buy_tax = %s,
lp_burned = %s, is_scam = %s, can_burn = %s, can_mint = %s,
can_freeze = %s, updated_at = %s
WHERE address = %s
"""

CHAIN_TO_ID_MAP = {
    "ethereum": 1,
    "optimism": 10,
    "cronos": 25,
    "bsc": 56,
    "okex-chain": 66,
    "okt chain": 66,
    "gnosis": 100,
    "heco": 128,
    "polygon": 137,
    "fantom": 250,
    "kucoin": 321,
    "kcc": 321,
    "kucoin token": 321,
    "zksync": 324,
    "ethw": 10001,
    "fon": 201022,
    "arbitrum": 42161,
    "arbitrum-nova": 42161,
    "arbitrum-one": 42161,
    "avalanche": 43114,
    "linea": 59144,
    "base": 8453,
    "tron": "tron",
    "scroll": 534352,
    "solana": "solana",
    "eth": "eth",
    "core": "core",
    "polygonzkevm": "polygonzkevm",
    "loop": "loop",
    "kava": "kava",
    "metis": "metis",
    "astar": "astar",
    "oasis": "oasis",
    "iotex": "iotex",
    "conflux": "conflux",
    "canto": "canto",
    "energi": "energi",
    "velas": "velas",
    "grove": "grove",
    "pulse": "pulse",
    "besc": "besc",
    "shibarium": "shibarium",
    "opbnb": "opbnb",
    "bitrock": "bitrock",
    "mantle": "mantle",
    "lightlink": "lightlink",
    "klaytn": "klaytn",
    "injective": "injective",
    "radix": "radix",
    "sui": "sui",
    "manta": "manta",
    "zeta": "zeta"
}

ID_TO_CHAIN_MAP = {
    1: "eth",
    10: "optimism",
    25: "cronos",
    56: "bsc",
    100: "gnosis",
    128: "heco",
    137: "polygon",
    250: "fantom",
    324: "zksync",
    10001: "ethw",
    201022: "fon",
    42161: "arbitrum",
    43114: "avalanche",
    59144: "linea",
    8453: "base",
    534352: "scroll",
    "solana": "solana",
    "eth": "eth",
    "arbitrum": "arbitrum",
    "bac": "bsc",
    "polygon": "polygon",
    "fantom": "fantom",
    "avalanche": "avalanche",
    "core": "core",
    "zksync": "zksync",
    "polygonzkevm": "polygonzkevm",
    "loop": "loop",
    "kava": "kava",
    "metis": "metis",
    "astar": "astar",
    "oasis": "oasis",
    "iotex": "iotex",
    "conflux": "conflux",
    "canto": "canto",
    "energi": "energi",
    "velas": "velas",
    "grove": "grove",
    "pulse": "pulse",
    "besc": "besc",
    "linea": "linea",
    "base": "base",
    "shibarium": "shibarium",
    "opbnb": "opbnb",
    "bitrock": "bitrock",
    "optimism": "optimism",
    "mantle": "mantle",
    "lightlink": "lightlink",
    "klaytn": "klaytn",
    "injective": "injective",
    "radix": "radix",
    "sui": "sui",
    "manta": "manta",
    "zeta": "zeta",
}
