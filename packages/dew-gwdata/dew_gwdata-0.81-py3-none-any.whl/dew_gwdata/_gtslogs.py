import collections
import logging
import glob
import os
from pathlib import Path
import pickle
import re
import shutil
import traceback

import pandas as pd
import lasio

try:
    from pandas.core.groupby.groupby import DataError
except ImportError:
    from pandas.core.groupby import DataError

from .utils import *

logger = get_logger()

GTSLOGS_PATHS = {
    "sharedrive": Path(
        r"R:\DFW_CBD\ShareData\Corporate Science Information\Science Monitoring Information\Resource Monitoring Services\3 Assets & Services\Geophysics Glenside\Logging\Gtslogs"
    ),
    "geophyslogs": Path(r"R:\DFW_CBD\Geophyslogs\gtslogs"),
}


scanned_pdf = re.compile(r"\d*_dis[ck]\d*_.*")

_las_to_log_type_alias_mapping = (
    pd.read_csv(Path(__file__).parent / "las_to_alias.csv")
    .set_index("las_mnemonic")
    .alias_name
)


def las_to_log_type(mnemonic):
    """Convert LAS file mnemonic to a log type.

    Args:
        mnemonic (str)

    Returns:
        str: a log type alias. '?' is used for missing mnemonics.

    The mapping is stored in the file las_to_alias.csv which is stored along
    the dew_gwdata source files. Obviously, one day, it should be in SA Geodata.

    """
    if mnemonic in _las_to_log_type_alias_mapping.index.values:
        return _las_to_log_type_alias_mapping.loc[mnemonic]
    else:
        return "?"


def get_las_metadata(las_fn):
    """Quickly obtain some useful metadata about a LAS file.

    Args:
        las_fn (str): path to a LAS file

    Returns:
        dict: dictionary with keys:
        - "max_depth_las" (float) showing the actual range of depths
          in the file
        - "log_types" (str): comma-separated list of alphabetically sorted
          log_types from the mnemonics list below, excluding '?' and duplicates
        - "mnemonics" (list of dicts) - each item is a dict with keys
          "log_type", "las_mnemonic", and "extra_copy"

    """
    results = {}
    las = lasio.read(
        las_fn, null_policy="none", ignore_header_errors=True, ignore_data=True
    )
    result = {}
    result["max_depth_las"] = max([las.well.STOP.value, las.well.STRT.value])
    result["mnemonics"] = las_curves_to_curve_records(las.curves.keys())
    result["log_types"] = ", ".join(
        sorted(
            [
                c["log_type"]
                for c in result["mnemonics"]
                if c["log_type"] != "?" and c["extra_copy"] is False
            ]
        )
    )
    return result


