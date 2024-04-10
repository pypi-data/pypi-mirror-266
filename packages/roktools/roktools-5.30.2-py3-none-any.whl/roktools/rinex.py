import argparse
from abc import ABC, abstractmethod
from dataclasses import dataclass
import datetime
import enum
import math
import pandas as pd
import re
from typing import List, Tuple, Union, IO
import sys

from . import logger
from . import time
from .constants import SPEED_OF_LIGHT, EARTH_GRAVITATION_PARAM_MU
from .file import process_filename_or_file_handler, skip_lines
from .gnss.types import ConstellationId, Band, TrackingChannel, Satellite

from .tle import TLE, read_celestrak, get_constellation_from_label


RINEX_LINE_SYS_OBS_TYPES = "SYS / # / OBS TYPES"

RINEX_BAND_MAP = {
    ConstellationId.GPS: {
        '1': Band.L1,
        '2': Band.L2,
        '5': Band.L5
    },
    ConstellationId.GLONASS: {
        '1': Band.G1,
        '4': Band.G1a,
        '2': Band.G2,
        '6': Band.G2a,
        '3': Band.G3
    },
    ConstellationId.GALILEO: {
        '1': Band.E1,
        '5': Band.E5a,
        '7': Band.E5b,
        '8': Band.E5,
        '6': Band.E6
    },
    ConstellationId.BEIDOU: {
        '2': Band.B1_2,
        '1': Band.B1,
        '5': Band.B2a,
        '7': Band.B2b,
        '8': Band.B2,
        '6': Band.B3
    },
    ConstellationId.QZSS: {
        '1': Band.L1,
        '2': Band.L2,
        '5': Band.L5,
        '6': Band.L6
    },
    ConstellationId.IRNSS: {
        '5': Band.L5,
        '9': Band.S
    },
    ConstellationId.SBAS: {
        '1': Band.L1,
        '5': Band.L5
    }
}

class RinexSatIdProvider(ABC):
    """
    This abstract class provides an interface to provide the RINEX Satellite ID and constellation
    """
    @abstractmethod
    def get_constellation_letter(self) -> str:
        pass

    def get_sat_number(self, norad_id) -> int:
        return norad_id


class RinexSatIdFactory:
    @staticmethod
    def create(constellation: ConstellationId) -> RinexSatIdProvider:
        if constellation == ConstellationId.STARLINK:
            return StarlinkRNXId()
        elif constellation == ConstellationId.SPIRE:
            return SpireRNXId()
        elif constellation == ConstellationId.ONEWEB:
            return OneWebRNXId()
        else:
            raise ValueError("Invalid constellation")

class StarlinkRNXId(RinexSatIdProvider):
    def get_constellation_letter(self) -> str:
        return ConstellationId.STARLINK.value

class SpireRNXId(RinexSatIdProvider):
    def get_constellation_letter(self) -> str:
        return ConstellationId.SPIRE.value

class OneWebRNXId(RinexSatIdProvider):
    def get_constellation_letter(self) -> str:
        return ConstellationId.ONEWEB.value

@dataclass
class ObservableType(object):
    type: str
    channel: TrackingChannel

    @staticmethod
    def from_string(observable_type: str) -> 'ObservableType':
        return ObservableType(observable_type[0], TrackingChannel.from_rinex3_code(observable_type))

    def __repr__(self):
        return f'{self.type:1s}{self.channel}'


@dataclass
class ObservableValue(object):
    value: float
    lli: int
    snr: int

@dataclass
class Clock(object):
    bias_s:float
    drift_s_per_s:float
    drift_rate_s_per_s2:float

@dataclass
class Record(object):
    epoch: datetime.datetime
    sat: Satellite
    channel: TrackingChannel
    range: float
    phase: float
    doppler: float
    snr: float
    flags: str
    slip: int

    def set_value(self, observable_type: ObservableType, observable_value: ObservableValue) -> None:

        if observable_type.type == 'C':
            self.range = observable_value.value
        elif observable_type.type == 'L':
            self.phase = observable_value.value
        elif observable_type.type == 'D':
            self.doppler = observable_value.value
        elif observable_type.type == 'S':
            self.snr = observable_value.value
        else:
            raise TypeError(f'Unrecognise observable type {observable_type.type}')

        if observable_value.lli != 0:
            self.slip = 1
            self.flags = '00000100'

    def aslist(self) -> list:

        return [self.epoch, self.sat.constellation, self.sat, str(self.channel),
                f'{self.sat}{self.channel}', self.range, self.phase, self.doppler, self.snr, self.flags, self.slip]

    @staticmethod
    def get_list_fieldnames() -> List[str]:
        return ["epoch", "constellation", "sat", "channel", "signal", "range", "phase", "doppler", "snr", "flag", "slip"]


