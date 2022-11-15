from collections import Counter

from django.db import models
from django.db.models import F, Max, Q


# Create your models here.
class Update(models.Model):
    date = models.DateField()
    source = models.SlugField(max_length=200)

    class Meta:
        unique_together = ["date", "source"]


class Human(models.Model):
    qid = models.PositiveBigIntegerField(primary_key=True, default=0)
    updates = models.ManyToManyField(Update)

    @classmethod
    def get_chart_titles(
        cls, query_dict, parameter_titles_dict, counting_label, chart_type
    ):
        title = ""
        subtitle = ""
        x_title = ""
        y_title = ""
        if chart_type == "line":
            title = f"Total {counting_label} Over Time"
            x_title = "Year"
            y_title = counting_label
        elif chart_type == "map":
            title = f"{counting_label}"

        if query_dict:
            subtitle = "Whose "
            all_parameters = list(query_dict.keys())
            for parameter in all_parameters:
                if len(all_parameters) > 1 and all_parameters.index(parameter) != 0:
                    subtitle += " AND "
                subtitle += f"<strong><em>{parameter_titles_dict[parameter]}</em></strong> includes "
                for value_list in query_dict[parameter]:
                    if (
                        len(value_list) > 1
                        and query_dict[parameter].index(value_list) != 0
                    ):
                        subtitle += " AND "
                    for value in value_list:
                        if (
                            len(value_list) > 1
                            and value_list.index(value) == len(value_list) - 1
                        ):
                            subtitle += " OR "
                        subtitle += f"<em>{Nonhuman.objects.get(qid=value).label}</em>"
                        if (
                            len(value_list) != 2
                            and value_list.index(value) < len(value_list) - 1
                        ):
                            subtitle += ", "
                    if value_list != query_dict[parameter][-1]:
                        subtitle += " AND "

        return title, subtitle, x_title, y_title

    @classmethod
    def get_all_line_data(cls, counting_label):
        all_data_queryset = None

        if "births" in counting_label.split("|") or "deaths" in counting_label.split(
            "|"
        ):
            q_filter = Q()
            for d in counting_label.split("|"):
                q_filter |= Q((f"{d[:-1]}date__isnull", False))
            all_data_queryset = Wikidata.objects.filter(q_filter)
        elif counting_label == "dataset":
            all_data_queryset = Wikidata.objects.all()

        return all_data_queryset

    @classmethod
    def get_all_map_data(cls, counting_label):
        all_data_queryset = None

        if counting_label == "places":
            all_data_queryset = Wikidata.objects.filter(
                (
                    Q(birthdate__isnull=False)
                    & Q(birthplace__place__longitude__isnull=False)
                    & Q(birthplace__place__latitude__isnull=False)
                )
                | (
                    Q(deathdate__isnull=False)
                    & Q(deathplace__place__longitude__isnull=False)
                    & Q(deathplace__place__latitude__isnull=False)
                )
                | (
                    Q(deathdate__isnull=False)
                    & Q(burialplace__place__longitude__isnull=False)
                    & Q(burialplace__place__latitude__isnull=False)
                )
            )

        return all_data_queryset

    @classmethod
    def get_q_filter(cls, qid_list, parameter_label):
        q_filter = Q()
        for qid in qid_list:
            place_type = None
            if "continent" in parameter_label:
                place_type = "continent"
            elif "country" in parameter_label:
                place_type = "country"

            if place_type:
                q_filter |= Q(
                    (
                        f"{parameter_label.split('_')[0]}place__place__{place_type}__qid",
                        qid,
                    )
                )
            else:
                q_filter |= Q((f"{parameter_label}__qid", qid))

        return q_filter

    @classmethod
    def get_line_chart_data(cls, queried_queryset, counting_label):
        totals_per_time_data = {}
        # print(filtered_queryset.get(qid=152824).birthdate.first().year)
        if "births" in counting_label.split("|") or "deaths" in counting_label.split(
            "|"
        ):
            for d in counting_label.split("|"):
                all_dates_by_qid = queried_queryset.filter(
                    **{f"{d[:-1]}date__isnull": False}
                ).values_list(
                    "qid",
                    f"{d[:-1]}date__year",
                )
                all_years = list(zip(*set(all_dates_by_qid)))[1]
                totals_per_time_data[d] = Counter(all_years)
        elif counting_label == "dataset":
            pass  # TODO

        return totals_per_time_data

    @classmethod
    def get_map_chart_data(cls, queried_queryset, counting_label):
        time_map_data = {}
        date_type = counting_label[:-1]
        if counting_label == "burials":
            date_type = "death"

        if counting_label in ["births", "deaths", "burials"]:
            time_map_data = (
                queried_queryset.alias(
                    best_date=Max(f"{date_type}date__precision"),
                    best_place=Max(f"{counting_label[:-1]}place__place__precision"),
                )
                .filter(**{f"{date_type}date__precision": F("best_date")})
                .filter(
                    **{f"{counting_label[:-1]}place__place__precision": F("best_place")}
                )
                .annotate(
                    title=F("label"),
                    year=F(f"{date_type}date__year"),
                    longitude=F(f"{counting_label[:-1]}place__place__longitude"),
                    latitude=F(f"{counting_label[:-1]}place__place__latitude"),
                )
                .values("title", "year", "longitude", "latitude")
            )
        elif counting_label == "places":
            pass  # TODO

        return list(time_map_data)