class GtslogsArchiveFolder:
    """Archive of gtslogs data.

    Args:
        path (str): `'geophyslogs'`, `'sharedrive'`, or a path to a folder.

    """

    pickle_filename = "dew_gwdata_cache.pickle"

    def __init__(
        self,
        path="geophyslogs",
        generate_cache=False,
        include_confidential=True,
        **kwargs,
    ):
        try:
            from internal_sa_gwdata import connect_to_sageodata

            self.db = connect_to_sageodata()
        except:
            self.db = None

        if not os.path.isdir(path):
            path = GTSLOGS_PATHS[path]

        self.path = Path(path)
        self._job_paths = {}
        self._job_ranges = {}
        if generate_cache:
            self.cache_job_paths()
        else:
            if os.path.isfile(self.pickle_path):
                self.load_job_path_cache()
            else:
                raise Warning("you need to run with generate_cache=True at least once")
        self.include_confidential = include_confidential
        self.job_kwargs = kwargs

    @property
    def include_confidential(self):
        return self._include_confidential

    @include_confidential.setter
    def include_confidential(self, value):
        self._include_confidential = value
        if value:
            self.included_jobs = self._job_paths.keys()
        else:
            if self.db:
                self.included_jobs = [
                    int(job)
                    for job in self.db.query(
                        "select job_no from dhdb.gl_log_hdr_vw where gl_confidential_flag = 'N'"
                    ).job_no.values
                    if not pd.isnull(job)
                ]
            else:
                print(
                    "Unable to filter out confidential jobs without access to SA Geodata."
                )
                self.included_jobs = self._job_paths.keys()

    @property
    def job_paths(self):
        return {
            job: path
            for job, path in self._job_paths.items()
            if job in self.included_jobs
        }

    @property
    def job_ranges(self):
        return self._job_ranges

    @property
    def pickle_path(self):
        return os.path.join(self.path, self.pickle_filename)

    def find_jobs_for_wells(self, wells):
        jobs = self.db.geophys_log_metadata(wells.dh_no)
        return self[sorted(jobs.job_no.tolist())]

    def refresh(self):
        return self.cache_job_paths()

    def cache_job_paths(self):
        self._job_paths = {}
        self._job_ranges = {}
        for job, path, dirs, filenames in self.walk():
            self._job_paths[job] = path
        self.save_job_path_cache()

    def save_job_path_cache(self):
        with open(self.pickle_path, "wb") as f:
            pickle.dump(
                {"_job_ranges": self._job_ranges, "_job_paths": self._job_paths}, f
            )

    def load_job_path_cache(self):
        with open(self.pickle_path, "rb") as f:
            self.__dict__.update(pickle.load(f))

    def __iter__(self):
        for job_no, job_path in self.job_paths.items():
            yield GLJob(job_path)

    def walk(self):
        """Iterate through Gtslogs.

        Arguments:
            - path (str): root path to search through. You can use a
                file path or a key to the module-level
                variables ``paths``.

        Return:
            A generator. Each next() method call returns a tuple
            ``(job, path, dirs, filenames)``

        Note that it won't iterate through files inside a subfolder of
        a job folder.

        """
        for path, dirs, filenames in os.walk(self.path, topdown=True):
            logger.debug(str(path))

            span = re.search(r"Jobs (\d+) to (\d+)$", path)
            if span:
                job_from = int(span.group(1))
                job_to = int(span.group(2))
                logger.info("{}-{} = {}".format(job_from, job_to, path))
                self._job_ranges[(job_from, job_to)] = path

            dirs.sort(reverse=True)
            base, name = os.path.split(path)
            try:
                job = int(name)
            except:
                pass
            else:
                yield job, path, dirs, filenames

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.job(key, create_if_necessary=False)
        else:
            return self.jobs(key, create_if_necessary=False)

    def job(self, job, create_if_necessary=True, **kwargs):
        """Open geophysical logging job.

        Args:
            job (int): job number.
            create_if_necessary (bool): create an empty folder if
                warranted.

        Other keyword arguments are passed the GLJob constructor.

        Returns: `dew_gwdata.GLJob` object.

        """
        kws = self.job_kwargs
        kws.update(kwargs)
        job = int(job)
        if job in self.job_paths:
            return GLJob(self.job_paths[job], **kws)
        else:
            logger.info("Unable to locate a folder for job {}".format(job))
            for job_from, job_to in self.job_ranges.keys():
                logger.debug(f"Checking for job {job} in range {job_from} to {job_to}")
                if job >= job_from and job <= job_to:
                    parent_path = self.job_ranges[(job_from, job_to)]
                    candidate_job_path = os.path.join(parent_path, str(job))
                    if not os.path.isdir(candidate_job_path):
                        if (
                            not os.path.isfile(candidate_job_path)
                            and create_if_necessary
                        ):
                            logger.info(
                                "Creating job folder {}".format(candidate_job_path)
                            )
                            os.makedirs(candidate_job_path)
                            self.job_paths[job] = candidate_job_path
                            self.save_job_path_cache()
                    if os.path.isdir(candidate_job_path):
                        return GLJob(candidate_job_path, **kws)
        raise KeyError("GLJob {} does not exist in this archive".format(job))

    def jobs(self, job_nos, **kwargs):
        """Return geophysical logging jobs.

        Args:
            job_nos (iterable): list of job numbers.

        Other keyword arguments will be passed to self.job().

        Returns: `dew_gwdata.GLJobs` object.

        """
        return GLJobs([self.job(job_no, **kwargs) for job_no in job_nos])

    def __repr__(self):
        return "<GtslogsArchiveFolder {} jobs @ {}...{}>".format(
            len(self.job_paths), self.path[:8], self.path[-25:]
        )


