import calendar
import sys
from datetime import date, timedelta
from urllib.parse import unquote

import requests
from django.core.management.base import BaseCommand
from django.db.models import Max

from count_history_v3.base.models import Parameter
from count_history_v3.humans.models import (
    Human,
    Lifedate,
    Nonhuman,
    Update,
    Wikidata,
    Wikipedia,
)


class Command(BaseCommand):
    help = "This finds notable humans on various wikipedia pages."
    max_days_between_updates = 7
    log_id = "find_notable_humans: "
    sleep_time = 3
    pages_to_scrape = {
        "List_of_days_of_the_year": 1,
        "List_of_years": 1,
        "List_of_decades,_centuries,_and_millennia": 1,
    }
    requests_user_agent = (
        "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0"
    )
    request_timeout = 5
    ignore_startswith = (
        "File:",
        "Special:BookSources",
        "Special:EntityPage",
        "Template_talk:",
        "Talk:",
        "Wikipedia:",
        "Category:",
        "Portal:",
        "List_of_",
        "Help:",
        "Template:",
    )
    ignore_endswith = ("_(identifier)",)

    def custom_print(self, message, style):
        if style == "SUCCESS":
            self.stdout.write(self.style.SUCCESS(f"{self.log_id}{message}"))
        elif style == "OKBLUE":
            self.stdout.write(self.style.MIGRATE_HEADING(f"{self.log_id}{message}"))
        elif style == "WARNING":
            self.stdout.write(self.style.WARNING(f"{self.log_id}{message}"))
        elif style == "ERROR":
            self.stdout.write(self.style.ERROR(f"{self.log_id}{message}"))
        sys.stdout.flush()

    def add_arguments(self, parser):
        pass

    # this is meant to be run regularly (once a week?)
    def handle(self, *args, **options):
        self.custom_print("Starting up...", "OKBLUE")

        # Go through wikipedia looking for notable humans
        for page_title in self.pages_to_scrape:
            pages_to_scrape = self.pages_to_scrape[page_title]
            if pages_to_scrape == 0:
                pass  # Well, then don't scrape any pages
            else:
                parameters = {
                    "action": "parse",
                    "format": "json",
                    "page": page_title,
                }
                request = requests.get(
                    "https://en.wikipedia.org/w/api.php",
                    headers={"User-Agent": self.requests_user_agent},
                    params=parameters,
                    timeout=self.request_timeout,
                )
                if request.status_code != 200:
                    self.custom_print(
                        f"status {request.status_code} accessing {request.url}",
                        "ERROR",
                    )
                else:
                    list_page_text = request.json()["parse"]["text"]["*"]
                    link_start = list_page_text.find("/wiki/", 0)
                    link_count = 0
                    while link_start > -1 and link_count < pages_to_scrape:
                        link_end = list_page_text.find('"', link_start)
                        link_slug = list_page_text[
                            link_start + 6 : link_end  # noqa: E203
                        ]

                        # I am looking at the 3 pages "List_of_days_of_the_year", "List_of_years", and
                        # "List_of_decades,_centuries,_and_millennia" for links to more specific time periods
                        # To find those more specific time period pages, a link found on one of those 3 pages must meet
                        # cond_1 and cond_2 or it won't lead to a more specific time period page
                        cond_1 = False
                        cond_2 = False
                        if page_title == "List_of_days_of_the_year":
                            cond_1 = link_slug.split("_")[0] in calendar.month_name
                            cond_2 = link_slug.split("_")[1].isnumeric()
                        elif page_title == "List_of_years":
                            if link_slug.isnumeric():
                                cond_1 = True
                                cond_2 = True
                            else:
                                link_slug_split = link_slug.split("_")
                                if len(link_slug_split) == 2:
                                    cond_1 = link_slug_split[0].isnumeric()
                                    cond_2 = link_slug_split[1] == "BC"
                                    if cond_1 and cond_2:
                                        pass
                                    else:
                                        cond_1 = link_slug_split[1].isnumeric()
                                        cond_2 = link_slug_split[0] == "AD"
                        elif page_title == "List_of_decades,_centuries,_and_millennia":
                            if (
                                "millennium" in link_slug
                                or "century" in link_slug
                                or "decade" in link_slug
                            ):
                                cond_1 = True
                                cond_2 = True
                            else:
                                cond_1 = link_slug.endswith("BC")
                                cond_2 = link_slug[:-4].isnumeric()
                                if cond_1 and cond_2:
                                    pass
                                else:
                                    cond_1 = link_slug.endswith("s")
                                    cond_2 = link_slug[:-1].isnumeric()
                        else:
                            pass  # not one of the 3 pages I am starting with

                        if cond_1 and cond_2:
                            self.parse_time_page(link_slug)
                            link_count += 1

                        link_start = list_page_text.find("/wiki/", link_end)

        # get all remaining humans who are still not up to date and get updates
        humans = list(
            Human.objects.annotate(most_recent_update=Max("updates__date")).filter(
                most_recent_update__gte=date.today()
                - timedelta(days=self.max_days_between_updates)
            )
        )
        if humans:
            batch = []
            for human in humans:
                if len(batch) == 50 or human == humans[-1]:
                    self.batch_update_humans(batch, "not_listed")
                else:
                    batch.append(human.wikidata.wikipedia.title)

        # TODO: update nonhuman model and place model

        self.custom_print(f"{self.log_id}: The end!", "OKBLUE")

    def parse_time_page(self, time_page_slug):
        self.custom_print(f"Parsing {time_page_slug}", "OKBLUE")

        link_query_batch = []

        parameters = {
            "action": "parse",
            "format": "json",
            "page": time_page_slug,
        }
        request = requests.get(
            "https://en.wikipedia.org/w/api.php",
            headers={"User-Agent": self.requests_user_agent},
            params=parameters,
            timeout=self.request_timeout,
        )
        if request.status_code != 200:
            self.custom_print(
                f"status {request.status_code} accessing {request.url}", "ERROR"
            )
        else:
            time_page_text = request.json()["parse"]["text"]["*"]

            link_on_page_start = time_page_text.find("/wiki/", 0)
            while link_on_page_start > -1:
                link_on_page_end = time_page_text.find('"', link_on_page_start)
                link_on_page = time_page_text[
                    link_on_page_start + 6 : link_on_page_end  # noqa: E203
                ]
                link_on_page_slug = unquote(link_on_page.split("#")[0])

                # Now, I am looking at a specific time period page where we are trying to find notable humans
                # We can start off by ignoring certain types of links
                if link_on_page_slug.isnumeric():
                    pass
                elif (
                    link_on_page_slug not in link_query_batch
                    and not link_on_page_slug.startswith(self.ignore_startswith)
                    and not link_on_page_slug.endswith(self.ignore_endswith)
                ):
                    link_is_another_date = False
                    link_on_page_split = link_on_page_slug.split("_")
                    if len(link_on_page_split) == 1:
                        if link_on_page_split[0] in calendar.month_name:
                            link_is_another_date = True
                    elif len(link_on_page_split) == 2:
                        if (
                            link_on_page_slug not in link_query_batch
                            and link_on_page_split[1].isnumeric()
                        ):
                            link_is_another_date = True
                        elif (
                            link_on_page_split[0].isnumeric()
                            and link_on_page_split[1] == "BC"
                        ):
                            link_is_another_date = True
                        elif (
                            link_on_page_slug not in link_query_batch
                            and link_on_page_split[0] == "AD"
                        ):
                            link_is_another_date = True

                    if not link_is_another_date:
                        link_query_batch.append(link_on_page_slug)

                if (
                    len(link_query_batch) == 50
                    or time_page_text.find("/wiki/", link_on_page_end) == -1
                ):
                    self.batch_update_humans(link_query_batch, time_page_slug)
                link_on_page_start = time_page_text.find("/wiki/", link_on_page_end)

    def batch_update_humans(self, link_query_batch, time_page_slug):
        parameters = {
            "titles": "|".join(link_query_batch),
            "action": "wbgetentities",
            "sites": "enwiki",
            "languages": "en",
            "props": "labels|descriptions|claims|sitelinks",
            "format": "json",
        }
        wikidata_request = requests.get(
            "https://www.wikidata.org/w/api.php",
            headers={"User-Agent": self.requests_user_agent},
            params=parameters,
            timeout=self.request_timeout,
        )
        self.custom_print(
            f"Looking for humans at {wikidata_request.url} ...",
            "OKBLUE",
        )
        link_query_batch = []

        if wikidata_request.status_code != 200:
            self.custom_print(
                f"status {wikidata_request.status_code} accessing {wikidata_request.url}",
                "WARNING",
            )
        else:
            entities = wikidata_request.json()["entities"]

            update_obj, created = Update.objects.get_or_create(
                date=date.today(), source=time_page_slug
            )

            for potential_human_qid in entities:
                unknown_title = None
                potential_human_entities = None
                try:
                    int(potential_human_qid)
                    unknown_title = entities[potential_human_qid]["title"]
                except ValueError:
                    potential_human_entities = entities[potential_human_qid]

                if not unknown_title:
                    try:
                        p31 = potential_human_entities["claims"]["P31"]
                        if p31[0]["mainsnak"]["datavalue"]["value"]["id"] == "Q5":
                            human_qid = int(potential_human_qid[1:])
                            human_entities = potential_human_entities

                            (
                                human_obj,
                                created,
                            ) = Human.objects.get_or_create(qid=human_qid)
                            try:
                                most_recent_update = (
                                    human_obj.updates.all().latest("date").date
                                )
                                time_since_update = date.today() - most_recent_update
                                days_since_update = time_since_update.days
                            except Update.DoesNotExist:
                                days_since_update = self.max_days_between_updates + 1

                            if days_since_update < self.max_days_between_updates:
                                pass
                            else:
                                # update wikidata model
                                try:
                                    description = human_entities["descriptions"]["en"][
                                        "value"
                                    ]
                                except KeyError:
                                    description = ""
                                wd_update = {
                                    "label": human_entities["labels"]["en"]["value"],
                                    "description": description,
                                }
                                wd_object, created = Wikidata.objects.update_or_create(
                                    human=human_obj, defaults=wd_update
                                )
                                parameter_codes = {
                                    "gender": "P21",
                                    "citizenship": "P27",
                                    "ethnicity": "P172",
                                    "religion": "P140",
                                    "occupation": "P106",
                                    "position": "P39",
                                    "birthplace": "P19",
                                    "deathplace": "P20",
                                    "burialplace": "P119",
                                    "education": "P69",
                                    "degree": "P512",
                                    "field": "P101",
                                    "political_party": "P102",
                                    "membership": "P463",
                                    "handedness": "P552",
                                    "twitterfollowers": "P8687",
                                }
                                for p_name in parameter_codes:
                                    if (
                                        parameter_codes[p_name]
                                        in human_entities["claims"]
                                    ):
                                        claim_list = human_entities["claims"][
                                            parameter_codes[p_name]
                                        ]
                                        if p_name == "twitterfollowers":
                                            for claim in reversed(claim_list):
                                                if "P6552" in claim["qualifiers"]:
                                                    wd_object.twitterfollowers = int(
                                                        claim["mainsnak"]["datavalue"][
                                                            "value"
                                                        ]["amount"]
                                                    )
                                                    wd_object.twitterid = int(
                                                        claim["qualifiers"]["P6552"][0][
                                                            "datavalue"
                                                        ]["value"]
                                                    )
                                                    wd_object.save()
                                                    break
                                        else:
                                            for p in claim_list:
                                                try:
                                                    nonhuman_qid = int(
                                                        p["mainsnak"]["datavalue"][
                                                            "value"
                                                        ]["id"][1:]
                                                    )
                                                except KeyError:
                                                    nonhuman_qid = (
                                                        None  # must be an unknown value
                                                    )

                                                if nonhuman_qid:
                                                    (
                                                        nonhuman_object,
                                                        created,
                                                    ) = Nonhuman.objects.update_or_create(
                                                        qid=nonhuman_qid,
                                                        defaults={"qid": nonhuman_qid},
                                                    )
                                                    try:
                                                        parameter_object = (
                                                            Parameter.objects.filter(
                                                                dataset__label="humans"
                                                            ).get(label=p_name)
                                                        )
                                                    except Parameter.DoesNotExist:
                                                        parameter_object = None

                                                    if parameter_object:
                                                        nonhuman_object.parameter.add(
                                                            parameter_object
                                                        )

                                                    wd_object.__getattribute__(
                                                        p_name
                                                    ).add(nonhuman_object)
                                    else:
                                        pass  # key does not have this parameter on wikidata

                                # handle birth and death dates here
                                lifedate_codes = {
                                    Lifedate.Types.BIRTH: "P569",
                                    Lifedate.Types.DEATH: "P570",
                                }
                                for lifedate_type in lifedate_codes:
                                    if (
                                        lifedate_codes[lifedate_type]
                                        in human_entities["claims"]
                                    ):
                                        claim_list = human_entities["claims"][
                                            lifedate_codes[lifedate_type]
                                        ]
                                        for lifedate_claim in claim_list:
                                            lifedate = None
                                            try:
                                                lifedate = lifedate_claim["mainsnak"][
                                                    "datavalue"
                                                ]["value"]["time"]
                                            except KeyError:
                                                pass  # no lifedate for this person

                                            if lifedate:
                                                bc_ad_multiplier = 1
                                                if lifedate[0] == "-":
                                                    lifedate_split = lifedate[1:].split(
                                                        "-"
                                                    )
                                                    bc_ad_multiplier = -1
                                                else:
                                                    lifedate_split = lifedate.split("-")

                                                datavalue = lifedate_claim["mainsnak"][
                                                    "datavalue"
                                                ]
                                                (
                                                    lifedate_obj,
                                                    created,
                                                ) = Lifedate.objects.get_or_create(
                                                    type=lifedate_type,
                                                    year=bc_ad_multiplier
                                                    * int(lifedate_split[0]),
                                                    month=int(lifedate_split[1]),
                                                    day=int(lifedate_split[2][:2]),
                                                    precision=int(
                                                        datavalue["value"]["precision"]
                                                    ),
                                                    calendar=datavalue["value"][
                                                        "calendarmodel"
                                                    ].split("/")[-1],
                                                )
                                                if (
                                                    lifedate_type
                                                    == Lifedate.Types.BIRTH
                                                ):
                                                    wd_object.birthdate.add(
                                                        lifedate_obj
                                                    )
                                                else:
                                                    wd_object.deathdate.add(
                                                        lifedate_obj
                                                    )

                                self.custom_print(
                                    f"Completed wikidata update for {wd_object.label} - {human_obj.qid}",
                                    "SUCCESS",
                                )

                                # update wikipedia model
                                enwiki_title = None
                                try:
                                    enwiki_title = human_entities["sitelinks"][
                                        "enwiki"
                                    ]["title"].replace(" ", "_")
                                except KeyError:
                                    pass

                                if not enwiki_title:
                                    pass  # do not create a wikipedia entry
                                else:
                                    (
                                        wp_object,
                                        created,
                                    ) = Wikipedia.objects.get_or_create(
                                        title=enwiki_title,
                                    )
                                    wd_object.wikipedia = wp_object
                                    wd_object.save()

                                    # update wikipedia object
                                    parameters = {
                                        "title": enwiki_title,
                                        "action": "info",
                                        "format": "json",
                                    }
                                    wikipedia_request = requests.get(
                                        "https://www.wikipedia.org/w/index.php",
                                        headers={
                                            "User-Agent": self.requests_user_agent
                                        },
                                        params=parameters,
                                        timeout=self.request_timeout,
                                    )
                                    status_code = wikipedia_request.status_code
                                    if status_code != 200:
                                        self.custom_print(
                                            f"status {wikipedia_request.status_code} accessing {wikipedia_request.url}",
                                            "WARNING",
                                        )
                                    else:
                                        # pagesize
                                        base_i = wikipedia_request.text.find(
                                            "Page length (in bytes)"
                                        )
                                        start_i = (
                                            wikipedia_request.text.find("<td>", base_i)
                                            + 4
                                        )
                                        end_i = wikipedia_request.text.find(
                                            "</td>", start_i
                                        )
                                        wp_object.pagesize = int(
                                            wikipedia_request.text[
                                                start_i:end_i
                                            ].replace(",", "")
                                        )
                                        wp_object.save()

                                        # page views in last 30 days
                                        base_i = wikipedia_request.text.find(
                                            'mw-pvi-month">'
                                        )
                                        start_i = (
                                            wikipedia_request.text.find(">", base_i) + 1
                                        )
                                        end_i = wikipedia_request.text.find(
                                            "</div>", start_i
                                        )
                                        wp_object.recentviews = int(
                                            wikipedia_request.text[
                                                start_i:end_i
                                            ].replace(",", "")
                                        )
                                        wp_object.save()

                                        # edit count
                                        base_i = wikipedia_request.text.find(
                                            "Total number of edits"
                                        )
                                        start_i = (
                                            wikipedia_request.text.find("<td>", base_i)
                                            + 4
                                        )
                                        end_i = wikipedia_request.text.find(
                                            "</td>", start_i
                                        )
                                        wp_object.editcount = int(
                                            wikipedia_request.text[
                                                start_i:end_i
                                            ].replace(",", "")
                                        )
                                        wp_object.save()

                                        # recent number of edits(within past 30 days)
                                        base_i = wikipedia_request.text.find(
                                            "Recent number of edits (within past 30 days)"
                                        )
                                        start_i = (
                                            wikipedia_request.text.find("<td>", base_i)
                                            + 4
                                        )
                                        end_i = wikipedia_request.text.find(
                                            "</td>", start_i
                                        )
                                        wp_object.recentedits = int(
                                            wikipedia_request.text[
                                                start_i:end_i
                                            ].replace(",", "")
                                        )
                                        wp_object.save()

                                        # article grade"
                                        if (
                                            wikipedia_request.text.find(
                                                'href="/wiki/Category:Featured_articles'
                                            )
                                            > -1
                                        ):
                                            wp_object.grade = Wikipedia.Grades.FEATURED
                                        elif (
                                            wikipedia_request.text.find(
                                                'href="/wiki/Category:Good_articles'
                                            )
                                            > -1
                                        ):
                                            wp_object.grade = Wikipedia.Grades.GOOD
                                        else:
                                            wp_object.grade = Wikipedia.Grades.UNGRADED

                                        self.custom_print(
                                            f"Completed wikipedia update for {wp_object.title}",
                                            "SUCCESS",
                                        )

                                        human_obj.updates.add(update_obj)
                        else:
                            pass  # not a human
                    except KeyError:
                        pass  # definitely not a human
