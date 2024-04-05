# (c) 2015-2022 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
from playmolecule.job import Job, JobStatus
from playmolecule.utils import (
    get_destination_folder,
    ensurelist,
    parse_timestamp_utc,
    utc_timestamp_to_local,
    _requestURL,
    InvalidTokenError,
)
from playmolecule.datacenter import DataCenter
from playmolecule.config import _config
from dateutil.parser import parse as dateparse
import time
import logging
import json
import os


logger = logging.getLogger(__name__)


class fg:
    black = "\u001b[30m"
    red = "\u001b[31m"
    green = "\u001b[32m"
    yellow = "\u001b[33m"
    blue = "\u001b[34m"
    magenta = "\u001b[35m"
    cyan = "\u001b[36m"
    white = "\u001b[37m"
    end = "\033[0m"

    def rgb(r, g, b):
        return f"\u001b[38;2;{r};{g};{b}m"


class UserNotFoundError(Exception):
    pass


class UserFailedRegistrationError(Exception):
    pass


class UserUpdateError(Exception):
    pass


class SessionError(Exception):
    pass


class UserNotLoggedInError(Exception):
    pass


def _throw_error(message, _logger=False):
    if _logger:
        logger.error(message)
    else:
        raise SessionError(message)


def _describe_app(python_obj, job=None):
    nonprivparams = [param for param in python_obj["params"] if param["name"][0] != "_"]
    mandatoryparams = sorted(
        [param for param in nonprivparams if param["mandatory"]],
        key=lambda param: param["name"],
    )
    optionalparams = sorted(
        [param for param in nonprivparams if not param["mandatory"]],
        key=lambda param: param["name"],
    )
    printparams = mandatoryparams + optionalparams

    print(f"{fg.yellow}Parameters\n----------{fg.end}")
    for param in printparams:
        atype = param["type"]
        if atype == "str_to_bool":
            atype = "bool"
        if param["nargs"] is not None:
            atype = f"list[{atype}]"
        default = param["value"] if param["type"] != "str" else f"\"{param['value']}\""
        helpstr = f"{fg.yellow}{param['name']}{fg.end} : {fg.blue}{atype}{fg.end}, {fg.green}default={default}{fg.end}"
        if param["mandatory"]:
            helpstr += f" {fg.red}[Required]{fg.end}"
        choices = param["choices"]
        if choices is not None:
            choices = '", "'.join(choices)
            helpstr += f', {fg.magenta}choices=("{choices}"){fg.end}'
        print(helpstr)
        descr = param["description"]
        print("    " + descr)


def requires_login(func):
    def wrapper(*args, **kwargs):
        if not args[0]._is_logged_in():
            raise UserNotLoggedInError("This method requires first calling login()")
        return func(*args, **kwargs)

    return wrapper