class GLJobs(collections.abc.MutableSequence):
    """A collection of geophysical logging jobs.

    Not meant to be initialised directly - use
    `dew_gwdata.GtslogsArchiveFolder.jobs()`
    method.

    """

    def __init__(self, jobs=None):
        if jobs is None:
            jobs = []
        self.jobs = jobs
        self._refresh()

    def __repr__(self):
        return repr(self.jobs)

    def __len__(self):
        return len(self.jobs)

    def __getitem__(self, ix):
        return self.jobs[ix]

    def __delitem__(self, ix):
        del self.jobs[ix]
        self._refresh()

    def __setitem__(self, ix, value):
        self.jobs[ix] = value

    def insert(self, ix, value):
        self.jobs.insert(ix, value)
        self._refresh()

    def append(self, value):
        self.jobs.append(value)
        self._refresh()

    def count(self, item):
        return self.jobs.count(item)

    def index(self, *args):
        return self.jobs.index(*args)

    def __iter__(self):
        return iter(self.jobs)

    def _refresh(self):
        if len(self):
            self._attributes = list(self[0].to_scalar_dict().keys())
        else:
            self._attributes = []

    def __getattr__(self, name):
        if name in self._attributes:
            return [getattr(j, name) for j in self]
        else:
            raise AttributeError(
                "GLJobs object does not have an attribute named '{}'".format(name)
            )

    def glob(self, pattern):
        results = []
        for job in self:
            results += job.glob(pattern)
        return results

    @property
    def filenames(self):
        return self.glob("*.*")

    @property
    def data_filenames(self):
        results = []
        for job in self:
            results += job.data_filenames
        return [Path(r) for r in results]

    @property
    def data_files(self):
        results = []
        for job in self:
            results += job.data_files
        return results

    def get_preferred_data_filenames(self, *args, **kwargs):
        return [job.get_preferred_data_filename(*args, **kwargs) for job in self]

    def get_preferred_data_files(self, *args, **kwargs):
        return [job.get_preferred_data_file(*args, **kwargs) for job in self]

    def geophys_log_metadata(self, conn=None, **kwargs):
        """Get geophysical log metadata from SA Geodata."""
        if conn is None:
            from dew_gwdata import sageodata

            conn = sageodata(**kwargs)
        return conn.geophys_log_metadata_by_job_no([j.number for j in self.jobs])


