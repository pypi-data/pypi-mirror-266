from datetime import datetime

from blockchain import read_db
from blockchain.constants import GET_ACTIVE_SYMBOLS_DATA_QUERY, GET_AUTHOR_HANDLE_DETAILS_FROM_TWITTER_PROFILE_QUERY, \
    SEARCH_TELEGRAM_DATA_QUERY, GET_TWEETS_QUERY
from common_utils.chain_utils import id_to_chain
from common_utils.time_utils import format_datetime


def get_onchain_data(search_term, limit=3, start=0):
    result = []
    total_results = 0
    query = GET_ACTIVE_SYMBOLS_DATA_QUERY.format(search_term=search_term, start=start, limit=limit)
    if data := read_db.fetchall(query=query):
        for i in data:
            (symbol, name, is_coin, chain_id, token_id, pair_id, vol_24_hr, liquidity, marketcap, icon, buy_tax,
             sell_tax, pair_created_at, twitter, telegram, website) = i
            chain = "ethereum" if chain_id == 1 else id_to_chain.get(chain_id)
            if not pair_created_at:
                age_in_seconds = None
            else:
                age_in_seconds = datetime.utcnow().timestamp() - int(pair_created_at)
            result.append({
                "symbol": symbol,
                "name": name,
                "is_coin": is_coin,
                "chain_id": chain_id,
                "chain": chain,
                "token_id": token_id,
                "pair_id": pair_id,
                "vol_24_hr": vol_24_hr,
                "liquidity": liquidity,
                "marketcap": marketcap,
                "icon": icon,
                "buy_tax": buy_tax,
                "sell_tax": sell_tax,
                "age_in_seconds": age_in_seconds,
                "pair_created_at": pair_created_at,
                "twitter": twitter,
                "telegram": telegram,
                "website": website
            })
            total_results += 1
        return True, (result, total_results)
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


def get_tweets_data(search_term=None, tweet_id=None, author_handle=None, limit=3, start=0):
    result = []
    if not search_term and not tweet_id and not author_handle:
        return False, "Either search_term, tweet_id or author_handle is required"

    where_condition = ""
    if search_term:
        where_condition = f"body LIKE '%{search_term}%'"
    elif tweet_id:
        where_condition = f"tweet_id = '{tweet_id}'"
    elif author_handle:
        where_condition = f"author_handle = '{author_handle}'"
    
    query = GET_TWEETS_QUERY.format(where_condition=where_condition, start=start, limit=limit)

    if data := read_db.fetchall(query=query):
        for i in data:
            tweet_id, body, author_handle, tweet_create_time = i
            result.append({
                "tweet_id": tweet_id,
                "tweet_body": body,
                "author_handle": author_handle,
                "tweet_create_time": format_datetime(input_date_string=str(tweet_create_time))
            })

        return True, result
    else:
        return False, "No match found!"
