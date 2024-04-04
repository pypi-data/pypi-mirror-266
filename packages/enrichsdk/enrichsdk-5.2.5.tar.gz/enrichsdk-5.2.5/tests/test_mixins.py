import os
import sys
import json
import copy
import shutil
import time
import imp
import tempfile
import pytest
import random
import string
import traceback
import moto
import boto3
from moto import mock_s3
import traceback
import pandas as pd

from enrichsdk.package.mock import MockConfig, MockState
from enrichsdk import Transform
from enrichsdk.core.mixins import S3Mixin, ParallelMixin, FilesMixin
from enrichsdk.lib import Context


class MixinInstance(Transform, S3Mixin, ParallelMixin, FilesMixin):
    pass


# => Smple dataset
carsfile = os.path.join(os.path.dirname(__file__), "fixtures", "data", "cars.csv")
carsdf = pd.read_csv(carsfile)


def cars_compute(rows):
    return rows.shape[0]


###########################
def id_generator(size=None, chars=string.ascii_uppercase + string.digits):
    if size is None:
        size = random.randint(1, 25)
    return "".join(random.choice(chars) for _ in range(size))


id_list = [id_generator() for i in range(100)]


def splitfunc(s):
    return len(s)


def applyfunc(label, strlist):
    return len(strlist)


test_bucket_name = "hello"
csv_files = {
    "txns/2014-01-01.csv": (
        b"name,amount,id\n" b"Alice,100,1\n" b"Bob,200,2\n" b"Charlie,300,3\n"
    ),
    "txns/2014-01-02.csv": (b"name,amount,id\n"),
    "txns/2015-01-03.csv": (
        b"name,amount,id\n" b"Dennis,400,4\n" b"Edith,500,5\n" b"Frank,600,6\n"
    ),
}

# Ideas on mocking s3 is from here
# https://github.com/dask/s3fs/blob/master/s3fs/tests/test_s3fs.py
port = 5555
endpoint_uri = "http://127.0.0.1:%s/" % port


def get_boto3_client():
    from botocore.session import Session

    # NB: we use the sync botocore client for setup
    session = Session()
    return session.create_client("s3", endpoint_url=endpoint_uri)