class GLJob:
    def __init__(
        self, path, preferred_files_regexp=".*", preferred_file_method="last_modified"
    ):
        assert preferred_file_method in (
            "last_modified",
            "largest",
            "shortest_filename",
        )
        self._preferred_files_regexp = preferred_files_regexp
        self._preferred_file_method = preferred_file_method
        self.number = int(os.path.split(path)[-1])
        self.job_no = self.number
        logger.debug("opening job {}".format(self.number))
        self.path = Path(path)

    def __hash__(self):
        return self.number

    def to_scalar_dict(self):
        return {
            "number": self.number,
            "job_no": self.job_no,
            "path": self.path,
            # "curves": self.curves,
        }

    def copy_files(self, destination, pattern="*.*"):
        for filename in self.glob(pattern):
            filename = Path(filename)
            shutil.copy(filename, destination)

    @property
    def curves(self):
        curves = []
        for f in self.data_files:
            curves += list(f.curves)
        return set(curves)

    def glob(self, pattern):
        return glob.glob(os.path.join(self.path, pattern))

    @property
    def filenames(self):
        return glob.glob(os.path.join(self.path, "*.*"))

    @classmethod
    def from_filename(cls, filename, **kwargs):
        """Given a filename, return the job number and file name."""
        path = Path(filename)
        job_path_parts = []
        found_job = False
        for part in path.parts[::-1]:
            if found_job:
                job_path_parts.append(part)
            else:
                try:
                    int(part)
                except:
                    pass
                else:
                    found_job = True
                    job_path_parts.append(part)
        return cls(os.path.join(*job_path_parts[::-1]), **kwargs)

    def _get_preferred_file(self, fns=None, method=None):
        if fns is None:
            fns = self.data_filenames
        if method is None:
            method = self._preferred_file_method
        if method == "last_modified":
            return sorted(fns, key=lambda x: os.path.getmtime(x))[-1]
        elif method == "largest":
            return sorted(fns, key=lambda x: os.path.getsize(x))[-1]
        elif method == "shortest_filename":
            return sorted(fns, key=len)[0]

    def get_preferred_data_filename(self, regexp=None):
        if regexp is None:
            regexp = self._preferred_files_regexp

        data_filenames = [
            fn for fn in self.data_filenames if re.search(regexp, os.path.basename(fn))
        ]
        n = len(data_filenames)
        if n == 0:
            return ""
        elif n == 1:
            return data_filenames[0]
        else:
            masters = [fn for fn in data_filenames if ".master" in fn.lower()]
            if len(masters) == 0:
                return self._get_preferred_file(data_filenames)
            elif len(masters) == 1:
                return masters[0]
            else:
                return self._get_preferred_file(masters)

    def get_preferred_data_file(self, **kwargs):
        return LogDataFile(self.get_preferred_data_filename(**kwargs))

    @property
    def data_filenames(self):
        filenames = []
        for fn in self.filenames:
            _, ext = os.path.splitext(fn)
            ext = ext.lower()[1:]
            logger.debug(
                "Checking to see whether {} is a supported log data file extension type".format(
                    ext
                )
            )
            if ext in LogDataFile.supported_exts:
                filenames.append(fn)
        return [Path(fn) for fn in filenames]

    @property
    def data_files(self):
        return [LogDataFile(fn) for fn in self.data_filenames]

    @property
    def scanned_log_pdfs(self):
        filenames = []
        for fn in Path(self.path).glob("*.pdf"):
            if scanned_pdf.match(fn.stem):
                filenames.append(fn)
        return [Path(fn) for fn in filenames]

    def dfs(self, include_curves=None, case_insensitive_match=True):
        """Return dataframes for log data files in job.

        Args:
            include_curves (list): list of regexps for curves to retain.
                if None, keep all.
            case_insensitive_match (bool): if True, make the regexp pattern
                matching case-insensitive

        Returns: dictionary of filename: dataframe selections.

        """
        if not include_curves:
            include_curves = ["*"]
        dfs = {}
        for f in self.data_files:
            df = f.df()
            cols = list(df.columns)
            keep_cols = []
            for col in cols:
                for pattern in include_curves:
                    if case_insensitive_match:
                        pattern = "(?i)" + pattern
                    if re.match(pattern, col) and not col in keep_cols:
                        keep_cols.append(col)
            dfs[f.filename] = df[keep_cols]
        return dfs

    def df(self):
        """Load all curves from all available data files.

        Returns: pandas DataFrame with a MultiIndex for columns
        with levels (filename and curve).

        This may or may not work! TODO FIX ME!

        # For example:

        #     >>> import dew_gwdata as gd
        #     >>> archive = gd.GtslogsArchiveFolder()
        #     >>> df = archive.job(9641).df()
        #     >>> df.info(max_cols=200)
        #     <class 'pandas.core.frame.DataFrame'>
        #     Float64Index: 39686 entries, -0.2103568750114324 to 234.98
        #     Data columns (total 108 columns):
        #     (allwaterNo4_cal8_down_CAL8_2018-12-18_084437.csv, v1 caliper arm extension)                 11650 non-null float64
        #     (allwaterNo4_cal8_down_CAL8_2018-12-18_084437.csv, diameter)                                 11650 non-null float64
        #     ...
        #     (rawdata_allwaterNo4_IND3S_up_IND3S_2018-12-18_114926.csv, depth_v1)                         4837 non-null float64
        #     (rawdata_allwaterNo4_IND3S_up_IND3S_2018-12-18_114926.csv, depth_apparent conductivity)      4837 non-null float64
        #     (rawdata_allwaterNo4_IND3S_up_IND3S_2018-12-18_114926.csv, apparent conductivity)            4837 non-null float64
        #     dtypes: float64(108)
        #     memory usage: 33.0 MB

        # For example, to select only the gamma logs:

        #     >>> gammas = df.iloc[:, df.columns.get_level_values("curve") == "gamma"]
        #     >>> gammas.info()
        #     <class 'pandas.core.frame.DataFrame'>
        #     Float64Index: 39686 entries, -0.2103568750114324 to 234.98
        #     Data columns (total 4 columns):
        #     (allwaterNo4_G9N9SP_down_G9N9+Box1_2018-12-18_104314.csv, gamma)            8700 non-null float64
        #     (allwaterNo4_G9N9SP_up_G9N9+Box1_2018-12-18_110124.csv, gamma)              8700 non-null float64
        #     (rawdata_allwaterNo4_G9N9SP_down_G9N9+Box1_2018-12-18_104314.csv, gamma)    3948 non-null float64
        #     (rawdata_allwaterNo4_G9N9SP_up_G9N9+Box1_2018-12-18_110124.csv, gamma)      6825 non-null float64
        #     dtypes: float64(4)
        #     memory usage: 1.5 MB

        """
        dfs = []
        columns = []
        for i, (fn, f) in enumerate(zip(self.data_filenames, self.data_files)):
            df = f.df()
            name = os.path.basename(fn)
            df.columns = pd.MultiIndex.from_tuples([(name, x) for x in df.columns])
            df.columns.names = ["filename", "curve"]
            dfs.append(df)
        if dfs:
            return pd.concat(dfs, axis=1).interpolate(method="slinear")
        else:
            return pd.DataFrame()

    def geophys_log_metadata(self, conn=None, **kwargs):
        """Get geophysical log metadata from SA Geodata."""
        if conn is None:
            from dew_gwdata import sageodata

            conn = sageodata(**kwargs)
        return conn.geophys_log_metadata_by_job_no([self.number])

    def __repr__(self):
        return "<GL GLJob {}: {} data files>".format(
            self.number, len(self.data_filenames)
        )

    def __int__(self):
        return self.number