class EpochFlag(enum.Enum):

    OK = 0
    POWER_FAILURE = 1
    MOVING_ANTENNA = 2
    NEW_SITE = 3
    HEADER_INFO = 4
    EXTERNAL_EVENT = 5

    @staticmethod
    def get_from_line(line: str) -> 'EpochFlag':
        """
        Extract the epoch flag from the incoming line

        >>> EpochFlag.get_from_line(">                              4 95")
        <EpochFlag.HEADER_INFO: 4>
        >>> EpochFlag.get_from_line("> 2023 08 03 12 00  8.0000000  0 38")
        <EpochFlag.OK: 0>
        >>> EpochFlag.get_from_line(None)
        Traceback (most recent call last):
        ...
        ValueError: The line [ None ] does not have an Epoch Flag
        >>> EpochFlag.get_from_line("")
        Traceback (most recent call last):
        ...
        ValueError: The line [  ] does not have an Epoch Flag
        >>> EpochFlag.get_from_line("> 2023 08 03 1")
        Traceback (most recent call last):
        ...
        ValueError: The line [ > 2023 08 03 1 ] does not have an Epoch Flag
        """

        INDEX = 31

        if line and len(line) >= INDEX + 1 and line[0] == '>':
            epoch_flag = int(line[INDEX])
            return EpochFlag(epoch_flag)

        raise ValueError(f'The line [ {line} ] does not have an Epoch Flag')


class FilePeriod(enum.Enum):

    DAILY = 86400
    HOURLY = 3600
    QUARTERLY = 900
    UNDEFINED = 0

    @staticmethod
    def from_string(string):
        """
        Get the FilePeriod from a string

        >>> FilePeriod.from_string('daily')
        <FilePeriod.DAILY: 86400>

        >>> FilePeriod.from_string('DAILY')
        <FilePeriod.DAILY: 86400>
        """

        if (string.lower() == 'daily'):
            return FilePeriod.DAILY
        elif (string.lower() == 'quarterly'):
            return FilePeriod.QUARTERLY
        elif (string.lower() == 'hourly'):
            return FilePeriod.HOURLY
        else:
            return FilePeriod.UNDEFINED

    @staticmethod
    def list():
        """ Return a list of the available valid periodicities """
        return list([v.name for v in FilePeriod if v.value > 0])

    def build_rinex3_epoch(self, epoch):
        """
        Construct a Rinex-3-like epoch string

        >>> epoch = datetime.datetime(2020, 5, 8, 9, 29, 20)
        >>> FilePeriod.QUARTERLY.build_rinex3_epoch(epoch)
        '20201290915_15M'

        >>> FilePeriod.HOURLY.build_rinex3_epoch(epoch)
        '20201290900_01H'

        >>> FilePeriod.DAILY.build_rinex3_epoch(epoch)
        '20201290000_01D'
        """

        hour = epoch.hour if self != FilePeriod.DAILY else 0

        day_seconds = (epoch - epoch.combine(epoch, datetime.time())).total_seconds()

        minute = get_quarter_str(day_seconds) if self == FilePeriod.QUARTERLY else 0

        date_str = epoch.strftime('%Y%j')

        return '{}{:02d}{:02d}_{}'.format(date_str, hour, minute, self)

    def __str__(self):

        if self.value == FilePeriod.DAILY.value:
            return '01D'
        elif self.value == FilePeriod.QUARTERLY.value:
            return '15M'
        elif self.value == FilePeriod.HOURLY.value:
            return '01H'
        else:
            raise ValueError('Undefined FilePeriod value')


# ------------------------------------------------------------------------------