class TestClass(object):
    """
    Test whether I can instantiate a module
    """

    @classmethod
    def setup_class(cls):

        # => Boostrap the workspace
        enrich_root = tempfile.mkdtemp(prefix="enrichtest__")
        cls.enrich_root = enrich_root
        os.environ["ENRICH_ROOT"] = enrich_root

        # => Set root
        enrich_data = os.path.join(enrich_root, "data")
        try:
            os.makedirs(enrich_data)
        except:
            pass
        os.environ["ENRICH_DATA"] = enrich_data

        # => etc
        enrich_etc = os.path.join(enrich_root, "etc")
        try:
            os.makedirs(enrich_etc)
        except:
            pass
        os.environ["ENRICH_ETC"] = enrich_etc

        siteconf = {
            "credentials": {"aws": {"secret_key": "secret", "access_key": "access"}}
        }
        with open(os.path.join(enrich_etc, "siteconf.json"), "w") as fd:
            fd.write(json.dumps(siteconf, indent=4))

        context = Context()
        cls.config = MockConfig(context.asdict())

        # Make sure that site conf is present for the get_credentials.
        # to work
        cls.config.load_test_state({})

        cls.state = MockState(config=cls.config)
        cls.mixintest = MixinInstance(config=cls.config)

        # Need to run a s3 simulating server. See this:
        # https://github.com/dask/s3fs/blob/main/s3fs/tests/test_s3fs.py
        try:
            import shlex
            import subprocess

            cls.proc = subprocess.Popen(shlex.split("moto_server s3 -p %s" % port))
        except Exception as e:
            traceback.print_exc()

        os.environ["AWS_ACCESS_KEY_ID"] = "testing"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
        os.environ["AWS_SECURITY_TOKEN"] = "testing"
        os.environ["AWS_SESSION_TOKEN"] = "testing"

        # Create s3 client
        cls.client = get_boto3_client()

        # Now
        cls.client.create_bucket(Bucket=test_bucket_name)

        # Put files
        for flist in [csv_files]:
            for f, data in flist.items():
                cls.client.put_object(
                    Bucket=test_bucket_name,
                    Key=f,
                    Body=data,
                    ContentType="application/csv",
                    ContentEncoding="utf-8",
                    StorageClass="STANDARD",
                    ACL="public-read-write",
                )

    @classmethod
    def teardown_class(cls):

        if os.path.exists(cls.enrich_root):
            shutil.rmtree(cls.enrich_root)

        for flist in [csv_files]:
            for f, data in flist.items():
                try:
                    cls.client.delete_object(Bucket=test_bucket_name, Key=f)
                except:
                    traceback.print_exc()
                    pass

        cls.proc.terminate()

    def test_invalid_handle_none(self):
        """
        Test invalid credentials
        """

        # Dont give any credentials...
        with pytest.raises(Exception) as excinfo:
            self.mixintest.get_s3_handle(client_kwargs={"endpoint_url": endpoint_uri})

        assert "Could not find the credentials" in str(excinfo)

    def test_invalid_handle_awscred(self):
        """
        Test invalid credentials via aws cred
        """

        self.mixintest.aws_cred = None

        # Dont give any credentials...
        with pytest.raises(Exception) as excinfo:
            self.mixintest.get_s3_handle(client_kwargs={"endpoint_url": endpoint_uri})

        assert "Could not find the credentials" in str(excinfo)

    def test_correct_handle(self):
        """
        Test s3_get_handle
        """

        cred = self.mixintest.get_credentials("aws")
        handle = self.mixintest.get_s3_handle(
            cred=cred, client_kwargs={"endpoint_url": endpoint_uri}
        )

        assert len(handle.ls("/")) == 1
        assert handle.ls("/")[0] == "hello"

    def test_list_files_invalid_s3(self):
        """
        Test list files with invalid s3
        """

        cred = self.mixintest.get_credentials("aws")
        s3 = None

        with pytest.raises(Exception) as excinfo:
            included, excluded = self.mixintest.s3_list_files(
                path="sss", bucket="hello", s3=s3
            )
        assert "Invalid s3 handle" in str(excinfo)

    def test_list_files_invalid_path(self):
        """
        Test list files with invalid path
        """

        cred = self.mixintest.get_credentials("aws")
        s3 = self.mixintest.get_s3_handle(
            cred=cred, client_kwargs={"endpoint_url": endpoint_uri}
        )

        included, excluded = self.mixintest.s3_list_files(
            path="sss", bucket="hello", s3=s3
        )

        assert len(included) == 0
        assert len(excluded) == 0

    def test_list_files_invalid_bucket(self):
        """
        Test list files with invalid path
        """

        cred = self.mixintest.get_credentials("aws")
        s3 = self.mixintest.get_s3_handle(
            cred=cred, client_kwargs={"endpoint_url": endpoint_uri}
        )

        with pytest.raises(Exception) as excinfo:
            included, excluded = self.mixintest.s3_list_files(path="sss", s3=s3)

        assert "Invalid/missing bucket" in str(excinfo)

    def test_list_files_valid_1(self):
        """
        Test list files with valid path - all files
        """

        cred = self.mixintest.get_credentials("aws")
        s3 = self.mixintest.get_s3_handle(
            cred=cred, client_kwargs={"endpoint_url": endpoint_uri}
        )

        included, excluded = self.mixintest.s3_list_files(
            path="txns/*", bucket="hello", s3=s3
        )

        assert len(included) == 3

    def test_list_files_valid_2(self):
        """
        Test list files with valid path - apply filter
        """

        cred = self.mixintest.get_credentials("aws")
        s3 = self.mixintest.get_s3_handle(
            cred=cred, client_kwargs={"endpoint_url": endpoint_uri}
        )

        included, excluded = self.mixintest.s3_list_files(
            path="txns/2015*", bucket="hello", s3=s3
        )

        assert len(included) == 1

    def test_list_files_invalid_func(self):
        """
        Test list files with invalid function
        """

        cred = self.mixintest.get_credentials("aws")
        s3 = self.mixintest.get_s3_handle(
            cred=cred, client_kwargs={"endpoint_url": endpoint_uri}
        )

        func = "hello"

        with pytest.raises(Exception) as excinfo:
            included, excluded = self.mixintest.s3_list_files(
                path="txns/*", bucket="hello", s3=s3, include=func
            )

        assert "Include" in str(excinfo)

    def test_list_files_valid_func(self):
        """
        Test list files with valid function
        """

        cred = self.mixintest.get_credentials("aws")
        s3 = self.mixintest.get_s3_handle(
            cred=cred, client_kwargs={"endpoint_url": endpoint_uri}
        )

        func = lambda x: x.startswith("txns/2014")

        included, excluded = self.mixintest.s3_list_files(
            path="txns/*", bucket="hello", s3=s3, include=func
        )

        assert len(included) == 2

    @pytest.mark.parametrize(
        "df,partitions,cores",
        [
            (carsdf, 1, 1),
            (carsdf, 2, 1),
            (carsdf, 2, 2),
            (carsdf, 2, 10),
            (carsdf, 5, 10),
        ],
    )
    def test_parallel_single(self, df, partitions, cores):
        mixintest = self.mixintest
        rows = df.shape[0]
        dfs = mixintest.pexec_single(df, cars_compute, partitions, cores)
        assert sum(dfs) == rows

    @pytest.mark.parametrize(
        "df,partitions,cores",
        [
            (carsdf, 1, 1),
            (carsdf, 2, 1),
            (carsdf, 2, 2),
            (carsdf, 2, 10),
            (carsdf, 5, 10),
        ],
    )
    def test_parallel_multiple(self, df, partitions, cores):
        """
        Test parallel execution
        """
        mixintest = self.mixintest

        dfs = [df[df.YEAR == y] for y in df.YEAR.unique()]
        dfs = mixintest.pexec_multiple(dfs, cars_compute, cores)
        assert sum(dfs) == df.shape[0]

    @pytest.mark.parametrize(
        "label,files,splitfunc,applyfunc,error",
        [
            (None, None, None, None, "label"),
            ("hello", None, None, None, "files"),
            ("hello", "Kilo", None, None, "files"),
            ("hello", [], None, None, "splitfunc"),
            ("hello", [], "shello", None, "splitfunc"),
            ("hello", [], splitfunc, None, "applyfunc"),
            ("hello", [], splitfunc, "hello", "applyfunc"),
        ],
    )
    def test_file_split_apply_invalid_parameters(
        self, label, files, splitfunc, applyfunc, error
    ):
        """
        Check parameters
        """

        with pytest.raises(Exception) as excinfo:
            self.mixintest.file_split_apply(label, files, splitfunc, applyfunc)

        assert "Invalid parameter" in str(excinfo)
        assert error in str(excinfo)

    def test_file_split_apply_valid_parameters(self):
        """
        Check valid parameters
        """

        result = self.mixintest.file_split_apply("ehllo", id_list, splitfunc, applyfunc)

        assert isinstance(result, dict)
        assert len(id_list) == sum(result.values())

    def test_file_preprocessed_read(self):
        """
        Test the file preprocess
        """

        # => Check whether the loading is correct
        root = os.path.join(self.enrich_root, "data", "_test", "root")
        metadata = self.mixintest.file_preprocessed_read(root)

        assert "dfs" in metadata
        assert "files" in metadata
        assert len(metadata["dfs"]) == 0
        assert len(metadata["files"]) == 0
