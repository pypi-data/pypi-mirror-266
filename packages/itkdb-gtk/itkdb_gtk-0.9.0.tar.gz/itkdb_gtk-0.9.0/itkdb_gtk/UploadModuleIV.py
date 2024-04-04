#!/usr/bin/env python3
"""Read IV files and create plots.

Analisis de la IV con macros de la webApp

SENSOR_IV_Analysis.py in
https://gitlab.cern.ch/atlas-itk/sw/db/production_database_scripts.git

webApp aqui:
https://itk-pdb-webapps-strips.web.cern.ch

"""
import os
import json
import warnings
from pathlib import Path
import shutil

import gi
import tempfile

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio


from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

try:
    import itkdb_gtk
    
except ImportError:
    import sys
    from pathlib import Path
    cwd = Path(sys.argv[0]).parent.parent
    sys.path.append(cwd.as_posix())

from itkdb_gtk import dbGtkUtils, ITkDBlogin, ITkDButils, UploadTest

# Check if Gtk can be open
gtk_runs, gtk_args = Gtk.init_check()


def remove_files(W, flist):
    for f in flist:
        os.unlink(f)


#
#   The following is taken from
#   https://gitlab.cern.ch/atlas-itk/sw/db/production_database_scripts.git
#
mm = 1e-3
cm = 1e-2
UpperV = 500  # For sensor to pass, I must be < Imax up until this voltage and no breakdown must be detected before then.
StabilityV = 700  # Voltage with multiple current readings to check stability

AreaDict = {
    "Unknown": (97.621 - 0.450) * (97.950 - 0.550) * mm * mm,
    #
    "ATLAS12": 95.7 * 95.64 * mm * mm,
    "ATLAS17LS": (97.621 - 0.450) * (97.950 - 0.550) * mm * mm,
    #
    "ATLAS18R0": 89.9031 * cm * cm,
    "ATLAS18R1": 89.0575 * cm * cm,
    "ATLAS18R2": 74.1855 * cm * cm,
    "ATLAS18R3": 80.1679 * cm * cm,
    "ATLAS18R4": 87.4507 * cm * cm,
    "ATLAS18R5": 91.1268 * cm * cm,
    #
    "ATLAS18SS": 93.6269 * cm * cm,
    "ATLAS18LS": 93.6269 * cm * cm,
    #
    "ATLASDUMMY18": (97.621 - 0.450) * (97.950 - 0.550) * mm * mm,
}