def strftime(epoch, fmt):
    """

    >>> epoch = datetime.datetime(2019, 8, 3, 10, 10, 10)
    >>> strftime(epoch, "ebre215${rinexhour}${rinexquarter}.19o")
    'ebre215k00.19o'

    >>> epoch = datetime.datetime(2019, 8, 3, 10, 50, 10)
    >>> strftime(epoch, "ebre215${RINEXHOUR}${rinexQUARTER}.19o")
    'ebre215k45.19o'

    >>> epoch = datetime.datetime(2019, 8, 3, 0, 0, 0)
    >>> strftime(epoch, "ebre215${rinexhour}${rinexquarter}.19o")
    'ebre215a00.19o'

    >>> epoch = datetime.datetime(2019, 8, 3, 23, 50, 10)
    >>> strftime(epoch, "ebre215${rinexhour}${rinexquarter}.19o")
    'ebre215x45.19o'
    """

    RINEX_HOUR = "abcdefghijklmnopqrstuvwxyz"

    PATTERN_HOUR = re.compile(r"\$\{rinexhour\}", re.IGNORECASE)
    PATTERN_QUARTER = re.compile(r"\$\{rinexquarter\}", re.IGNORECASE)

    hour = RINEX_HOUR[epoch.hour]
    quarter = get_quarter_str(epoch.minute * 60 + epoch.second)

    fmt = PATTERN_HOUR.sub(f"{hour}", fmt)
    fmt = PATTERN_QUARTER.sub(f"{quarter:02d}", fmt)

    return fmt


def get_quarter_str(seconds):
    """
    Get the Rinex quarter string ("00", "15", "30", "45") for a given number of seconds

    >>> get_quarter_str(100)
    0
    >>> get_quarter_str(920)
    15
    >>> get_quarter_str(1800)
    30
    >>> get_quarter_str(2900)
    45
    >>> get_quarter_str(3600 + 900)
    15
    """

    mod_seconds = seconds % 3600

    if mod_seconds < 900:
        return 0
    elif mod_seconds < 1800:
        return 15
    elif mod_seconds < 2700:
        return 30
    else:
        return 45


def parse_obs_line(line: str, n_obs: int) -> Tuple[Satellite, List[ObservableValue]]:
    """

    >>> line = "C05  40058862.469 6 208597044.05206  40058858.572 7 161300483.44407  40058861.947 7 169502210.29507"
    >>> parse_obs_line(line, 6)
    (C05, [ObservableValue(value=40058862.469, lli=0, snr=6), \
ObservableValue(value=208597044.052, lli=0, snr=6), \
ObservableValue(value=40058858.572, lli=0, snr=7), \
ObservableValue(value=161300483.444, lli=0, snr=7), \
ObservableValue(value=40058861.947, lli=0, snr=7), \
ObservableValue(value=169502210.295, lli=0, snr=7)])
    """

    satellite = Satellite.from_string(line[0:3])

    observable_values = []

    offset = 3
    for i_obs in range(n_obs):
        start = offset + i_obs * 16
        obs_str = line[start:start + 14]
        lli_str = line[start + 14:start + 14 + 1]
        snr_str = line[start + 15:start + 15 + 1]

        obs = float(obs_str) if obs_str and obs_str != '              ' and obs_str != '\n' else math.nan
        lli = int(lli_str) if lli_str and lli_str != ' ' and lli_str != '\n' else 0
        snr = int(snr_str) if snr_str and snr_str != ' ' and snr_str != '\n' else 0

        observable_values.append(ObservableValue(obs, lli, snr))

    return satellite, observable_values


def get_channels(observables: List[ObservableType]) -> List[TrackingChannel]:
    """
    Get the channel list from a list of observables

    >>> C1C = ObservableType.from_string("C1C")
    >>> L1C = ObservableType.from_string("L1C")
    >>> C1W = ObservableType.from_string("C1W")
    >>> C2W = ObservableType.from_string("C2W")
    >>> L2W = ObservableType.from_string("L2W")
    >>> C2L = ObservableType.from_string("C2L")
    >>> L2L = ObservableType.from_string("L2L")
    >>> C5Q = ObservableType.from_string("C5Q")
    >>> L5Q = ObservableType.from_string("L5Q")
    >>> get_channels([C1C, L1C, C1W, C2W, L2W, C2L, L2L, C5Q, L5Q])
    [1C, 1W, 2W, 2L, 5Q]
    """

    res = []
    for observable in observables:
        channel = observable.channel

        if channel not in res:
            res.append(channel)

    return res


