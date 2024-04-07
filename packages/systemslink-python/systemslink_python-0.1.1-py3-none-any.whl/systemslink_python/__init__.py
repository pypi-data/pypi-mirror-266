import requests
import datetime
import openpyxl
import pathlib
import pickle
import json
import os

# ─── CUSTOM EXCEPTIONS ──────────────────────────────────────────────────────────
class AccessDeniedException(Exception):
    """Used when a valid authentication cookie could not be retrieved."""

    def __init__(self, server_address, *args):
        super().__init__(args)
        self.server_address = server_address

    def __str__(self):
        return f"The system was unable to authenticate with the server at {self.server_address}."

class ParseFailureException(Exception):
    """Indicates that data could not be extracted from a response document."""

    def __str__(self):
        return "Failed to parse data from HTML. This may indicate data was not in expected format."

# ─── MAIN CLASSES ───────────────────────────────────────────────────────────────
class SystemsLinkMeter:
    """Class representing an individual meter object"""

    def __init__(self, server, id_, site_id, site_code, site_name, meter_ref, meter_serial,
                 location, supplier, utility, ref, sub_meter, tariff, units):
        """Creates a meter object with all of the following parameters.
        
        Parameters:
            server: The SystemsLinkServer object that this meter is associated with. Used for
                    performing web requests to retrieve data
            id: The internal SystemsLink ID for this meter
            site_code: In my system, the field called code is used to represent the building code.
            site_name: In the WebUI of our system, this is used to show the meter's building
            meter_ref: Not entirely sure what this represents. It is for the 'MeterReference' field
            meter_serial: Serial number one of the meter
            location: Location field of the meter
            supplier: Supplier of this meter 
            utility: The type of substance this meter is measuring (e.g. gas / electricity)
            ref: In our system, this is used as a description of the room this meter supplies
            sub_meter: Is SubMeter flag
            tariff: Again, not entirely sure what this does but should reflect the 'Tariff' field
            units: The units that this meter is measuring in
        """

        self._server = server
        self.id = id_
        self.site_id = site_id
        self.site_code = site_code
        self.site_name = site_name
        self.meter_ref = meter_ref
        self.meter_serial = meter_serial
        self.location = location
        self.supplier = supplier
        self.utility = utility
        self.ref = ref
        self.sub_meter = sub_meter
        self.tariff = tariff
        self.units = units
    
    def __str__(self):
        return f"{self.site_code} | {self.ref} ({self.utility})"
    
    def get_amr_data(self, date):
        """Get the AMR data from this meter on the specified day.
        
        Parameters:
            date: A python datetime.date object representing the day to retrieve data about
        
        Returns:
            dict {timestamp: value}: Where the timestamp is a Python datetime object representing
                                     the time when the reading was captured (i.e. showing
                                     consumption for the preceding 30 min period). For the period
                                     23:30 to midnight, the timestamp will be 1us before midnight
                                     to facilitate easier by-day aggregation
        """

        meter_points = self._server.get_amr_meter_data(self.id, date)

        # ─── PROCESS DATES ───────────────────────────────────────────────
        output_dict = {}
        for point in meter_points.keys():
            # 24:00 is not a valid time in 24hour clock. Convert to 23:59:59.999999 instead
            if point[11:16] == "24:00":
                point_timestamp = (datetime.datetime.strptime(point[0:10], "%d/%m/%Y") +
                                  datetime.timedelta(days=1) - datetime.timedelta(microseconds=1))
            
            # Otherwise can parse the whole date normally
            else:
                point_timestamp = datetime.datetime.strptime(point, "%d/%m/%Y %H:%M")
            
            output_dict[point_timestamp] = meter_points[point]
        
        return output_dict
    
    def get_year_data(self, start_date: datetime.date):
        """Use the 'Annual Hourly Summary' report to get an entire year of data at once.
        
        Parameters:
            start_date: The most recent day to be included in the report.
        
        Returns:
            dict {timestamp: value}: Where the timestamp is a Python datetime object representing
                                     the time when the reading was captured (i.e. showing
                                     consumption for the preceding 30 min period). For the period
                                     23:30 to midnight, the timestamp will be 1us before midnight
                                     to facilitate easier by-day aggregation
        """

        report_data = self._server.get_amr_year_report(self.id, self.site_id, start_date)

        # Modify timestamp for data points that are recorded exactly at midnight. 
        for entry in list(report_data.keys()):  # Convert to list because dictionary being modified
            if entry.time() == datetime.time(0,0,0,0):
                report_data[entry-datetime.timedelta(microseconds=1)] = report_data[entry]
                del report_data[entry]
        
        return report_data


