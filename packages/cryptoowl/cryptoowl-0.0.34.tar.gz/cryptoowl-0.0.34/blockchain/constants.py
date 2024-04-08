SOCIAL_INTELLIGENCE_READ_DB_SECRET_ID = "social-intelligence-read-db"
SOCIAL_INTELLIGENCE_DB_SECRET_ID = "social-intelligence-db"

GET_TOKEN_DETAILS_FROM_SYMBOL_QUERY = """
WITH tokens AS (
    SELECT "eth" AS chain, p.token_id, p.latest_liquidity_usd, p.latest_market_cap, 
    (pop.buy_vol_24_hr_usd + pop.sell_vol_24_hr_usd) AS vol_24_hr, token_symbol
    FROM social.pairs AS p
    LEFT JOIN social.pairs_onchain_properties AS pop
    ON p.pair_id = pop.pair_id
    WHERE p.token_symbol = %(symbol)s
    HAVING vol_24_hr > 0
    UNION ALL
    SELECT chain, address AS token_id, liquidity, marketcap, vol24hUSD AS vol_24_hr,
    symbol AS token_symbol
    FROM blockchains.tokens 
    WHERE symbol = %(symbol)s
    HAVING vol_24_hr > 0
)
SELECT * 
FROM tokens
ORDER BY vol_24_hr DESC
LIMIT %(limit)s
"""

GET_TOKEN_SYMBOL_FOR_MULTIPLE_SYMBOLS_QUERY = """
WITH tokens AS (
    SELECT "eth" AS chain, p.token_id, p.latest_liquidity_usd, p.latest_market_cap, 
    (pop.buy_vol_24_hr_usd + pop.sell_vol_24_hr_usd) AS vol_24_hr, p.token_symbol
    FROM social.pairs AS p
    LEFT JOIN social.pairs_onchain_properties AS pop
    ON p.pair_id = pop.pair_id
    WHERE p.token_symbol IN {symbols}
    HAVING vol_24_hr > 0
    UNION ALL
    SELECT chain, address AS token_id, liquidity, marketcap, vol24hUSD AS vol_24_hr, symbol AS token_symbol
    FROM blockchains.tokens 
    WHERE symbol IN {symbols}
    HAVING vol_24_hr > 0
)
SELECT * 
FROM (
    SELECT *,
    DENSE_RANK() OVER (PARTITION BY token_symbol ORDER BY vol_24_hr DESC) AS token_rank
    FROM tokens
    ORDER BY vol_24_hr DESC
) AS sub
WHERE token_rank <= %(limit)s
"""

GET_ACTIVE_SYMBOLS_DATA_QUERY = """
SELECT symbol, name, is_coin, chain_id, token_id, pair_id, vol_24_hr, liquidity, 
marketcap, icon, buy_tax, sell_tax, pair_created_at, twitter, telegram, website
FROM blockchains.active_symbols
WHERE symbol LIKE '%{search_term}%'
OR name LIKE '%{search_term}%'
OR token_id LIKE '%{search_term}%'
OR pair_id LIKE '%{search_term}%'
ORDER BY vol_24_hr DESC
LIMIT {limit}
OFFSET {start}
"""

GET_AUTHOR_HANDLE_DETAILS_FROM_TWITTER_PROFILE_QUERY = """
SELECT name, handle, profile_image_url, followers_count, followings_count
FROM tickr.twitter_profile
WHERE handle LIKE '%{author_handle}%'
ORDER BY followers_count DESC
LIMIT {limit}
OFFSET {start};
"""

SEARCH_TELEGRAM_DATA_QUERY = """
SELECT
    tcp.channel_id,
    tcp.total_mentions,
    tcp.token_mentions,
    tcp.average_mentions_per_day,
    te.name,
    te.image_url,
    te.tg_link,
    te.members_count,
    te.channel_age,
    tcp.win_rate_30_day
FROM
    telegram.telegram_channel_properties AS tcp
LEFT JOIN
    telegram.telegram_entity AS te
ON
    tcp.channel_id = te.channel_id
WHERE
    te.name LIKE '%{search_term}%'
    ORDER BY tcp.total_mentions DESC
LIMIT {limit}
OFFSET {start};
"""