def get_obs_mapping(lines: List[str]) -> dict:
    """
    Get the observable mappings for a constellation

    >>> line = "G    9 C1C L1C C1W C2W L2W C2L L2L C5Q L5Q                  SYS / # / OBS TYPES"
    >>> get_obs_mapping([line])
    {'G': [C1C, L1C, C1W, C2W, L2W, C2L, L2L, C5Q, L5Q]}

    >>> lines = ["G   20 C1C L1C D1C S1C C1W L1W D1W S1W C2W L2W D2W S2W C2L  SYS / # / OBS TYPES", \
                 "       L2L D2L S2L C5Q L5Q D5Q S5Q                          SYS / # / OBS TYPES"]
    >>> get_obs_mapping(lines)
    {'G': [C1C, L1C, D1C, S1C, C1W, L1W, D1W, S1W, C2W, L2W, D2W, S2W, C2L, L2L, D2L, S2L, C5Q, L5Q, D5Q, S5Q]}
    """

    constellation = None
    values = None

    for line in lines:

        constellation_letter = line[0] if line[0] != ' ' else None
        values_partial = [ObservableType.from_string(s) for s in line[6:60].split()]

        if constellation_letter:
            constellation = constellation_letter
            values = values_partial

        else:
            values.extend(values_partial)

    return {constellation: values}


def parse_rnx3_epoch(line):
    """
    Parse a measurement epoch from a Rinex3 and return a tuple
    with the epochm event type and number of lines

    >>> parse_rnx3_epoch("> 2017 08 03 11 22 30.1234000  0 29")
    (datetime.datetime(2017, 8, 3, 11, 22, 30, 123400), 0, 29)

    >>> parse_rnx3_epoch("> 2021  2  5 15 51 30.2000000 0 22")
    (datetime.datetime(2021, 2, 5, 15, 51, 30, 200000), 0, 22)

    >>> parse_rnx3_epoch("> 2020 11 18 21 43 30.0000000  0 28       0.000000000000")
    (datetime.datetime(2020, 11, 18, 21, 43, 30), 0, 28)

    >>> parse_rnx3_epoch("> 2019 07 02 13 25  5.9999995  0 31")
    (datetime.datetime(2019, 7, 2, 13, 25, 5, 999999), 0, 31)
    """

    try:
        _, year, month, day, hour, minute, seconds, epoch_flag, n_lines, *b = line.split()
    except ValueError as e:
        raise ValueError(f"Invalid Rinex 3 epoch line [ {line} ]: {e}")

    seconds, microseconds, *b = seconds.split('.')

    t = datetime.datetime(int(year), int(month), int(day),
                          hour=int(hour), minute=int(minute), second=int(seconds),
                          microsecond=int(microseconds[0:6]))

    return t, int(epoch_flag), int(n_lines)


def to_dataframe(rinex_file: str) -> pd.DataFrame:

    with open(rinex_file, 'r') as file:

        constellation_observables = {}
        records = []

        # Header parsing
        for line in file:

            if "END OF HEADER" in line:
                break

            if RINEX_LINE_SYS_OBS_TYPES in line:
                lines = [line]

                n_observables = int(line[1:6])
                n_extra_lines = (n_observables - 1) // 13 if n_observables > 13 else 0
                for _ in range(n_extra_lines):
                    lines.append(next(file))

                constellation_observables.update(get_obs_mapping(lines))

        # Body parsing
        for line in file:

            epoch_flag = EpochFlag.get_from_line(line)

            if epoch_flag == EpochFlag.OK:

                epoch, _, n_lines = parse_rnx3_epoch(line)

                for _ in range(n_lines):

                    line = next(file)

                    constellation = line[0]

                    observable_types = constellation_observables.get(constellation, None)
                    if observable_types is None:
                        continue

                    n_obs = len(observable_types)
                    channels = get_channels(observable_types)
                    satellite, observable_values = parse_obs_line(line, n_obs)

                    epoch_records = [
                        Record(epoch, satellite, channel, math.nan, math.nan, math.nan, math.nan, '00000000', 0)
                        for channel in channels]

                    # Create a dictionary with channels as keys and records as values
                    epoch_records_dict = {record.channel: record for record in epoch_records}

                    for observable_type, observable_value in zip(observable_types, observable_values):

                        record = epoch_records_dict.get(observable_type.channel, None)
                        if record is not None:
                            record.set_value(observable_type, observable_value)

                    records.extend(epoch_records)

            else:
                n_lines_to_skip = int(line[33:])
                for _ in range(n_lines_to_skip):
                    line = next(file)

        dataframe = pd.DataFrame([record.aslist() for record in records], columns=Record.get_list_fieldnames())

        return dataframe