def LocateMicroDischarge(
    I,
    V,
    sm_window=2,
    bd_limit=5.5,
    allow_running_bd=True,
    use_additional_cond=False,
    tolerence=0.05,
    voltage_span=4,
    fit_window=5,
):
    """
    Function for BDV estimation - if questions please contact Vera Latonova (vera.latonova@cern.ch).
    I,V must have same shape and voltages must be in ascending order,
    same indexes of I&V arrays must correspond each other,
    only invalid data or holdstep should be stripped before
    but it is not necessary. Measurments U=0&I=0 are removed.
    If there is same or higher amount of same voltages in row than
    sm_window, from this sequence we cannot estimete dI/dV and
    we have to remove this averaged point.

    It is assumed that only parameter use_additional_cond would be
    changed by caller. Changing of other parameters may affect
    BDV unexpectedly.


    @param[in] I                   - array of currents without any cut
    @param[in] V                   - array of voltages, ascending order, without any cut
    @param[in] sm_window           - size of smoothing window
    @param[in] bd_limit            - BD limit for |U| < 500V
    @param[in] allow_running_bd    - allow increase bd_limit for |U| > 500
    @param[in] use_additional_cond - use additional BD contition
    @param[in] tolerence           - configuration of additional condition
    @param[in] voltage_span        - max width of hump on spectra which may be neglected
                                     in voltage steps in additional contition
    @param[in] fit_window          - number of points used for linear fit before BD voltage

    @return BD voltage (always positive) or NO_BD_CONST = 9.99e99 if not found.
    """
    NO_BD_CONST = 9.99e99

    # add nan to the end of array
    V = np.abs(V)
    I = np.abs(I)

    # skip zeros
    ind = np.where(np.logical_or(I != 0, V != 0))
    V = V[ind]
    I = I[ind]

    V_ = np.append(V, np.nan * np.ones(sm_window - 1))
    I_ = np.append(I, np.nan * np.ones(sm_window - 1))

    # make 2D array of I's, V's each row_ind shifted by row_ind index
    # i.e from array [1,3,5] we make (for sm_window=2) 2D array
    # [  1,3,5,nan]
    # [nan,5,1,3]
    # than get average from each column -> I_avg, V_avg
    r = np.arange(sm_window)

    V2 = np.outer(np.ones(sm_window), V_)
    row_ind, col_ind = np.ogrid[: V2.shape[0], : V2.shape[1]]
    col_ind = col_ind - r[:, np.newaxis]
    V2 = V2[row_ind, col_ind]
    # strip fields with nans
    V2 = np.transpose(V2[:, (sm_window - 1) : -(sm_window - 1)])

    I2 = np.outer(np.ones(sm_window), I_)
    row_ind, col_ind = np.ogrid[: I2.shape[0], : I2.shape[1]]
    col_ind = col_ind - r[:, np.newaxis]
    I2 = I2[row_ind, col_ind]
    I2 = np.transpose(I2[:, (sm_window - 1) : -(sm_window - 1)])

    # get V & I averages
    try:
        V_avg = np.average(V2, axis=1)
        I_avg = np.average(I2, axis=1)
    except ZeroDivisionError:
        # not enough data
        return NO_BD_CONST

    # find dI / dV array
    # I'm not able to write this without cycle
    dIdV = np.array([])
    for i in range(V2.shape[0]):
        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            try:
                dIdV = np.append(dIdV, np.polyfit(V2[i, :], I2[i, :], 1)[0])
            except (np.RankWarning, TypeError):
                dIdV = np.append(dIdV, np.nan)

    # stripping U[n] == U[n+1] (i.e. hodlsetp) => fit cannot be sucessful =>
    # dIdV is nan @holdstep
    ind = np.where(np.isfinite(dIdV))
    I_avg = I_avg[ind]
    V_avg = V_avg[ind]
    dIdV = dIdV[ind]

    # get running BDV limit & compare
    bd_limit_running = bd_limit + np.where(
        allow_running_bd and V_avg > 500, (V_avg - 500.0) / 100.0, 0
    )
    V_avg_BD_ind = dIdV / (I_avg / V_avg) > bd_limit_running
    V_avg_BD = V_avg[V_avg_BD_ind]

    # Estimate BDV
    BDV = np.array([])

    # no break-down
    if V_avg_BD.shape == (0,):
        return NO_BD_CONST

    # if V_avg_BD_ind[0] == True ... BDV <- V[0]
    # for others V_avg_BD_ind[n] == True BDV <- (V_avg[n] + V_avg[n-1])/2
    if V_avg_BD_ind[0]:
        BDV = np.append(BDV, V[0])
    V_avg_BD_ind[0] = False

    BDV = np.append(
        BDV,
        (V_avg[np.where(V_avg_BD_ind)] + V_avg[np.where(V_avg_BD_ind)[0] - 1]) / 2.0,
    )

    ###########################################################################
    ## Application of additional condition ####################################
    ###########################################################################
    if not use_additional_cond:
        return BDV[0]

    # get index if V <= BDV
    B = np.where(np.less.outer(BDV, V))
    col_ind = np.mgrid[: BDV.shape[0], : V.shape[0]][1]
    col_ind[B[0], B[1]] = 0
    V_BDV_ind = np.max(col_ind, axis=1)

    back_ok_v_ind = 0
    while True:
        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            try:
                a, b = np.polyfit(
                    V[
                        max(back_ok_v_ind, V_BDV_ind[0] - fit_window) : max(
                            back_ok_v_ind, V_BDV_ind[0]
                        )
                    ],
                    I[
                        max(back_ok_v_ind, V_BDV_ind[0] - fit_window) : max(
                            back_ok_v_ind, V_BDV_ind[0]
                        )
                    ],
                    1,
                )
            except (np.RankWarning, TypeError):
                return BDV[0]

        ind = np.where(1 - (a * V + b) / I <= tolerence)[0]
        try:
            back_ok_v_ind = np.min(ind[ind > V_BDV_ind[0] + 1])
        except ValueError:
            # sensor is not going back
            return BDV[0]
        # hump is too long -- it cannot be skipped
        if back_ok_v_ind - V_BDV_ind[0] > voltage_span:
            return BDV[0]

        # skip BDVs inside hump
        ind = BDV >= V[back_ok_v_ind]
        BDV = BDV[ind]
        V_BDV_ind = V_BDV_ind[ind]
        if V_avg_BD.shape == (0,):
            return NO_BD_CONST
    return NO_BD_CONST


