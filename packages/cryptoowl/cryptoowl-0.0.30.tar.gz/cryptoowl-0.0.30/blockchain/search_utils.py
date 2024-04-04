from datetime import datetime

import numpy as np
import pandas as pd

from blockchain import read_db
from blockchain.constants import GET_ACTIVE_SYMBOLS_DATA_QUERY, GET_AUTHOR_HANDLE_DETAILS_FROM_TWITTER_PROFILE_QUERY, \
    SEARCH_TELEGRAM_DATA_QUERY


def get_onchain_data(search_term, limit=3, start=0):
    query = GET_ACTIVE_SYMBOLS_DATA_QUERY.format(search_term=search_term, start=start, limit=limit)
    data = pd.read_sql(query, con=read_db.conn())
    results = []
    total_results = 0
    if len(data):
        exact_match_data = data[(data["symbol"].str.lower() == search_term) | (data["name"].str.lower() == search_term)]

        combined_data = pd.concat([exact_match_data, data])
        combined_data = combined_data.drop_duplicates(subset=["symbol", "chain_id", "is_coin", "token_id", "pair_id"],
                                                      keep="first")
        combined_data = combined_data.replace(np.nan, None)

        for i in combined_data.itertuples():
            if not i.pair_created_at:
                age_in_seconds = None
            else:
                age_in_seconds = datetime.utcnow().timestamp() - int(i.pair_created_at)

            result_dict = {
                "symbol": i.symbol,
                "name": i.name,
                "is_coin": i.is_coin,
                "chain_id": i.chain_id,
                "token_id": i.token_id,
                "pair_id": i.pair_id,
                "vol_24_hr": i.vol_24_hr,
                "liquidity": i.liquidity,
                "marketcap": i.marketcap,
                "icon": i.icon,
                "buy_tax": i.buy_tax,
                "sell_tax": i.sell_tax,
                "age_in_seconds": age_in_seconds,
                "pair_created_at": i.pair_created_at,
                "twitter": i.twitter,
                "telegram": i.telegram,
                "website": i.website
            }
            results.append(result_dict)
            total_results += 1
        return True, (results, total_results)
    else:
        return False, "No match found!"


def get_twitter_author_handle_data(search_term, limit=3, start=0):
    result = []
    total_results = 0
    if details_from_twitter_profile := read_db.fetchall(
            query=GET_AUTHOR_HANDLE_DETAILS_FROM_TWITTER_PROFILE_QUERY.format(author_handle=search_term, start=start,
                                                                              limit=limit)):

        for dftp in details_from_twitter_profile:
            name, handle, profile_image_url, followers_count, followings_count = dftp

            result.append({
                "author_handle": handle,
                "name": name,
                "profile_image_url": profile_image_url,
                "followers_count": followers_count,
                "followings_count": followings_count
            })
            total_results += 1
        return True, (result, total_results)
    else:
        return False, "No match found!"


def get_telegram_data(search_term, limit=3, start=0):
    result = []
    total_results = 0
    if telegram_filter_data := read_db.fetchall(
            query=SEARCH_TELEGRAM_DATA_QUERY.format(search_term=search_term, limit=limit, start=start)):
        for tfd in telegram_filter_data:
            (channel_id, total_mentions, token_mentions, average_mentions_per_day, name, image_url, tg_link,
             members_count, channel_age, win_rate_30_day) = tfd
            telegram_response_dict = {
                "channel_id": channel_id,
                "channel_name": name,
                "image_url": image_url,
                "channel_link": tg_link,
                "total_mentions": total_mentions,
                "token_mentions": token_mentions,
                "members_count": members_count,
                "channel_age": str(channel_age.timestamp()) if channel_age else None,
                "average_mentions_per_day": average_mentions_per_day,
                "win_rate": win_rate_30_day
            }
            result.append(telegram_response_dict)
            total_results += 1
        return True, (result, total_results)
    else:
        return False, "No match found!"