class Obs:

    def __init__(self, filename: str):
        self.filename = filename
        self.data = to_dataframe(self.filename)
        timetags = sorted(set([ts.to_pydatetime() for ts in self.data['epoch']]))
        if len(timetags) > 1:
            self.interval = time.get_interval(timetags)

    def compute_detrended_code_minus_carrier(self) -> pd.DataFrame:
        self.count_cycle_slips()

        grouped_data = self.data.groupby(['channel', 'sat', 'slipc'], group_keys=False)
        self.data = grouped_data.apply(lambda df: self.__compute_grouped_detrended_cmc(df))

    def count_cycle_slips(self):
        grouped_data = self.data.groupby(['channel', 'sat'])
        self.data['slipc'] = grouped_data['slip'].transform(lambda slip: slip.cumsum())

    def __compute_grouped_detrended_cmc(self, grouped_df):
        # grouped_df is rinex_obs.data grouped by 'channel', 'sat' and 'slipc'
        const = grouped_df['constellation'].iloc[0]
        constellation_id = ConstellationId.from_string(const)

        chan = grouped_df['channel'].iloc[0]
        band_frequency = RINEX_BAND_MAP[constellation_id][chan[0]]
        wavelength = SPEED_OF_LIGHT / band_frequency

        cmc = grouped_df['range'] - grouped_df['phase'] * wavelength

        CMC_ROLL_WINDOW_SAMPLES = 600 / self.interval
        if len(cmc) >= CMC_ROLL_WINDOW_SAMPLES:
            trend = cmc.rolling(20).median()
        else:
            trend = cmc.mean()

        grouped_df['cmc_detrended'] = cmc - trend

        return grouped_df

@dataclass
class RawNavBlock(object):
    satellite: Satellite
    epoch: datetime.datetime
    lines: List[str]

    def __repr__(self):
        return '\n'.join(self.lines)

    def __lt__(self, other):

        if self.epoch != other.epoch:
            return self.epoch < other.epoch

        elif self.satellite.constellation != other.satellite.constellation:
            return self.satellite.constellation < other.satellite.constellation

        return self.satellite.prn < other.satellite.prn


