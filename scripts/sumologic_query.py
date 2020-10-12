# Script defaults:
#    timezone - CET
#    verbose output - disabled
#    ByReceiptTime - False
#
# Example #1:
# python sumologic_query_3.py -id <access_id> -k <access_key> -ft <from_time> -tt <to_time> -tz <timezone> query1.sumoql
#
# Example #2:
# python sumologic_query_3.py -id <access_id> -k <access_key> -ft 2020-10-03T00:00:00 -tt 2020-10-05T08:00:00 query1.sumoql
#
# Example #3 - verbose output:
# python sumologic_query_3.py -id <access_id> -k <access_key> -ft 2020-10-03T00:00:00 -tt 2020-10-05T08:00:00 -v query1.sumoql
#

import time
import logging
import click
from sumologic import SumoLogic
from pprint import pprint

logging.basicConfig(level=logging.DEBUG)


@click.command()
@click.argument("query", type=click.File("rb"))
@click.option("-id", "--access-id", type=str, required=True, help="Access ID")
@click.option("-k", "--access-key", type=str, required=True, help="Access Key")
@click.option(
    "-e",
    "--endpoint",
    type=str,
    required=True,
    help="Sumologic endpoint",
    default="https://api.us2.sumologic.com/api",
)
@click.option(
    "-ft",
    "--from-time",
    type=str,
    required=True,
    help="From time. Example: 2020-10-03T00:00:00 or 2020-10-03T21:00:00",
)
@click.option(
    "-tt",
    "--to-time",
    type=str,
    required=True,
    help="From time. Example: 2020-10-03T00:00:00 or 2020-10-03T21:00:00",
)
@click.option(
    "-tz",
    "--timezone",
    type=str,
    required=True,
    help="Timezone. Example: CET",
    default="CET",
)
@click.option(
    "-rt",
    "--by-receipt-time",
    type=bool,
    required=True,
    help="ByReceiptTime",
    default=False,
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Verbose output. Disabled by default",
    default=False,
)
@click.option(
    "-l", "--limit", type=int, help="Number of messages to display", default=50
)
def sumo_query(**kwargs):
    # create variables based on user input
    query_file = kwargs.pop("query", None)
    access_id = kwargs.pop("access_id", None)
    access_key = kwargs.pop("access_key", None)
    endpoint = kwargs.pop("endpoint", None)
    from_time = kwargs.pop("from_time", None)
    to_time = kwargs.pop("to_time", None)
    by_receipt_time = kwargs.pop("by_receipt_time", None)
    timezone = kwargs.pop("timezone", None)
    verbose = kwargs.pop("verbose", None)
    LIMIT = kwargs.pop("limit", None)

    delay = 5
    query = query_file.read().decode()

    # create connection instance
    sumo = SumoLogic(access_id, access_key, endpoint)

    # create search job
    search_job = sumo.search_job(query, from_time, to_time, timezone, by_receipt_time)

    # create search job status object and check state of the search job
    search_job_status = sumo.search_job_status(search_job)
    while search_job_status["state"] != "DONE GATHERING RESULTS":
        if search_job_status["state"] == "CANCELLED":
            break
        time.sleep(delay)
        search_job_status = sumo.search_job_status(search_job)

    if search_job_status["state"] == "DONE GATHERING RESULTS":
        count = search_job_status["recordCount"]
        limit = count if count < LIMIT and count != 0 else LIMIT
        result = sumo.search_job_messages(search_job, limit=limit)

    messages = result["messages"]

    # print result of the search job
    num = 0
    for map in messages:
        # map_string = map['map']['_raw'].replace("\\n","").replace("\\t","").replace("\\","")
        map_string = map["map"]["_raw"]
        try:
            map_dict = eval(map_string)
        except NameError:
            map_dict = eval(
                map_string.replace("null", "None")
                .replace("true", "True")
                .replace("false", "False")
            )
        # click.secho("//////// Docker info ////////", bg='white', fg='black')

        try:
            docker_dict = map_dict["message"]["docker"]
            click.secho("//////// Docker info ////////", bg="white", fg="black")
            pprint(docker_dict)

        except (KeyError, TypeError):
            click.secho("//////// Whole log message ////////", bg="white", fg="black")
            pprint(map_dict)
            click.secho(
                "\\\\\\\\\\\\\\\\ Whole log message \\\\\\\\\\\\\\\\",
                bg="white",
                fg="black",
            )
            print()
            print("########" * 10 + "   " + str(num) + "   " + "########" * 10)
            print()
            num += 1
            continue

        click.secho(
            "\\\\\\\\\\\\\\\\ Docker info \\\\\\\\\\\\\\\\", bg="white", fg="black"
        )

        click.secho("//////// Kubernetes info ////////", bg="white", fg="black")
        pprint(map_dict["message"]["kubernetes"])
        click.secho(
            "\\\\\\\\\\\\\\\\ Kubernetes info \\\\\\\\\\\\\\\\", bg="white", fg="black"
        )

        click.secho("//////// Log ////////", bg="white", fg="black")
        try:
            map_log_dict = eval(map_dict["message"]["log"])
        except SyntaxError:
            pprint(map_dict["message"]["log"], width=500)
            click.secho("\\\\\\\\\\\\\\\\ Log \\\\\\\\\\\\\\\\", bg="white", fg="black")
            print()
            print("########" * 10 + "   " + str(num) + "   " + "########" * 10)
            print()
            num += 1
            continue

        if type(map_log_dict) != dict:
            pprint(map_log_dict, width=500)
        else:
            if not verbose:
                for key, value in map_log_dict.items():
                    if key == "stacktrace" or key == "errorVerbose":
                        continue
                    else:
                        pprint(f"{key} : {map_log_dict[key]}", width=500)
            else:
                pprint(map_log_dict, width=500)
        click.secho("\\\\\\\\\\\\\\\\ Log \\\\\\\\\\\\\\\\", bg="white", fg="black")

        print()
        print("########" * 10 + "   " + str(num) + "   " + "########" * 10)
        print()
        num += 1


if __name__ == "__main__":
    sumo_query()