class SystemsLinkServer:
    """Class encompassing all functions that handle interacting with the server itself."""

    CACHE_DIR = pathlib.Path("cache/")
    COOKIE_CACHE_PATH = CACHE_DIR / "cookies"
    
    def __init__(self, base_url, username, password, disable_cookie_cache=False):
        self._base_url = base_url
        self._username = username
        self._password = password
        self._disable_cookie_cache = disable_cookie_cache

        self._session = requests.session()

        # Create caching DIR if necessary
        if not os.path.exists(self.CACHE_DIR) and not self._disable_cookie_cache:
            os.mkdir(self.CACHE_DIR)

        self._get_auth_cookie()
    
    def _get_auth_cookie(self):
        """Retrieves an authentication cookie using the stored username & password.
        If caching is enabled, an attempt is made to load cookie from configured cache. If
        unavailable or expired, a new cookie is requested from the server. Result is stored in
        _session.cookies
        
        Raises:
            systemslink_energy.AccessDeniedException: The system was unable to authenticate with
                                                      the configured server.
        """

        if not self._disable_cookie_cache and os.path.exists(self.COOKIE_CACHE_PATH):
            with open(self.COOKIE_CACHE_PATH, "rb") as f:
                self._session.cookies.update(pickle.load(f))

                # Remove any expired cookies
                for cookie in self._session.cookies:
                    if cookie.is_expired():
                        self._session.cookies.pop(cookie.name)
        
        if not self._session.cookies.get("AUTHCOOKIE"):
            print("Cookie Expired, requesting new auth cookie.")
            
            r = self._session.post(self._base_url+"Account/Login", data={
                "UserName": self._username,
                "Password": self._password
            })

            if not r.cookies.get("AUTHCOOKIE"):
                raise AccessDeniedException(self._base_url)
        
        if not self._disable_cookie_cache:
            with open(self.COOKIE_CACHE_PATH, "wb") as f:
                pickle.dump(self._session.cookies, f)
    
    def get_meter_list(self):
        """Retrieve a list of all meters that the authenticated user has access to.
        
        Raises:
            systemslink_energy.ParseFailureException: Data retrieved from the server was not in
                                                      expected format and data could not be parsed
        
        Returns:
            Meters: An array of dictionary containing all attributes about each meter.
        """

        index_response = self._session.get(self._base_url+"DataSet/Index")
        
        # ─── PARSING DATA ────────────────────────────────────────────────
        # Data is contained within a <script> tag in the HTML file. More specifically, it is held
        # within a jquery construct on a line that begins with $('#dataTableDataSets').dataTable
        data_string = None
        for line in map(str, index_response.content.splitlines()):
            if "$(\\'#dataTableDataSets\\').dataTable" in line:
                curly_brace_level = 0
                square_bracket_level = 0

                # Will track where the relevant data starts and ends
                data_start = 9E30
                data_end = 9E30

                for i, character in enumerate(line):
                    if character == "{":
                        curly_brace_level += 1
                    elif character == "}":
                        curly_brace_level -= 1
                    elif character == "[":
                        square_bracket_level += 1
                    elif character == "]":
                        square_bracket_level -= 1
                    
                    # Looking for the "data" keyword at '{' level 1
                    elif curly_brace_level == 1 and character == "d":
                        if line[i:i+4] == "data":
                            data_start = i + 6
                    
                    # Once we have found data start, the end is identified by a final ']'
                    if i > data_start and square_bracket_level == 0:
                        data_end = i+1
                        data_string = line[data_start:data_end]
                        break
                
                if data_start == 9E30 or data_end == 9E30:
                    raise ParseFailureException()
                
                break  # Only expecting one data line so stop looking
        
        if data_string is None:
            raise ParseFailureException()
        
        # ─── DATA TO OBJECT ──────────────────────────────────────────────
        # Data should now be in a valid format that can be parsed as JSON
        try:
            return json.loads(data_string)
        except json.JSONDecodeError:
            raise ParseFailureException()
    
    def get_amr_meter_data(self, meter_id, date: datetime.date):
        """Get AMR data for specified meter on given date
        
        Parameters:
            meter_id: The internal SystemsLink ID about which to retrieve data
            date: A single day that data can be retrieved from
        
        Returns:
            dict {timestamp: value}: Where the timestamp is a string of the form '16/03/2024 00:30'
                                     representing when the value was recorded. Value is the number
                                     of kWh used in the 30mins before timestamp
        
        Raises:
            systemslink_python.ParseFailureException: There was a problem processing the data from
                                                      the SystemsLink server
        """

        req_optns = {
            "siteId": "0",
            "groupID": "0",
            "reportConfiguration": json.dumps([
                {"Name": "reportdate", "Value": date.strftime("%d/%m/%Y")},
                {"Name": "profileresolution", "Value": "0"},
                {"Name": "reportperiod", "Value": "Day"}
            ]),
            "dataSetId": str(meter_id)
        }
        r = self._session.post(self._base_url+"Report/GetAggregateDatasetProfileReport", req_optns)
        
        # ─── PARSE DATA ──────────────────────────────────────────────────
        raw_data = None
        for line in map(str, r.content.splitlines()):
            if "var chartData" in line:
                data_start = line.find("{")
                data_end = line.rfind("}")
                
                try:
                    raw_data = json.loads(line[data_start:data_end+1])
                except json.decoder.JSONDecodeError:
                    raise ParseFailureException()
                
                break
        
        if raw_data is None:
            raise ParseFailureException()

        # ─── CONVERT TO MORE SENSIBLE FORMAT ─────────────────────────────
        response_data = {}
        # Getting data from ToolTips because I think this will always match the data points
        # ToolTip in the form '16/03/2024 00:30' and refers to the time the reading was taken
        # i.e. energy used from 00:00 - 00:30
        for i, label in enumerate(raw_data["ToolTips"][0]["Labels"]):
            response_data[label] = raw_data["Series"][0]["Values"][i]
        
        return response_data
    
    def retrieve_excel_report(self, dataset_id, site_id, report_id, report_date: datetime.date):
        """Retrieves specified report from the ExcelReports endpoint.
        
        Parameters:
            dataset_id: In the case of meters, this appears to be simply the meterID
            site_id: Seems to be the building that this item relates to
            report_id: I think this describes the type of report you want
            report_date: Last date to include in the report
        
        Returns:
            pathlib.Path: The file location of the report that has just been downloaded
        """

        report_cache_name = f"{dataset_id}{site_id}{report_id}.{report_date.isoformat()}.xlsx"
        report_cache_path = self.CACHE_DIR/"ExcelReports/"

        if os.path.exists(report_cache_path/report_cache_name):
            return report_cache_path/report_cache_name
        elif not os.path.exists(report_cache_path):
            os.mkdir(report_cache_path)
        
        request_options = {
            "reportId": report_id,
            "siteId": site_id,
            "reportDate": report_date.strftime("%d/%m/%Y"),
            "dataMode": 0, # Not really sure what all of these represent yet
            "reportType": 1, #
            "groupId": 0, #
            "dataSetId": dataset_id,
            "reportConfiguration": json.dumps([
                {"Name": "reportdate", "Value": report_date.strftime("%d/%m/%Y")},
                {"Name": "datamode", "Value": "0"},
                {"Name": "reportid", "Value": report_id}
            ])
        }

        r = self._session.get(self._base_url+"Report/DownloadExcelReport", params=request_options)
        with open(report_cache_path/report_cache_name, "wb") as f:
            f.write(r.content)
        
        return report_cache_path/report_cache_name
    
    def get_amr_year_report(self, meter_id, site_id, date:datetime.date, report_id=3722):
        """Retrieve a report containing an entire year's worth of data and parse.
        This is designed to help you import a large amount of backdated data. The report is
        retrieved from SystemsLink in an Excel format and Parsed out.

        Parameters:
            meter_id: ID of meter to retrieve data from
            site_id: Site where the meter is located
            date: Date from which to begin gathering data from
            report_id: This is the ID of the report to download. In my system, the "Annual Hourly
                       Summary" always have the report ID 3722 although I don't know if this is
                       the same on all systems so a default it set but can be changed
        """

        report_file = self.retrieve_excel_report(meter_id, site_id, report_id, date)
        
        # ─── USE OPENPYXL TO PARSE DATA FROM WORKBOOK ────────────────────
        workbook = openpyxl.load_workbook(filename=report_file, data_only=True, read_only=True)
        sheet = workbook.active  # 'Data' sheet is open by default

        output_dict = {}
        timestamp = None
        for row in sheet.iter_rows(min_row=0, max_row=20000, min_col=1, max_col=3):
            if type(row[0].value) == datetime.datetime:
                timestamp = row[0].value
            
            if timestamp is not None:
                timestamp += datetime.timedelta(minutes=30)
                # row[1] (B) seems to contain the amount of electricity used at a night rate
                # and row[2] (C) contains the amount of electricity used at a day rate. Either one
                # of them is always 0 in my case so just sum them
                output_dict[timestamp] = row[1].value + row[2].value
        
        return output_dict

