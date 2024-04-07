import logging
import datetime
import json
import pprint
import psycopg2
import psycopg2.extras
import psycopg2.tz

logger = logging.getLogger(__name__)


def human_delta(td_object: datetime.timedelta, max: int = 0):
    ms = int(td_object.total_seconds() * 1000)
    if ms == 0:
        return "0 ms"
    sign = ""
    if ms < 0:
        ms = -ms
        sign = "-"
    # fmt: off
    periods = [
        ("year",  1000 * 60 * 60 * 24 * 365),
        ("month", 1000 * 60 * 60 * 24 * 30),
        ("day",   1000 * 60 * 60 * 24),
        ("hr",    1000 * 60 * 60),
        ("min",   1000 * 60),
        ("sec",   1000),
        ("ms", 1)
    ]
    # fmt: on

    strings = []
    ct: int = 0
    for period_name, period_ms in periods:
        if ms > period_ms:
            period_value, ms = divmod(ms, period_ms)
            # has_s = "s" if period_value > 1 else ""
            # strings.append("%s %s%s" % (period_value, period_name, has_s))
            strings.append(f"{period_value} {period_name}")
            ct += 1
            if max > 0 and ct > max:
                break
    return sign + ", ".join(strings)  # + f"({td_object}, {ms})"


def item_to_str(item):
    prefix = "#=- "
    ret = "\n"
    if not item:
        ret = f"""
{prefix}
{prefix}Job:    NONE
{prefix}
"""
        return ret
    # logger.info(pprint.pformat(item))
    ret += f"{prefix}\n"
    type = item.get("type", "unknown-type")
    id = item.get("id", "XXXXXXX")
    ret += f"{prefix}BATCH JOB {type}: {id}\n"
    try:
        now = datetime.now()
        created_ago = human_delta(now - item.get("created_at"), None)
        updated_ago = human_delta(now - item.get("updated_at"), None)
        ret += f"{prefix}Created: {created_ago}, Updated: {updated_ago} ####\n"
    except:
        pass
    try:
        source = item.get("source")
        if source:
            ret += f"{prefix}Source: {source}\n"
        status = item.get("status")
        if status:
            ret += f"{prefix}Status: {status}\n"
    except:
        pass
    data_raw = item.get("data")
    if data_raw:
        ret += f"{prefix}Data:\n\n"
        try:
            data = json.loads(data_raw)
            data_str = json.dumps(data, indent=3, sort_keys=True, default=str)
            ret += data_str + "\n\n"
        except json.JSONDecodeError as e:
            ret += f"{prefix}JSON PARSE ERROR\n"
    result_raw = item.get("result")
    if result_raw:
        ret += f"{prefix}Result:\n\n"
        try:
            result = json.loads(result_raw)
            result_str = json.dumps(result, indent=3, sort_keys=True, default=str)
            ret += result_str + "\n\n"
        except json.JSONDecodeError as e:
            ret += result_raw + "\n\n"
    ret += f"{prefix}\n"
    return ret


def test_log_item():
    # fmt:off
    test_item={
        'created_at': datetime.datetime(2022, 1, 12, 21, 39, 55, 432446, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)),
        'data': '{\n   "shopify_domain": "merchbot-test.myshopify.com"\n}',
        'id': 510946,
        'priority': 50,
        'result': "Successfully blabla",
        'source': 'shopify/orders-fetch-all',
        'status': 'in-progress',
        'type': 'shopify/orders-update',
        'updated_at': datetime.datetime(2022, 1, 12, 21, 39, 55, 440179, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None))
    }
    # fmt:on
    logger.info(item_to_str(test_item))
    logger.info(item_to_str({}))
    logger.info(item_to_str({"id": "bob"}))