class Session:
    """The central class through which we control the PlayMolecule backend.

    Starts a PlayMolecule session with a user token, each user has his own unique token.
    There are some operations which can only be performed by using the Admin token.

    Parameters
    ----------
    token: str
        The user token. If None it will try to read it from the config file.
    wait_for_backend : bool
        If set to True, it will block execution until it manages to contact the PlayMolecule backend
    server_ip : str
        The IP address of the backend server. If None it will try to read it from the config file.
    server_port : int
        The port on which the backend server listens. If None it will try to read it from the config file.
    server_version : str
        The API version of the backend server. If None it will try to read it from the config file.
    server_protocol : str
        The protocol used by the backend server.

    Examples
    --------
    >>> s = Session()
    >>> s = Session(server_ip="127.0.0.1", server_port=8095, wait_for_backend=True)
    >>> s.login(username="user", password="pass")
    """

    def __init__(
        self,
        wait_for_backend=False,
        server_ip=None,
        server_port=None,
        server_version="v2",
        server_protocol="http",
        _access_token=None,
        _refresh_token=None,
    ):
        self.output = "."
        self._access_token = _access_token
        self._refresh_token = _refresh_token

        if server_ip is None or server_port is None:
            val = os.getenv("PM_BACKEND_ENDPOINT")
            if val is not None:
                self._server_endpoint = val
            else:
                self._server_endpoint = (
                    _config.get("server", "endpoint")
                    + "/"
                    + _config.get("server", "version")
                )
        else:
            self._server_endpoint = (
                f"{server_protocol}://{server_ip}:{server_port}/{server_version}"
            )

        if wait_for_backend:
            self.wait_for_backend()

        services = self.get_service_status(_logger=False)
        down = [serv for serv, val in services.items() if not val["Status"]]
        if len(down) != 0:
            logger.warning(
                f"PMWS Server is currently reporting the following services as offline: {down}"
            )

    def _generate_access_token(self):
        res = _requestURL(
            "get",
            "/auth/refresh-token",
            headers={"Authorization": f"REFRESH_TOKEN {self._refresh_token}"},
            _logger=False,
            endpoint=self._server_endpoint,
        )
        res = res.json()
        self._access_token = res["data"]["access_token"]

    def _request_url(self, *args, **kwargs):
        if "_throwError" not in kwargs:
            kwargs["_throwError"] = _throw_error
        return _requestURL(*args, **kwargs, endpoint=self._server_endpoint)

    @requires_login
    def _request_url_token(self, *args, **kwargs):
        if "_throwError" not in kwargs:
            kwargs["_throwError"] = _throw_error

        try:
            if "headers" not in kwargs:
                kwargs["headers"] = {}
            kwargs["headers"].update(
                {"Authorization": f"ACCESS_TOKEN {self._access_token}"}
            )

            return _requestURL(*args, **kwargs, endpoint=self._server_endpoint)
        except InvalidTokenError:
            # Refresh the access token if we failed due to invalid token and call the function again
            self._generate_access_token()
            kwargs["headers"]["Authorization"] = f"ACCESS_TOKEN {self._access_token}"
            return _requestURL(*args, **kwargs, endpoint=self._server_endpoint)

    def wait_for_backend(self):
        """Blocks execution until it's able to contact the backend server"""
        while True:
            try:
                _ = self._request_url("get", "/apps", _logger=False)
                break
            except SessionError:
                logger.warning(
                    "Could not find PMWS backend. Sleeping for 5s and trying again"
                )
                time.sleep(5)

    def register(self):
        """Registers a new user in PlayMolecule

        Parameters
        ----------
        admin_token : str
            The admin user token
        """
        from getpass import getpass

        email = input("Email: ")
        fullname = input("Full name: ")
        username = input("Username: ")
        password = getpass()
        # TODO: Hash the pass with some salt for transit
        self._request_url(
            "post",
            "/auth/signup",
            headers={"Content-Type": "application/json"},
            json={
                "mail": email,
                "username": username,
                "password": password,
                "name": fullname,
            },
        )

        code = input("Please enter the code sent to your email: ")
        self._request_url(
            "post", "/auth/verify/mail", json={"mail": email, "code": code}
        )
        logger.info("User registered!")

    def login(self, email=None, password=None, google_auth=False):
        """Logs in a user retrieving the user token from the user name and password"""
        from getpass import getpass
        import webbrowser

        if google_auth:
            webbrowser.open(f"{self._server_endpoint}/auth/google/login")
            return

        if email is None:
            email = input("Email: ")
        if password is None:
            password = getpass()

        # TODO: Hash the pass with some salt for transit
        res = self._request_url(
            "post", "/auth/login", json={"mail": email, "password": password}
        )
        res = res.json()
        self._access_token = res["data"]["access_token"]
        self._refresh_token = res["data"]["refresh_token"]

        if self._access_token is None:
            raise RuntimeError("Failed to login")

        logger.info(
            f"Hello {res['data']['username']}. You have successfully logged in."
        )

    @requires_login
    def _get_all_users(self):
        res = self._request_url_token("get", "/users")
        return json.loads(res.text)

    def _is_logged_in(self):
        return self._access_token is not None

    def _require_log_in(self):
        if not self._is_logged_in():
            raise RuntimeError(
                "Please either use login(), register(), or pass your personal token to Session to use the API."
            )

    def _get_apps(self):
        r = self._request_url("get", "/apps", _logger=False)
        if r is None:
            return

        res = json.loads(r.text)
        apps = {}
        apps_rev = {}
        for app in res:
            apps_rev[app["id"]] = f"{app['name']}_v{app['version']}"
            if app["name"] not in apps:
                apps[app["name"]] = {}
            version = float(app["version"])
            if version not in apps[app["name"]]:
                apps[app["name"]][version] = {"id": app["id"]}

        return apps, apps_rev

    def _get_app_id(self, appname, version=None, _logger=True):
        apps, _ = self._get_apps()

        appnamelower = appname.lower()
        # Lower-case the app names for comparison
        apps = {key.lower(): val for key, val in apps.items()}

        if appnamelower not in apps:
            _throw_error(f"The app {appname} does not exist", _logger)

        if version is None:
            version = sorted(apps[appnamelower])[
                -1
            ]  # Get latest version if not specified
        else:
            version = float(version)
            if version not in apps[appnamelower]:
                _throw_error(
                    f"Version {version} of app {appname} does not exist", _logger
                )

        return apps[appnamelower][version]["id"]

    def get_apps(self, _logger=True):
        """Returns or prints the available apps.

        The list of apps is printed if _logger is True else it's returned

        Parameters
        ----------
        _logger: bool
            Set as True for printing the info and errors in sys.stdout.
            If False, it returns the same information as an object.

        Returns
        -------
        app_list : list
            A list with all the app info
        """
        r = self._request_url("get", "/apps", _logger=_logger)
        if r is None:
            return

        python_obj = json.loads(r.text)
        if _logger:
            print("%-30s %-50s %-20s" % ("Name", "Description", "Version"))
            for app in python_obj:
                print(
                    "%-30s %-50s %-20s"
                    % (app["name"], app["description"], app["version"])
                )
        else:
            return python_obj

    def describe_app(self, appname, version=None, _logger=True):
        """
        Describe the input parameters of an app.

        Parameters
        ----------
        appname: str
            The app name
        version: str
            The app version to be described.
        _logger : bool
            Set to False to return the app information as a dictionary. Otherwise it will be printed to sys.stdout.
        """
        appid = self._get_app_id(appname, version, _logger)
        r = self._request_url("get", f"/apps/{appid}/manifest", _logger=_logger)
        if r is None:
            return

        python_obj = json.loads(r.text)
        if _logger:
            _describe_app(python_obj, None)
        else:
            return python_obj

    @requires_login
    def get_jobs(
        self,
        limit=None,
        group=None,
        appid=None,
        execid=None,
        count=False,
        in_status=None,
        not_in_status=None,
        newer_than=None,
        older_than=None,
        children=False,
        children_in_status=None,
        _logger=True,
    ):
        """Returns or prints a list of submitted jobs.

        Parameters
        ----------
        limit: int
            Maximum number of jobs to be listed or returned
        group: str
            The executions group to be returned
        appid: str
            Specify the id of an app to return only executions of this app
        execid: str
            Specify the execution ID of a job. It can accept a partial beginning of an execution ID or the whole execid
        count: bool
            If True it will only return the number of jobs matching the above criteria
        in_status : list
            A list of JobStatus codes. Jobs which are in any of the specified states will be returned
        not_in_status : list
            A list of JobStatus codes. Only jobs which don't belong to any of the specified states will be returned
        newer_than : int
            Return only jobs more recent than `newer_than` seconds.
        older_than : int
            Return only jobs more old than `older_than` seconds.
        children : bool
            Set to True to also return the children of the jobs
        children_in_status : list
            A list of JobStatus codes. Only children jobs which are in any of the specified states will be returned
        _logger: bool
            Set as True for printing the info and errors in sys.stdout.
            If False, it returns the same information as a list (default=True).

        Returns
        -------
        execs: list
            A list of job executions
        """
        request_dict = {}
        if in_status is not None:
            request_dict["in_status"] = [int(s) for s in ensurelist(in_status)]
        if not_in_status is not None:
            request_dict["not_in_status"] = [int(s) for s in ensurelist(not_in_status)]
        if group is not None:
            request_dict["group"] = str(group)
        if appid is not None:
            request_dict["app_id"] = str(appid)
        if execid is not None:
            request_dict["exec_id"] = str(execid)
        if children_in_status is not None:
            request_dict["children_in_status"] = [
                int(s) for s in ensurelist(children_in_status)
            ]
        request_dict["newer_than"] = int(newer_than) if newer_than is not None else -1
        request_dict["older_than"] = int(older_than) if older_than is not None else -1
        request_dict["limit"] = limit if limit is not None else -1
        request_dict["count"] = count
        request_dict["children"] = children

        r = self._request_url_token("post", "/jobs", json=request_dict, _logger=_logger)
        if r is None:
            return

        # _, apps_rev = self._get_apps()
        if count:
            return json.loads(r.text)

        executions = json.loads(r.text)[::-1]
        for exe in executions:
            exe["date"] = parse_timestamp_utc(exe["date"])
            if "{" in exe["specs"]:
                try:
                    exe["specs"] = json.loads(exe["specs"].replace("'", '"'))
                except Exception:
                    pass
            else:  # Compatibility with old jobs
                exe["specs"] = {"app": exe["specs"]}

        if _logger:
            strfmt = "{:<20} {:<37} {:<16s} {:<30} {:<30} {:<30}"
            print(strfmt.format("App", "ID", "Status", "Date", "Name", "Group"))
            for exe in executions:
                print(
                    strfmt.format(
                        exe["container"],
                        exe["id"],
                        str(JobStatus(int(exe["status"]))),
                        utc_timestamp_to_local(exe["date"]).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        exe["name"],
                        exe["group"],
                    )
                )
        else:
            return executions

    @requires_login
    def get_job(self, execid=None, name=None, group=None, strict=True, _logger=True):
        """Finds and returns a Job object

        Parameters
        ----------
        execid : str
            The execution id
        name : str
            The name of an execution
        group : str
            The group of an execution
        strict : bool
            If strict is True, Job creation will raise exceptions if not able to load correctly the app configuration into the Job.
        _logger: bool
            If False, it will reduce verbosity.

        Returns
        -------
        job: Job
            The job object with all it's parameters set

        Examples
        --------
        >>> job = s.get_job(execid="3cadd50b-b208-4a3d-8cf3-d991d22e858a")
        """
        if execid is not None:
            url = f"/jobs/{execid}"
        elif name is not None and group is not None:
            url = f"/jobs/group/{group}/{name}"
        else:
            _throw_error("The job id or group and name has to specified", _logger)
            return

        r = self._request_url_token("get", url, _logger=_logger)
        if r is None:
            return

        job_info = json.loads(r.text)
        job = Job(session=self, appid=None, job_json=job_info, strict=strict)
        return job

    @requires_login
    def start_app(self, appname, version=None, _logger=True):
        """Returns a new job object of the specified app.

        Parameters
        ----------
        appname: str
            The app name of the used app.
        version: str
            The app version to be used.
        _logger: bool
            Set as True for printing the info and errors in sys.stdout. If False, it returns the same information as an object (default=True).

        Returns
        -------
        job: Job
            The new job object

        Examples
        --------
        >>> job = s.start_app("ProteinPrepare")
        >>> job.pdbid = "3ptb"
        >>> job.submit()
        """
        appid = self._get_app_id(appname, version, _logger)
        job = Job(session=self, appid=appid)
        return job

    @requires_login
    def retrieve_jobs(
        self,
        outdir=".",
        force=False,
        execid=None,
        name=None,
        group=None,
        recursive=False,
        _logger=True,
    ):
        """Retrieve the results of several jobs.

        Parameters
        ----------
        outdir : str
            Path to which to retrieve the jobs
        force: bool
            If force=True, the destination folder will be overwritten
        execid:
            The id of the job to be retrieved.
        name : str
            The name of an execution to be retrieved
        group : str
            The group of an execution to be retrieved
        recursive : bool
            Set to True to store the jobs in subfolders named by the job names
        _logger: bool
            Set to False to reduce verbosity

        Examples
        --------
        >>> s.retrieve_jobs("./results", execid="3cadd50b-b208-4a3d-8cf3-d991d22e858a")
        >>> s.retrieve_jobs("./results", group="my_job_group") # Will retrieve all jobs of the group
        """
        outdir = os.path.abspath(outdir)
        if execid is not None:
            job = self.get_job(execid=execid)
            if recursive:
                folder = job.name
                if job.name == "":
                    folder = execid
                outdir = get_destination_folder(
                    os.path.join(outdir, folder), force=force
                )
            else:
                outdir = get_destination_folder(
                    os.path.join(outdir, execid), force=force
                )
            os.makedirs(outdir, exist_ok=True)
            job.retrieve(path=outdir, force=False, _logger=_logger)
        elif group is not None and name is not None:
            job = self.get_job(group=group, name=name)
            inner_folder = os.path.join(group, name)
            outdir = get_destination_folder(
                os.path.join(outdir, inner_folder), force=force
            )
            os.makedirs(outdir, exist_ok=True)
            job.retrieve(path=outdir, force=False, _logger=_logger)
        elif group is not None and name is None:
            jobs = self.get_jobs(group=group, _logger=_logger)
            outdir = get_destination_folder(os.path.join(outdir, group), force=force)
            os.makedirs(outdir, exist_ok=True)
            for job in jobs:
                self.retrieve_jobs(
                    execid=job["id"],
                    outdir=outdir,
                    recursive=True,
                    _logger=_logger,
                )

    @requires_login
    def set_job_status(self, execid, status, error_info=None, _logger=True):
        """Sets the status of a job

        Parameters
        ----------
        execid : str
            The execution ID of the job to modify
        status : JobStatus
            The status to which to set the job
        error_info : str
            If the status is Error you can provide verbose information on the error for the users
        _logger : bool
            Set to False to reduce verbosity

        Examples
        --------
        >>> s.set_job_status(execid="3cadd50b-b208-4a3d-8cf3-d991d22e858a", status=JobStatus.ERROR)
        """
        headers = {"Content-type": "application/json", "Accept": "text/plain"}
        request_dict = {
            "status": int(status),
        }
        if error_info is not None:
            request_dict["error_info"] = str(error_info)

        r = self._request_url_token(
            "put",
            f"/jobs/{execid}",
            headers=headers,
            json=request_dict,
            _logger=_logger,
        )
        if r is None:
            return

        if _logger:
            logger.info(f"Status of execution {execid} updated to {str(status)}")

    def get_service_status(self, _logger=True):
        """Gets the current status of all PlayMolecule backend services

        Parameters
        ----------
        _logger : bool
            Set to False to return the status of the services instead of printing them to sys.stdout
        """
        r = self._request_url("get", "/services", _logger=_logger)
        if r is None:
            return None

        res = json.loads(r.text)
        for key in res:
            res[key]["LastChecked"] = dateparse(res[key]["LastChecked"])

        if _logger:
            logger.info("Current service status:")
            for key, val in res.items():
                status = "Up" if val["Status"] else "Down"
                logger.info(
                    f"    {key:12s}: {status:10s} Last Checked: {val['LastChecked']}"
                )
        else:
            return res

    @requires_login
    def cancel_job(self, execid, _logger=True):
        """Cancels a job.

        This will set the status to ERROR and stop any running execution (children as well)

        Parameters
        ----------
        execid : str
            The execution ID of the job we wish to cancel
        """
        headers = {
            "Content-type": "application/json",
            "Accept": "text/plain",
        }

        r = self._request_url_token(
            "delete", f"/jobs/{execid}", headers=headers, _logger=_logger
        )
        if r is None:
            return

        if _logger:
            logger.info(f"Execution {execid} was cancelled")

    @requires_login
    def delete_job(self, execid, _logger=True):
        """Deletes a job and all associated data and metadata related to it from the backend. Cannot be undone.

        Parameters
        ----------
        execid : str
            The execution ID of the job we wish to cancel
        _logger : bool
            If set to False it reduces the verbosity of the output
        """
        headers = {"Content-type": "application/json", "Accept": "text/plain"}

        r = self._request_url_token(
            "delete", f"/jobs/{execid}/delete", headers=headers, _logger=_logger
        )
        if r is None:
            return

        if _logger:
            logger.info(f"Execution {execid} was deleted")

    @requires_login
    def _get_user_access(self, userid, appid, _logger=True):
        res = self._request_url_token(
            "get", f"/users/{userid}/access/{appid}", _logger=_logger
        )
        if res is None:
            return

        res = json.loads(res.text)
        return res if len(res) != 0 else None

    def _get_user_access_request_file(self, userid, appid, path, _logger=True):
        res = self._get_user_access(userid, appid, _logger)
        if res is None:
            return None

        dc = DataCenter(self)
        fileloc = dc.download_dataset(int(res["access_request_dataset_id"]), path)
        return fileloc

    @requires_login
    def _set_user_access(
        self, userid, appid, status=None, request_dataset_id=None, _logger=True
    ):
        if status is None and request_dataset_id is None:
            raise RuntimeError(
                "You need to pass a value for either status or request_dataset_id"
            )

        request_dict = {
            "requestdatasetid": request_dataset_id,
            "status": status if status is not None else -10,
        }
        res = self._request_url_token(
            "post",
            f"/users/{userid}/access/{appid}",
            data=request_dict,
            _logger=_logger,
        )
        if res is None:
            return

        return json.loads(res.text)

    @requires_login
    def _request_user_access(self, userid, appid, request_file, _logger=True):
        dc = DataCenter(self)
        dsid = dc.upload_dataset(
            request_file,
            f"access-requests/{appid}/{userid}",
            overwrite=True,
            tags="access_requests",
            _logger=_logger,
        )
        if dsid is None:
            return _throw_error(
                "Failed to request user access due to upload failure", _logger=_logger
            )

        return self._set_user_access(
            userid, appid, request_dataset_id=dsid, _logger=_logger
        )

    @requires_login
    def _reduce_user_access(self, userid, appid, _logger=True):
        res = self._request_url_token(
            "delete", f"/users/{userid}/access/{appid}", _logger=_logger
        )
        if res is None:
            return

        return json.loads(res.text)

    @requires_login
    def _get_user_app_rating(self, userid, appid, _logger=True):
        res = self._request_url_token(
            "get", f"/users/{userid}/rating/{appid}", _logger=_logger
        )
        if res is None:
            return

        res = json.loads(res.text)
        return res if len(res) != 0 else None

    @requires_login
    def _set_user_app_rating(self, userid, appid, rating, comment, _logger=True):
        request_dict = {"rating": rating, "comment": comment}
        res = self._request_url_token(
            "post",
            f"/users/{userid}/rating/{appid}",
            data=request_dict,
            _logger=_logger,
        )
        if res is None:
            return

        return json.loads(res.text)

    def _get_total_app_rating(self, appid, _logger=True):
        res = self._request_url("get", f"/apps/{appid}/rating", _logger=_logger)
        if res is None:
            return

        res = json.loads(res.text)
        return res["avg"], res["count"]

    def _get_usage_statistics(self, _logger=True):
        res = self._request_url("get", "/usage_statistics", _logger=_logger)
        if res is None:
            return

        res = json.loads(res.text)
        return res