class Nonhuman(models.Model):
    qid = models.PositiveBigIntegerField(primary_key=True, default=0)
    label = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    lastupdate = models.DateField(null=True, blank=True)
    parameter = models.ManyToManyField("base.Parameter", related_name="parameter")

    @classmethod
    def is_value_valid(cls, value_qid, parameter_label):
        return Nonhuman.objects.get(
            qid=value_qid, parameter__label=parameter_label
        ).exists()

    @classmethod
    def search_parameter_values(cls, search_str, parameter_label):
        other_place_params = [
            "birth_country",
            "birth_continent",
            "death_country",
            "death_continent",
            "burial_country",
            "burial_continent",
        ]
        if parameter_label in other_place_params:
            event = parameter_label.split("_")[0]
            place = parameter_label.split("_")[1]
            results = (
                Nonhuman.objects.filter(parameter__label=f"{event}place")
                .filter(**{f"place__{place}__label__istartswith": search_str})
                .order_by(f"place__{place}__label")
                .distinct(f"place__{place}__label")
                .annotate(
                    id=models.F(f"place__{place}__qid"),
                    text=models.F(f"place__{place}__label"),
                )
                .values("id", "text")
            )
        else:
            results = (
                Nonhuman.objects.filter(parameter__label=parameter_label)
                .filter(label__istartswith=search_str)
                .order_by("label")
                .distinct("label")
                .annotate(id=models.F("qid"), text=models.F("label"))
                .values("id", "text")
            )

        return list(results)


class Place(models.Model):
    nonhuman = models.OneToOneField(
        Nonhuman, on_delete=models.CASCADE, primary_key=True
    )
    latitude = models.DecimalField(
        max_digits=6, decimal_places=3, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=6, decimal_places=3, blank=True, null=True
    )
    precision = models.DecimalField(
        max_digits=10, decimal_places=8, blank=True, null=True
    )
    country = models.ManyToManyField(
        Nonhuman,
        related_name="country",
    )
    continent = models.ManyToManyField(
        Nonhuman,
        related_name="continent",
    )


class Lifedate(models.Model):
    class Types(models.TextChoices):
        BIRTH = "b", "birth"
        DEATH = "d", "death"

    class Calendars(models.TextChoices):
        JULIAN = "Q1985786", "Julian"
        GREGORIAN = "Q1985727", "Gregorian"

    type = models.CharField(max_length=1, choices=Types.choices)
    year = models.SmallIntegerField(blank=True, null=True)
    month = models.PositiveSmallIntegerField(blank=True, null=True)
    day = models.PositiveSmallIntegerField(blank=True, null=True)
    precision = models.PositiveSmallIntegerField(blank=True, null=False)
    calendar = models.CharField(max_length=8, choices=Calendars.choices)

    class Meta:
        unique_together = ["type", "year", "month", "day", "precision", "calendar"]


class Wikipedia(models.Model):
    class Grades(models.TextChoices):
        FEATURED = "f", "Featured"
        GOOD = "g", "Good"
        UNGRADED = "u", "Ungraded"

    title = models.SlugField(primary_key=True, max_length=200)
    pagesize = models.PositiveIntegerField(blank=True, null=True)
    recentviews = models.PositiveIntegerField(blank=True, null=True)
    grade = models.CharField(max_length=1, choices=Grades.choices)
    editcount = models.PositiveIntegerField(blank=True, null=True)
    recentedits = models.PositiveIntegerField(blank=True, null=True)
    connections = models.ManyToManyField("self")


class Wikidata(models.Model):
    human = models.OneToOneField(Human, on_delete=models.CASCADE, primary_key=True)
    label = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    birthdate = models.ManyToManyField(Lifedate, related_name="birthdate")
    deathdate = models.ManyToManyField(Lifedate, related_name="deathdate")
    gender = models.ManyToManyField(Nonhuman, related_name="gender")
    citizenship = models.ManyToManyField(Nonhuman, related_name="citizenship")
    ethnicity = models.ManyToManyField(Nonhuman, related_name="ethnicity")
    religion = models.ManyToManyField(Nonhuman, related_name="religion")
    occupation = models.ManyToManyField(Nonhuman, related_name="occupation")
    position = models.ManyToManyField(Nonhuman, related_name="position")
    birthplace = models.ManyToManyField(Nonhuman, related_name="birthplace")
    deathplace = models.ManyToManyField(Nonhuman, related_name="deathplace")
    burialplace = models.ManyToManyField(Nonhuman, related_name="burialplace")
    education = models.ManyToManyField(Nonhuman, related_name="education")
    degree = models.ManyToManyField(Nonhuman, related_name="degree")
    field = models.ManyToManyField(Nonhuman, related_name="field")
    political_party = models.ManyToManyField(Nonhuman, related_name="political_party")
    membership = models.ManyToManyField(Nonhuman, related_name="membership")
    handedness = models.ManyToManyField(Nonhuman, related_name="handedness")
    twitterfollowers = models.PositiveIntegerField(null=True, blank=True)
    twitterid = models.PositiveBigIntegerField(null=True, blank=True)
    wikipedia = models.OneToOneField(Wikipedia, on_delete=models.CASCADE, null=True)