class Nav(object):
    """
    Class that holds Rinex Navigation data
    """

    RINEX4_EPH_BLOCK_LINES_LEO = 6

    RINEX4_EPH_BLOCK_LINES = {
        f'{ConstellationId.GPS.value} LNAV' : 8,
        f'{ConstellationId.GPS.value} CNAV' : 9,
        f'{ConstellationId.GPS.value} CNV2' : 10,
        f'{ConstellationId.GALILEO.value} INAV' : 8,
        f'{ConstellationId.GALILEO.value} FNAV' : 8,
        f'{ConstellationId.GLONASS.value} FDMA' : 5,
        f'{ConstellationId.QZSS.value} LNAV' : 8,
        f'{ConstellationId.QZSS.value} CNAV' : 9,
        f'{ConstellationId.QZSS.value} CNV2' : 10,
        f'{ConstellationId.BEIDOU.value} D1' : 8,
        f'{ConstellationId.BEIDOU.value} D2' : 8,
        f'{ConstellationId.BEIDOU.value} CNV1' : 10,
        f'{ConstellationId.BEIDOU.value} CNV2' : 10,
        f'{ConstellationId.BEIDOU.value} CNV3' : 9,
        f'{ConstellationId.SBAS.value} SBAS' : 4,
        f'{ConstellationId.IRNSS.value} LNAV' : 8,
        f'{ConstellationId.SPIRE.value}' : RINEX4_EPH_BLOCK_LINES_LEO,
        f'{ConstellationId.STARLINK.value}' : RINEX4_EPH_BLOCK_LINES_LEO,
        f'{ConstellationId.ONEWEB.value}' : RINEX4_EPH_BLOCK_LINES_LEO,
    }

    def __init__(self, file: Union[str,IO]):
        self.blocks = Nav._load(file)

    @staticmethod
    @process_filename_or_file_handler('r')
    def _load(fh:IO) -> List['Nav']:
        """
        Load from a stream of data
        """

        blocks = []

        # header
        line = fh.readline()

        if not line.startswith('     4'):
            raise ValueError(f'Unsupported RINEX Nav version [ {line[5:6]} ] ')

        # body
        while True:
            line = fh.readline().rstrip()
            if line is None or len(line) == 0:
                    break

            if line.startswith('> EOP'):
                skip_lines(fh, 3)
                continue

            elif line.startswith('> STO'):
                skip_lines(fh, 2)
                continue

            elif line.startswith('> ION') and line.endswith('> LNAV'):
                skip_lines(fh, 3)
                continue

            elif line.startswith('> ION') and line.endswith('> D1D2'):
                skip_lines(fh, 3)
                continue

            elif line.startswith('> ION') and line.endswith('> CNVX'):
                skip_lines(fh, 3)
                continue

            elif line.startswith('> ION') and line.endswith('> IFNV'):
                skip_lines(fh, 2)
                continue

            if not line.startswith('> EPH'):
                continue

            fields = line.split()
            sat = fields[2]
            satellite = Satellite(sat[0], int(sat[1:]))  # satellite from eph
            n_lines = Nav._get_block_n_lines(line.rstrip())
            lines = [fh.readline().rstrip() for _ in range(n_lines)]

            epoch_line = lines[0]
            epoch = datetime.datetime.strptime(epoch_line[4:23], "%Y %m %d %H %M %S")

            block_lines = [line] + lines
            block = RawNavBlock(satellite, epoch, block_lines)

            blocks.append(block)

        return blocks

    def get(satellite: Satellite):
        pass

    def __len__(self):
        """
        Number of blocks of the Rinex Nav file
        """
        return len(self.blocks)

    def __iter__(self):
        """
        Iterator for the Rinex blocks, to be used in for loops
        """
        return iter(self.blocks)


    def __lt__(self, other):
        return self.blocks < other.blocks


    @staticmethod
    def create_header(pgm:str = "roktools") -> str:
        """
        Create a basic RINEX 4.99 header

        Subversion 99 stands for Rokubun implementation of Rinex 4 standard
        that supports LEO navigation blocks
        """

        epoch_str = datetime.datetime.utcnow().strftime('%Y%m%d %H%M%S UTC ')

        out = "     4.99           NAVIGATION DATA     M                   RINEX VERSION / TYPE\n"
        out = out + f"{pgm.ljust(20)}rokubun             {epoch_str}PGM / RUN BY / DATE\n"
        out = out + "    18                                                      LEAP SECONDS\n"
        out = out + "                                                            END OF HEADER\n"
        return out

    @staticmethod
    def create_leo_navblock(tle:TLE, sat_clock:Clock) -> RawNavBlock:
        """
        Output a RINEX4 navigation block with the pseudo-orbital parameters
        defined in the TLE two element set
        """

        lines = []

        def create_orbit_line(a:float, b: float, c: float, d: float) -> str:
            return f'    {a:19.12e}{b:19.12e}{c:19.12e}{d:19.12e}'

        # Header line
        try:
            constellation = get_constellation_from_label(tle.label)
            rnxid = RinexSatIdFactory.create(constellation)
        except ValueError:
            raise ValueError(f'Could not infer constellation from [ {tle.label} ]')

        constellation = rnxid.get_constellation_letter()
        satid = rnxid.get_sat_number(tle.id)
        satellite = Satellite(constellation=constellation, prn=satid)
        lines.append(f'> EPH {constellation}{satid:05d}')

        # EPOCH - CLK epoch
        lines.append(tle.toe.strftime('    %Y %m %d %H %M %S') + \
               f'{sat_clock.bias_s:19.12e}{sat_clock.drift_s_per_s:19.12e}{sat_clock.drift_rate_s_per_s2:19.12e}')

        # ORBIT 1
        adot = 0.0
        crs = 0.0
        delta_n0 = 0.0
        M0 = tle.mean_anomaly_rad
        lines.append(create_orbit_line(adot, crs, delta_n0, M0))

        # ORBIT 2
        cuc = 0.0
        e = tle.eccentricity
        cus = 0.0
        sqrta = math.pow(math.sqrt(EARTH_GRAVITATION_PARAM_MU) / tle.mean_motion_rad_per_s, 1.0 / 3.0)  # n = sqrt(mu) / (sqrt(A))^3
        lines.append(create_orbit_line(cuc, e, cus, sqrta))

        # ORBIT - 3
        void = 0.0
        cic = 0.0
        # The RAAN parameter of GPS orbits are referred to the start of the GPS week, not the epoch
        # epoch of the ephemeris. Therfore, we need to compensate it
        weektow = time.to_week_tow(tle.toe)
        t_start_of_week = time.from_week_tow(weektow.week, 0.0)
        greenwich_raan_rad = compute_greenwich_ascending_node_rad(t_start_of_week)
        OMEGA0 = tle.RAAN_rad - greenwich_raan_rad
        OMEGA0 = math.fmod(OMEGA0 + math.tau, math.tau)

        cis = 0.0
        lines.append(create_orbit_line(void, cic, OMEGA0, cis))

        # ORBIT - 4
        i0 = tle.inclination_rad
        crc = 0.0
        omega = tle.arg_perigee_rad
        OMEGA_DOT = 0.0
        lines.append(create_orbit_line(i0, crc, omega, OMEGA_DOT))

        # ORBIT - 5
        idot = 0.0
        delta_n_dot = tle.n_dot_rad_per_s
        lines.append(create_orbit_line(idot, delta_n_dot, void, void))

        return RawNavBlock(satellite, tle.toe, lines)

    @staticmethod
    @process_filename_or_file_handler('w')
    def write_from_tle(output, tle_list: List[TLE]) -> None:

        output.write(Nav.create_header(pgm='rinex_from_tle'))

        for tle in tle_list:

            # Find the clock if available
            sat_clock = Clock(0, 0, 0)
            try:
                nav_block = Nav.create_leo_navblock(tle, sat_clock)
                output.write(str(nav_block))
                output.write('\n')
            except ValueError as e:
                logger.warning(e)
                continue

    @staticmethod
    def _get_block_n_lines(line:str) -> int:
        """
        Give the number of lines of a navigation block for a given constellation
        """

        key = line[6]
        constellation = ConstellationId(key)

        if constellation is not ConstellationId.ONEWEB and \
            constellation is not ConstellationId.SPIRE and \
            constellation is not ConstellationId.STARLINK:
            key = key + " " + line[10:]

        return Nav.RINEX4_EPH_BLOCK_LINES[key]