def merge_dataframes(dfs, index_duplicate_agg="mean"):
    def get_keys(frames):
        all_keys = []
        for frame in frames:
            cols = list(frame)
            all_keys += cols
        return set(all_keys)

    def rename(frames):
        ret_frames = [list(keys) for keys in frames]
        for key in get_keys(frames):
            locations = []
            for i, frame in enumerate(frames):
                for j, test_key in enumerate(frame):
                    if test_key == key:
                        locations.append((i, j))
            if len(locations) > 1:
                current_count = 1
                for k, (i, j) in enumerate(locations):
                    test_key = frames[i][j]
                    ret_frames[i][j] = test_key + ":{:.0f}".format(k + 1)
        return ret_frames

    labels = [list(df.columns) for df in dfs]
    new_labels = rename(labels)
    new_dfs = []
    for i, df in enumerate(dfs):
        df.columns = new_labels[i]
        try:
            df = df.groupby(df.index).agg(index_duplicate_agg)
        except DataError:
            logger.warning("Skipping dataframe because it lacks numeric data.")
        else:
            new_dfs.append(df)

    if len(new_dfs):
        return pd.concat(new_dfs, axis=1)
    else:
        return pd.DataFrame()


class LogDataFile(object):
    supported_exts = set(("csv", "las"))

    def __init__(self, path, job=None, **kwargs):
        folder, filename = os.path.split(path)
        _, ext = os.path.splitext(filename)
        ext = ext.lower()[1:]

        self._cached = None
        self.reload_kwargs = kwargs
        self.job = job
        self.path = path
        self.folder = folder
        self.filename = filename
        self.ext = ext

        if ext == "csv":
            self.__class__ = CSVLogDataFile
        elif ext == "las":
            self.__class__ = LASLogDataFile

    @property
    def dataobj(self):
        if self._cached is None:
            self._cached = self.reload()
        return self._cached

    def df(self):
        try:
            df = self.dataobj.df()
        except:
            df = self.dataobj
        df.columns = [k.strip().lower() for k in df.columns]
        return df

    @dataobj.setter
    def dataobj(self, value):
        raise NotImplementedError(
            "Cannot set data object directly - modify {} instead.".format(self.path)
        )


class CSVLogDataFile(LogDataFile):
    def df(self):
        return self.dataobj

    def reload(self):
        df = (
            pd.read_csv(self.path, skiprows=[1], **self.reload_kwargs)
            .rename(columns=lambda x: x.strip())
            .rename(columns=str.lower)
        )
        for key in df.columns:
            if key == "depth":
                df = df.set_index(key)
        # dfs = []
        # df_cols = list(df.columns)
        # for key in df_cols:
        #     if key in df.columns:
        #         if key == "depth_" and not key == "depth_original":
        #             data_key = key.replace("depth_", "")
        #             sub_df = pd.DataFrame(
        #                 {"depth": df[key], data_key: df[data_key]}
        #             ).set_index("depth")
        #             dfs.append(sub_df)
        #             df = df[[x for x in df.columns if not x in (key, data_key)]]
        # dfs.append(df.set_index("depth"))

        # new_df = merge_dataframes(dfs)
        # final_df = new_df.interpolate(method="slinear")
        self._cached = df
        return self._cached

    def depth_column(self, key=None):
        curves = self.curves()
        possible_depth_keys = ["Depth", "depth", curves[0]]
        if key:
            possible_depth_keys.insert(0, "depth_{}".format(key))
        for depth_key in possible_depth_keys:
            if depth_key in self.curves():
                break
        return depth_key

    @property
    def curves(self):
        return [x.strip().lower() for x in self.df().columns]

    def curve(self, key):
        return pd.Series(
            data=self.df()[key].values, index=self.df()[self.depth_column()].values
        ).dropna()


class LASLogDataFile(LogDataFile):
    def las(self):
        return self.dataobj

    def reload(self):
        self._cached = lasio.read(self.path, **self.reload_kwargs)
        return self._cached

    @property
    def curves(self, case_transform=None):
        """Get name of the available curves.

        Args:
            case_transform (func, optional): function to transform the
                curve name e.g. `lower`, `upper`. By default it is
                `lambda curve: curve`

        Returns: a list of the curve names for use with :meth:`LASLogDataFile.curve`.

        """
        return [x.strip() for x in self.las().keys()]

    def depth_column(self, key=None):
        return self.las().keys()[0]

    def curve(self, key):
        return pd.Series(data=self.las()[key], index=self.las().curves[0].data).dropna()