def scale_iv(I, T1, T2):
    """Normalize corrent  to given temperature (T2)

    Args:
        I (array): Current
        T1 (float): Original temperature
        T2 (float): New temperature.

    Return:
        Array with scaled currents.

    """
    factor = (T2 / T1) ** 2 * np.exp((-1.21 / 8.62) * (1 / T2 - 1 / T1))
    return factor * I


class IVwindow(dbGtkUtils.ITkDBWindow):
    """GUI for IV file handling."""

    def __init__(self, session, title="IV window", options=None):
        """Initialization."""
        super().__init__(
            session=session, title=title, show_search=None, gtk_runs=gtk_runs
        )
        self.mdata = {}
        self.mod_type = {}
        self.mod_SN = {}
        self.difference = None
        self.canvas = None

        self.init_window()

    def init_window(self):
        """Prepare the Gtk window."""
        self.hb.props.title = "IV data"

        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="view-refresh-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to refresh canvas.")
        button.connect("clicked", self.on_refresh)
        self.hb.pack_end(button)

        # Button to upload
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-send-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to upload test")
        button.connect("clicked", self.upload_test)
        self.hb.pack_end(button)

        # File entry and search button
        self.single_file = Gtk.FileChooserButton()
        self.single_file.connect("file-set", self.on_single_file_set)

        self.double_file = Gtk.FileChooserButton()
        self.double_file.connect("file-set", self.on_double_file_set)

        self.single_SN = Gtk.Label(label="(None)")
        self.double_SN = Gtk.Label(label="(None)")

        grid = Gtk.Grid(column_spacing=5, row_spacing=1)

        grid.attach(Gtk.Label(label="Files"), 1, 0, 1, 1)
        grid.attach(Gtk.Label(label="Serial No."), 2, 0, 1, 1)

        grid.attach(Gtk.Label(label="Single Data File"), 0, 1, 1, 1)
        grid.attach(self.single_file, 1, 1, 1, 1)
        grid.attach(self.single_SN, 2, 1, 1, 1)

        grid.attach(Gtk.Label(label="Double Data File"), 0, 2, 1, 1)
        grid.attach(self.double_file, 1, 2, 1, 1)
        grid.attach(self.double_SN, 2, 2, 1, 1)

        btn = Gtk.Button(label="Compute difference")
        btn.connect("clicked", self.on_difference)
        grid.attach(btn, 1, 3, 1, 1)

        btn = Gtk.Button(label="Upload to DB")
        btn.connect("clicked", self.upload_test)
        grid.attach(btn, 2, 3, 1, 1)

        self.mainBox.pack_start(grid, False, True, 0)

        self.fig = mpl.figure.Figure()
        self.fig.tight_layout()
        sw = Gtk.ScrolledWindow()  # Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # A scrolled window border goes outside the scrollbars and viewport
        sw.set_border_width(10)
        sw.set_size_request(310, 310)

        self.canvas = FigureCanvas(self.fig)  # a Gtk.DrawingArea
        self.canvas.set_size_request(400, 300)
        sw.add(self.canvas)
        self.mainBox.pack_start(sw, True, True, 0)

        # Create toolbar
        try:
            toolbar = NavigationToolbar(self.canvas)
        except TypeError:
            toolbar = NavigationToolbar(self.canvas, self)
            
        self.mainBox.pack_start(toolbar, False, False, 0)

        # The text view
        self.mainBox.pack_start(self.message_panel.frame, True, True, 5)

        self.show_all()

    def upload_test(self, *args):
        """Upload available tests."""
        try:
            mdata = self.mdata["double"]
        except KeyError:
            dbGtkUtils.complain("Cannot Upload to DB", "Data not yet ready.")
            return

        # Check if we are dealing with sensors or modules
        is_module = "Module_SN" in mdata

        if is_module:
            test = ITkDButils.get_test_skeleton(
                self.session, "MODULE", self.mdata["double"]["TestType"]
            )
            tp = "ATLAS18{}".format(self.mod_type["double"][0:2])
            area = AreaDict[tp] / cm**2

        else:
            test = ITkDButils.get_test_skeleton(
                self.session, "SENSOR", self.mdata["double"]["TestType"]
            )
            area = AreaDict[self.mod_type["double"]] / cm**2

        # The data arrays
        V = np.abs(mdata["curve"]["V"])
        I = np.abs(mdata["curve"]["I"])
        passed = True

        # Find Current @ 500V
        indx = np.where(V == 500)[0]
        i_500 = I[indx][0] / area
        self.write_message("I @ 500V = {:.2f} nA/cm2\n".format(i_500))

        # Compute current stability
        IStability = abs(I[abs(V) == StabilityV])
        IVariation = -1
        if np.size(IStability) > 1:  # Maybe make == 4?
            IVariation = abs(np.std(IStability) / np.mean(IStability))

        self.write_message("I stability = {:.6f} nA\n".format(IVariation))

        # Search for Micro discharges
        # Check for micro-discharge in non-normalized current,
        # removing duplicate Voltage entries (e.g. for stability measurements)
        comments = []
        defects = []
        UniqueVs, UniqueIndices = np.unique(V, return_index=True)
        MicroDischargeV = LocateMicroDischarge(I[UniqueIndices], UniqueVs)
        if MicroDischargeV < np.max(V):
            comments.append("Found micro discharge: {:.1f} V\n".format(MicroDischargeV))
            self.write_message(comments[-1])

            if MicroDischargeV < UpperV:
                txt = "microdischarge happening before {:.1f}V.".format(UpperV)
                defects.append({
                            "name": "MicroDischarge",
                            "description": txt,
                            "properties": {}
                        }
                )
                self.write_message("...{}. FAILED\n".format(txt))
                passed = False

        test["component"] = self.mod_SN["double"]
        test["institution"] = mdata["Institute"]
        test["runNumber"] = mdata["RunNumber"]
        test["date"] = ITkDButils.get_db_date(
            "{} {}".format(mdata["Date"], mdata["Time"])
        )
        test["passed"] = passed
        test["problems"] = False
        test["properties"]["VBIAS_SMU"] = mdata["Vbias_SMU"]
        test["properties"]["RSERIES"] = mdata["Rseries"]
        test["properties"]["TEST_DMM"] = mdata["Test_DMM"]
        test["properties"]["RSHUNT"] = mdata["Rshunt"]
        test["properties"]["RUNNUMBER"] = mdata["RunNumber"]
        test["properties"]["COMMENTS"] = mdata["Comments"]
        test["properties"]["ALGORITHM_VERSION"] = "0.0.0"
        if is_module:
            test["properties"]["SOFTWARE_TYPE_VERSION"] = "pyProbe"
            test["properties"]["MODULE_STAGE"] = mdata["Module_Stage"]

        test["results"]["TEMPERATURE"] = mdata["Temperature"]
        test["results"]["HUMIDITY"] = mdata["Humidity"]
        test["results"]["VBD"] = MicroDischargeV
        test["results"]["I_500V"] = i_500
        test["results"]["VOLTAGE"] = -np.abs(V)
        test["results"]["CURRENT"] = -np.abs(I)
        test["results"]["RMS_STABILITY"] = IVariation
        test["results"]["SHUNT_VOLTAGE"] = np.zeros(V.shape)
        test["defects"] = defects
        test["comments"] = comments

        # write attachment.
        if is_module:
            items = [
                "Type",
                "Wafer",
                "Module_SN",
                "Module_Stage",
                "Date",
                "Time",
                "Institute",
                "TestType",
                "Vbias_SMU",
                "Rseries",
                "Test_DMM",
                "Rshunt",
                "Software type and version, fw version",
                "RunNumber",
                "Temperature",
                "Humidity",
                "Comments",
            ]
        else:
            items = [
                "Type",
                "Batch",
                "Wafer",
                "Component",
                "Date",
                "Time",
                "Institute",
                "TestType",
                "Vbias_SMU",
                "Rseries",
                "Test_DMM",
                "Rshunt",
                "RunNumber",
                "Temperature",
                "Humidity",
                "Comments",
            ]

        try:
            fnam = "{}_{}_IV_{}-".format(
                self.mod_SN["double"], mdata["Module_Stage"], mdata["RunNumber"]
            )
        except KeyError:
            fnam = "{}_W_IV_{}".format(self.mod_SN["double"], mdata["RunNumber"])

        data_out = tempfile.NamedTemporaryFile(
            "w", prefix=fnam, suffix=".dat", delete=False
        )
        data_out.write("{}\n".format(fnam))
        for key in items:
            if key == "Module_SN" or key == "Component":
                data_out.write("{}: {}\n".format(key, self.mod_SN["double"]))
            else:
                data_out.write("{}: {}\n".format(key, mdata[key]))

        for il, label in enumerate(mdata["curve"]["labels"]):
            if il:
                data_out.write("\t")
            data_out.write(label)
        data_out.write("\n")

        ncol = len(mdata["curve"]["labels"])
        ndata = len(self.difference)
        for i in range(ndata):
            v = -abs(V[i])
            iv = -abs(self.difference[i])
            if ncol > 2:
                data_out.write("{:.2f}\t{:.2f}\t{:.2f}\n".format(v, iv, 0.0))
            else:
                data_out.write("{:.2f}\t{:.2f}\n".format(v, iv))

        print(data_out.name)
        data_out.close()

        js_out = tempfile.NamedTemporaryFile(
            "w", prefix="payload-", suffix=".json", delete=False
        )
        js_out.write(json.dumps(test, indent=3, cls=dbGtkUtils.MyEncoder))
        js_out.close()

        if dbGtkUtils.ask_for_confirmation("Save Data File locally?", "Saves attached file also locally."):
            fc = Gtk.FileChooserDialog(title="Save data file", action=Gtk.FileChooserAction.SAVE)
            fc.add_buttons(
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN,
                Gtk.ResponseType.OK,
            )

            fc.set_current_name("{}.dat".format(fnam))
            rc = fc.run()
            if rc == Gtk.ResponseType.OK:
                shutil.copyfile(data_out.name, fc.get_filename())

            fc.hide()
            fc.destroy()

        attachment = ITkDButils.Attachment(data_out.name, "resultsFile", fnam)
        uploadW = UploadTest.UploadTest(self.session, js_out.name, attachment)
        uploadW.connect("destroy", remove_files, [data_out.name, js_out.name])

    def on_refresh(self, *args):
        """Refresh canvas."""
        if self.fig and self.canvas:
            self.fig.tight_layout()
            self.canvas.draw()

    def find_module(self, SN):
        """Find module (SN) on database

        Args:
            SN (str): Module Serial number.
            
        """
        md = ITkDButils.get_DB_component(self.session, SN)
        if md is None:
            dbGtkUtils.complain(
                "Could not find {}".format(SN), str(ITkDButils.get_db_response())
            )

        return md

    def on_single_file_set(self, *args):
        """File chosen."""
        obj_type = ["sensor", "module"]
        fnam = self.single_file.get_filename()
        if fnam is None or not Path(fnam).exists():
            dbGtkUtils.complain("Could not find data file", fnam, parent=self)

        mdata = self.read_file(fnam)

        is_module = 1
        try:
            SN = mdata["Module_SN"]
        except KeyError:
            SN = mdata["Component"]
            is_module = 0

        self.write_message("Reading data for {} {}\n".format(obj_type[is_module], SN))
        md = self.find_module(SN)
        if md is None:
            self.write_message("...object does not exist.\n")
            self.single_file.unselect_all()
            return

        # All good
        self.mod_SN["single"] = SN
        self.mdata["single"] = mdata
        self.mod_type["single"] = md["type"]["code"]
        print(self.mod_type["single"])

        self.single_SN.set_text("{} - {}".format(SN, md["type"]["name"]))
        self.fig.clf()
        self.show_curve(
            131,
            mdata["curve"]["V"],
            mdata["curve"]["I"],
            self.mod_type["single"][0:4] if is_module else "Single",
            mdata["curve"]["labels"][0],
            mdata["curve"]["labels"][1],
        )

    def on_double_file_set(self, *args):
        "File chosen for the 'double module'"
        obj_type = ["sensor", "module"]
        fnam = self.double_file.get_filename()
        if fnam is None or not Path(fnam).exists():
            dbGtkUtils.complain("Could not find data file", fnam, parent=self)

        mdata = self.read_file(fnam)
        is_module = 1
        # Check SN in data file
        try:
            SN = mdata["Module_SN"]
        except KeyError:
            is_module = 0
            SN = mdata["Component"]

        halfM_SN = SN
        if "single" in self.mod_SN:
            if self.mod_SN["single"] == SN:
                dbGtkUtils.complain(
                    "Wrong {}} SN", "{} already used.".format(obj_type[is_module], SN)
                )
                self.double_file.unselect_all()
                return

        # Check that it exists in the DB
        if len(SN) != 14 or SN[0:4] != "20US":
            self.write_message("Invalid SN: {}\n".format(SN))
            SN = dbGtkUtils.get_a_value(
                "Invalid SN", "Give Ring or corresponding Half Module SN"
            )

        self.write_message("Reading data for module {}\n".format(SN))
        md = self.find_module(SN)
        if md is None:
            self.write_message("...object does not exist.\n")
            self.double_file.unselect_all()
            return

        found_child = False
        if md["type"]["name"].find("Ring") >= 0:
            self.write_message("...This is a Ring module. Searching children in DB\n")
            for child in md["children"]:
                if child["component"]:
                    ctype = child["type"]["code"]
                    if ctype.find("MODULE") < 0:
                        continue

                    cSN = child["component"]["serialNumber"]
                    if cSN == self.mod_SN["single"]:
                        continue

                    halfM_SN = cSN
                    found_child = True
                    self.write_message("...found {}\n".format(halfM_SN))
                    break

            if not found_child:
                self.write_message("Requesting a Half Module SN\n")
                halfM_SN = dbGtkUtils.get_a_value(
                    "Give Half Module SN", "Serial Number"
                )

            md = ITkDButils.get_DB_component(self.session, halfM_SN)
            if md is None:
                dbGtkUtils.complain(
                    "Could not find {}".format(halfM_SN),
                    str(ITkDButils.get_db_response()),
                )
                self.double_file.unselect_all()
                return

            self.write_message("... {}\n".format(halfM_SN))

        if "single" in self.mod_type:
            if is_module and self.mod_type["single"] == md["type"]["code"]:
                dbGtkUtils.complain(
                    "Wrong module type.",
                    "Module type cannot be {}".format(self.mod_type["single"]),
                )

                self.double_file.unselect_all()
                return

        self.mod_SN["double"] = halfM_SN
        self.mod_type["double"] = md["type"]["code"]
        self.mdata["double"] = mdata

        self.double_SN.set_text("{} - {}".format(halfM_SN, md["type"]["name"]))
        self.show_curve(
            133,
            mdata["curve"]["V"],
            mdata["curve"]["I"],
            "Double",
            mdata["curve"]["labels"][0],
            None,
        )

        # Compute difference if single already available
        if "single" in self.mdata:
            self.on_difference()

    def on_difference(self, *args):
        """Compute difference."""
        if "single" not in self.mdata or "double" not in self.mdata:
            dbGtkUtils.complain(
                "Data needed", "Check if single oand doubel module data are available"
            )
            return

        is_module = "Module_SN" in self.mdata["double"]
        double_I = self.mdata["double"]["curve"]["I"]
        single_I = scale_iv(
            self.mdata["single"]["curve"]["I"],
            self.mdata["single"]["Temperature"] + 273.0,
            self.mdata["double"]["Temperature"] + 273.0,
        )

        try:
            nmin = double_I.size
            self.difference = double_I - single_I
        except ValueError:
            nmin = np.min([double_I.size, single_I.size])
            self.write_message(
                "Size of current arrays is not the same: {} {}\n".format(
                    double_I.size, single_I.size
                )
            )
            self.difference = double_I[:nmin] - single_I[:nmin]

        self.show_curve(
            132,
            self.mdata["double"]["curve"]["V"][:nmin],
            self.difference,
            self.mod_type["double"][0:4] if is_module else "Diff",
            self.mdata["double"]["curve"]["labels"][0],
            None,
        )

    def show_curve(self, subplot, X, Y, title=None, xlabel="X", ylabel="Y"):
        """Shows data"""
        ax = self.fig.add_subplot(subplot)
        plt.cla()
        if xlabel:
            ax.set_xlabel(xlabel)

        if ylabel:
            ax.set_ylabel(ylabel)

        if title:
            ax.set_title(title)

        ax.plot(X, Y)
        ax.grid()
        self.on_refresh()

    @staticmethod
    def read_file(fnam):
        """Read a data file. Return dictionary with all teh data."""
        labels = []
        metadata = {}
        with open(fnam, "r", encoding="utf-8") as ifile:
            first = True
            for line in ifile:
                if first:
                    first = False
                    ipos = line.rfind(".")
                    metadata["fname"] = line[:ipos]
                    continue

                if line.find("Voltage [V]") >= 0 or line.find("Voltage[V]") >= 0:
                    labels = line.split("\t")
                    break

                rc = line.find(":")
                if rc >= 0:
                    key = line[:rc].strip()
                    val = line[rc + 1 :].strip()
                    if key in ["Temperature", "Humidity"]:
                        metadata[key] = float(val)
                    else:
                        metadata[key] = val

            V = []
            I = []
            for line in ifile:
                data = [float(s) for s in line.split()]
                V.append(data[0])
                I.append(data[1])

            metadata["curve"] = {
                "V": np.abs(np.array(V)),
                "I": np.abs(np.array(I)),
                "labels": labels[0:2],
            }
            return metadata


def main():
    """Main entryy."""
    import sys

    # DB login
    dlg = ITkDBlogin.ITkDBlogin()
    client = dlg.get_client()
    if client is None:
        print("Could not connect to DB with provided credentials.")
        dlg.die()
        sys.exit()

    client.user_gui = dlg

    # Start the Application
    win = IVwindow(client)
    win.show_all()
    win.set_accept_focus(True)
    win.present()
    win.connect("destroy", Gtk.main_quit)

    try:
        Gtk.main()
    except KeyboardInterrupt:
        print("Arrggggg !!!")

    dlg.die()
    print("Bye !!")
    sys.exit()

if __name__ == "__main__":
    main()