def compute_greenwich_ascending_node_rad(epoch_utc:datetime.datetime) -> float:
    """
    Compute the Ascending Node of the Greenwich meridian at the given UTC epoch

    >>> round(compute_greenwich_ascending_node_rad(datetime.datetime(2024, 2, 11)), 9)
    2.453307616
    """

    gmst_h = time.gmst(epoch_utc)

    gmst_rad = gmst_h * math.tau / 24.0
    gmst_rad = gmst_rad % math.tau

    return gmst_rad

def merge_nav(files:List[Union[str,IO]]) -> str:
    """
    Merge RINEX navigation files

    :param files: list of RINEX Nav files to merge

    :return: the merged RINEX NAV file as a string
    """

    # Read navigation blocks and place them into memory
    rinex_navs = [Nav(file) for file in files]

    sorted_blocks = sorted([block for rinex_nav in rinex_navs for block in rinex_nav])

    # Proceed to output all of them
    out = Nav.create_header(pgm="merge_rinex_nav")

    out += '\n'.join([str(block) for block in sorted_blocks])

    return out

def merge_nav_cli():

    parser = argparse.ArgumentParser(description="Tool to merge various RINEX 4 files",
                                        formatter_class=argparse.RawDescriptionHelpFormatter)  # for verbatim

    parser.add_argument('files', metavar='FILE', type=str, nargs='+', help='input RINEX4 file(s)')

    args = parser.parse_args()

    merged_rinex_str = merge_nav(args.files)

    sys.stdout.write(merged_rinex_str)


def rinex_from_tle():

    argParser = argparse.ArgumentParser(description="Tool to convert a TLE file (from Celetrak) to RINEX file. Based on https://arxiv.org/abs/2401.17767",
                                        formatter_class=argparse.RawDescriptionHelpFormatter)  # for verbatim

    argParser.add_argument('celestrak_file', metavar='<filename>', type=str,
                           help='File from Celestrak with the TLE elements to convert to RINEX')

    args = argParser.parse_args()

    tle_list = read_celestrak(args.celestrak_file)

    Nav.write_from_tle(sys.stdout, tle_list)