class SystemsLinkAPI:
    """Class containing main library functions."""

    def __init__(self, base_url, username, password, site_id, disable_cookie_cache=False):
        """Create a new instance of the SystemsLink API.
        
        Parameters:
            base_url: The root domain in of the SystemsLink server. Should be in the form
                     https://example.org/ (notice trailing /)
            username: A valid login username for this server
            password: A valid login password for this server
            disable_cookie_cache: The authentication cookie is only valid for 2 hours so caching it
                                across program restarts is only intended to reduce authentications
                                while testing. default=False
        """

        self._server = SystemsLinkServer(base_url, username, password, disable_cookie_cache)
        self.site_id = site_id # No support for multiple sites yet
        self.refresh_meters()
    
    def refresh_meters(self):
        """Request an updated list of all available meters from the SystemsLink server.
        Will save result in self._meters attribute
        """

        self._meters = []
        
        for meter in self._server.get_meter_list():
            self._meters.append(SystemsLinkMeter(
                server=self._server,
                id_=meter["Id"],
                site_id=self.site_id,
                site_code=meter["Code"],
                site_name=meter["Name"],
                meter_ref=meter["MeterReference"],
                meter_serial=meter["MeterSerial1"],
                location=meter["Location"],
                supplier=meter["Supplier"],
                utility=meter["Utility"],
                ref=meter["Reference"],
                sub_meter=bool(meter["SubMeter"]),
                tariff=meter["Tariff"],
                units=meter["Units"]
            ))
    
    def get_meters(self):
        return self._meters