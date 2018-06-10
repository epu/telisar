"""
Primitives for the Telisaran reckoning of dates and time.
"""
from abc import ABC, abstractmethod


class InvalidEraError(Exception):
    pass


class InvalidYearError(Exception):
    pass


class InvalidSeasonError(Exception):
    pass


class InvalidSpanError(Exception):
    pass


class InvalidDayError(Exception):
    pass


class InvalidHourError(Exception):
    pass


class InvalidMinuteError(Exception):
    pass


class InvalidDateError(Exception):
    pass


class MissingSeasonError(Exception):
    pass


def _suffix(n):
    if n == 1:
        return 'st'
    elif n == 2:
        return 'nd'
    elif n == 3:
        return 'rd'
    else:
        return 'th'


class DateObject(ABC):
    """
    Base class for all date components. This ABC implements basic arithmetic operator support for
    all DateObjects as integer seconds since the beginning of time. If the current instance has a
    from_seconds() method, it will be called with the result of the calculation, otherwise the
    integer seconds will be returned.

    Subclasseres must define the number, as_seconds and length_in_seconds attributes.

    Attribtues:
        number (int): The numeric index of the object in its parent group
        as_seconds (int): The component object expressed as seconds since the beginning of time.
        length_in_seconds (int): The number of seconds in a single object.
    """

    @property
    @abstractmethod
    def number(self):
        pass

    @property
    def as_seconds(self):
        return (self.number - 1) * self.length_in_seconds

    def length_in_seconds(self):
        raise NotImplementedError("Please define the length_in_seconds class attribute.")

    def __str__(self):
        return str(self.number)

    def __repr__(self):
        return str(self)

    def __int__(self):
        return self.as_seconds

    def __eq__(self, other):
        return int(self) == int(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        val = int(self) + int(other)
        if hasattr(self.__class__, 'from_seconds'):
            return self.__class__.from_seconds(val)
        else:
            return val

    def __sub__(self, other):
        val = int(self) - int(other)
        if hasattr(self.__class__, 'from_seconds'):
            return self.__class__.from_seconds(val)
        else:
            return val


class datetime(DateObject):
    """
    A date and time on the Telisaran calendar.

    Attributes:
        era (Era): The era component of the date
        year (Year): The year component of the date
        season (Season): The season component of the date
        day (Day): The day component of the date
        hour (Hour): The hour component of the time
        minute (Minute): The minute component of the time
        second (int): The seconds component of the time
        long (str): The long representation of the date and time
        short (str): The short representation of the date and time
        numeric (str): The dotted numeric representation of the date and time
        date (str): The shorthand representation of the day and date
        time_long (str): The long form of the time, including names of hours
        time_short (str): The short form of the time
        time (str): Alias of time_short
        as_seconds (int): The date and time expressed in seconds since the beginning of time
        number (int): alias for as_seconds
    """

    def __init__(self, era=1, year=1, season=1, day=1, hour=0, minute=0, second=0):
        """
        Args:
            year (int): The year
            season (int): The season, 1-8
            day (int): The day, 1-45
            era (int): The era, 1-3
        """
        self.era = Era(era)
        self.year = Year(year, era=self.era)
        if season == Year.length_in_seasons + 1:
            self.season = FestivalOfTheHunt(year)
        else:
            self.season = Season(season_of_year=season, year=self.year.year)
        self.day = Day(day, season=self.season)
        self.hour = Hour(hour)
        self.minute = Minute(hour)

        if second < 0 or second > 59:
            raise InvalidDateError("second {} must be between 0 and 59")
        self.second = second

    @property
    def long(self):

        if self.season.number == 9:
            template = ("{time} on {day_name}, the {day}{day_suffix} day of the {season}, "
                        "in the year {year} of the {era}")
        else:
            template = ("{time} on {day_name}, the {day}{day_suffix} day of the {season} "
                        "(the {span_day}{span_day_suffix} day of the {span}{span_suffix} span) "
                        "in the year {year} of the {era}")
        return template.format(
            time=self.time_long,
            day_name=self.day.name,
            day=self.day.day_of_season,
            day_suffix=_suffix(self.day.day_of_season),
            season=self.season,
            span_day=self.day.day_of_span,
            span_day_suffix=_suffix(self.day.day_of_span),
            span=self.day.span,
            span_suffix=_suffix(self.day.span),
            year=self.year,
            era=self.era.long
        )

    @property
    def numeric(self):
        return (
            "{0.era.number}.{0.year.number}.{0.season.number}."
            "{0.day.day_of_season:02d}."
            "{0.hour.number:02d}.{0.minute.number:02d}.{0.second:02d}"
        ).format(self)

    @property
    def date(self):
        if self.season.number == 9:
            season = 'H'
        else:
            season = self.season.name[0].upper()

        return "{name}{date}{season}".format(
            name=self.day.name[0].upper(),
            date=self.day.day_of_season,
            season=season,
        )

    @property
    def time_long(self):
        return "{minute}{hour}".format(
            minute="{} past ".format(self.minute) if self.minute != 0 else '',
            hour=self.hour.name
        )

    @property
    def time(self):
        return "{0.hour.number:02d}:{0.minute.number:02d}:{0.second:02d}".format(self)

    @property
    def time_short(self):
        return "{name}, {day}{suffix} of the {season}, {year} {era} {time}".format(
            name=self.day.name,
            day=self.day.day_of_season,
            suffix=_suffix(self.day.day_of_season),
            season=self.season.name,
            year=self.year,
            era=self.era.short,
            time=self.time
        )

    @property
    def short(self):
        return self.time_short

    @property
    def as_seconds(self):
        return sum(map(int, [self.era, self.year, self.season, self.day]))

    @property
    def number(self):
        return self.as_seconds

    def __repr__(self):
        return (
            "<Date: year={0.year}, season={0.season.season_of_year}, day={0.day.day_of_season}, "
            "span={0.day.span}, era={0.era}, hour={0.hour}, minute={0.minute}, second={0.second}>:"
            " {0.short}".format(self)
        )

    @classmethod
    def from_seconds(cls, seconds):
        """
        Return a datetime object corresponding to the given number of seconds since the beginning.
        """
        era = int(seconds / Era.length_in_seconds)
        e_sec = era * Era.length_in_seconds

        year = int((seconds - e_sec) / Year.length_in_seconds)
        y_sec = year * Year.length_in_seconds

        season = int((seconds - e_sec - y_sec) / Season.length_in_seconds)
        s_sec = season * Season.length_in_seconds

        day = int((seconds - e_sec - y_sec - s_sec) / Day.length_in_seconds)
        d_sec = day * Day.length_in_seconds

        hour = int((seconds - e_sec - y_sec - s_sec - d_sec) / Hour.length_in_seconds)
        h_sec = hour * Hour.length_in_seconds

        minute = int((seconds - e_sec - y_sec - s_sec - d_sec - h_sec) / Minute.length_in_seconds)
        m_sec = minute * Minute.length_in_seconds

        seconds = seconds - e_sec - y_sec - s_sec - d_sec - h_sec - m_sec

        return cls(
            era=era + 1,
            year=year + 1,
            season=season + 1,
            day=day + 1,
            hour=hour,
            minute=minute,
            second=seconds
        )


class Minute(DateObject):
    """
    A representation of one minute on the Telisaran clock.

    Class Attributes:
        length_in_seconds (int): The length of an hour in seconds

    Attributes:
        minute (int): The minute of the hour (0-59)
        number (int): alias for minute
    """
    length_in_seconds = 60

    def __init__(self, minute):
        if minute < 0 or minute > 59:
            raise InvalidHourError("minute {} must be between 0 and 59")
        self.minute = minute

    @property
    def as_seconds(self):
        return self.number * Minute.length_in_seconds

    @property
    def number(self):
        return self.minute


class Hour(DateObject):
    """
    A representation of one hour on the Telisaran clock.

    Class Attributes:
        length_in_seconds (int): The length of an hour in seconds

    Instance Attributes:
        hour (int): The hour of the day (0-23)
        number (int): alias for hour
    """
    length_in_seconds = 60 * Minute.length_in_seconds

    names = {
        '0': "Black Hour",
        '6': "Soul's Hour",
        '12': "Sun's Hour",
        '18': "Grey Hour",
    }

    def __init__(self, hour):
        if hour < 0 or hour > 23:
            raise InvalidHourError("hour {} must be between 0 and 23")
        self.hour = hour

    @property
    def as_seconds(self):
        return self.number * Hour.length_in_seconds

    @property
    def number(self):
        return self.hour

    @property
    def name(self):
        if str(self) in Hour.names:
            return Hour.names[str(self)]
        else:
            return "{}{} hour".format(str(self), _suffix(int(self)))


class Day(DateObject):
    """
    A representation of one day on the Telisaran calendar.

    Class Attributes:
        length_in_seconds (int): The length of a day in seconds
        names (list): The names of the days

    Instance Attributes:
        day_of_season (int): The day of the season (1 - 45)
        day_of_span (int): The day of the span  (
        name (str): The name of the day
        season (Season): The Season in which this day occurs
        span (int): The span of the season in which this day falls (1 - 9)
    """
    length_in_seconds = 24 * Hour.length_in_seconds

    names = ['Syfdag', 'Mimdag', 'Wodag', 'Thordag', 'Freydag']

    def __init__(self, day_of_season, season=None):
        """
        Create a Day instance.

        Args:
            day_of_season (int): The day of the season between 1 and 45.
            season (Season): optional, specify a Season instance for this day.
        """
        if day_of_season < 1 or day_of_season > Season.length_in_days:
            raise InvalidDayError("{}: day_of_season must be between 1 and {}".format(
                day_of_season, Season.length_in_days))

        self.day_of_season = day_of_season
        self.season = season

    @property
    def number(self):
        return self.day_of_season

    @property
    def span(self):
        return int((self.day_of_season - 1) / Span.length_in_days) + 1

    @property
    def day_of_span(self):
        return (self.day_of_season - 1) % Span.length_in_days + 1

    @property
    def name(self):
        if self.season.number == 9:
            return self.season.day_names[self.day_of_span - 1]
        else:
            return Day.names[self.day_of_span - 1]

    def as_date(self):
        """
        Return a new Date object representing this day. The instance must have a season attribute.
        """
        try:
            return datetime(year=int(self.season.year), season=int(self.season), day=int(self))
        except AttributeError:
            raise MissingSeasonError("You must assign a season to this Day instance.")

    def __repr__(self):
        return self.name


class Span(DateObject):
    """
    A span (week) of days in a Season.

    Class Attributes:
        length_in_days (int): The number of days in a span.
    """
    length_in_days = len(Day.names)
    length_in_seconds = length_in_days * Day.length_in_seconds

    @property
    def number(self):
        return 1


class Season(DateObject):
    """
    A season (month) of days in a Telisaran year.

    Class Attributes:
        names (list): The names of the seasons
        length_in_spans (int): The number of spans in a season
        length_in_days (int): The number of days in a season

    Instance Attributes:
        name (str): The name of the season
        season_of_year (int): The season of the year, between 1 and 8.
        days (list): A list of Day objects for every day in the season
        year (int): The year in which this season falls.
    """
    names = ['Fox', 'Owl', 'Wolf', 'Eagle', 'Shark', 'Lion', 'Raven', 'Bear']
    length_in_spans = 9
    length_in_days = length_in_spans * Span.length_in_days
    length_in_seconds = length_in_days * Day.length_in_seconds

    def __init__(self, season_of_year, year):
        if season_of_year == len(Season.names) + 1:
            return FestivalOfTheHunt(year)
        elif season_of_year < 1 or season_of_year > len(Season.names):
            raise InvalidSeasonError("season_of_year {} must be between 1 and {}".format(
                season_of_year, len(Season.names)))
        self.season_of_year = season_of_year
        self.year = year

        self._days = []

    @property
    def number(self):
        return self.season_of_year

    @property
    def days(self):
        if not self._days:
            for i in range(1, Season.length_in_days + 1):
                self._days.append(Day(i, season=self))
        return self._days

    @property
    def name(self):
        return Season.names[self.season_of_year - 1]

    def __int__(self):
        return (self.season_of_year - 1) * self.length_in_seconds

    def __str__(self):
        return "Season of the {}".format(self.name)


class FestivalOfTheHunt(Season):
    """
    The 9th season, which only has 5 days, occurring at the end of each year.

    Class Attributes:
        day_names (list): The names of the days in this season
        length_in_spans (int): the length of the festival in spans
        length_in_days (int): The length of the festival in days
        length_in_seconds (int): The length of the festival in seconds

    Instance Attributes:
        season_of_year (int): The season of the year (9)
        days (list): A list of Day objects for every day in the season
        name (str): The name of this special season
        year (Year): The year in which this festival falls
    """
    day_names = [
        "Syf's Hunt",
        "Mimir's Hunt",
        "Woden's Hunt",
        "Thorus's Hunt",
        "Freya's Hunt"
    ]
    length_in_spans = 1
    length_in_days = 5
    length_in_seconds = length_in_days * Day.length_in_seconds

    def __init__(self, year):
        self.season_of_year = 9
        self.year = year
        self._days = []

    @property
    def name(self):
        return "Festival Of The Hunt"

    def __str__(self):
        return "the {}".format(self.name)


class Year(DateObject):
    """
    A year on the Telisaran calendar.

    Class Attributes:
        length_in_seasons (int): The length of a year in seasons
        length_in_spans (int): The length of a year in spans
        length_in_days (int): The length of a year in days
        length_in_seconds (int): The length of a year in seconds

    Instance Attributes:
        era (Era): The era
        year (Year): The year
        seasons (list): The seasons in the year
        number (int): Alias of year
    """

    # precompute some length properties. Note that every year has one extra span, the Festival Of
    # The Hunt, which falls between the last span of the Bear and the first span of the Fox.
    length_in_seasons = len(Season.names)
    length_in_spans = (length_in_seasons * Season.length_in_spans) + 1
    length_in_days = length_in_spans * Span.length_in_days
    length_in_seconds = length_in_days * Day.length_in_seconds

    def __init__(self, year, era):
        """
        Instantiate a Year object

        Args:
            year (int): The year of the era.
            era (int): The era
        """
        self.era = era
        if year < 1:
            raise InvalidYearError("Years must be greater than 1.")
        if self.era.end and year > self.era.end:
            raise InvalidYearError("The {} ended in {}".format(self.era.name, self.era.end))
        self.year = year
        self.seasons = [Season(i, self) for i in range(1, Year.length_in_seasons + 1)]
        self.seasons.append(FestivalOfTheHunt(self))

    @property
    def number(self):
        return self.year


class Era(DateObject):
    """
    An age of years, by Telisaran reckoning.

    Class Attributes:
        long_names (list): The long names of the eras
        shot_names (list): The abbreviated names of the eras
        lenth_in_seconds (int): The length of an era, in seconds

    Instance Attributes:
        era (int): The number of the era (1-3)
        end (int): The last year of the era
        short (str): The short name of this era
        long (str): The long name of this era
        number (int): Alias for era

    """
    long_names = ['Ancient Era', 'Old Era', 'Modern Era']
    short_names = ['AE', 'OE', 'ME']

    length_in_seconds = 10000 * Year.length_in_seconds

    def __init__(self, era, end=None):
        """
        Args:
            era (int): The number of the era; must be between 1 and 3.
            end (year): The last year of the era
        """
        if era < 1 or era > len(Era.long_names) + 1:
            raise InvalidEraError("Eras must be between 0 and {}".format(len(Era.long_names)))
        self.era = era
        self.end = end

    @property
    def short(self):
        return Era.short_names[self.era - 1]

    @property
    def long(self):
        return Era.long_names[self.era - 1]

    @property
    def number(self):
        return self.era

    def __repr__(self):
        return self.long


eras = [
    Era(1, end=20000),
    Era(2, end=10000),
    Era(3, end=None)
]