#!/usr/bin/env python3
"""Test dashboard."""
import sys

try:
    import itkdb_gtk
    
except ImportError:
    from pathlib import Path
    cwd = Path(sys.argv[0]).parent.parent
    sys.path.append(cwd.as_posix())
    
    
from itkdb_gtk import dbGtkUtils
from itkdb_gtk import GetShipments
from itkdb_gtk import PetalReceptionTests
from itkdb_gtk import ITkDBlogin
from itkdb_gtk import CreateShipments
from itkdb_gtk import UploadTest
from itkdb_gtk import UploadMultipleTests
from itkdb_gtk import GlueWeight
from itkdb_gtk import UploadModuleIV
from itkdb_gtk import WireBondGui

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

HELP_LINK="https://itkdb-gtk.docs.cern.ch"

class DashWindow(dbGtkUtils.ITkDBWindow):
    """Dashboard class."""
    UPLOAD_TEST = 1
    UPLOAD_MANY_TESTS = 2
    CREATE_SHIPMNT = 3
    RECV_SHIPMNT = 4
    PETAL_GND = 5
    GLUE_WEIGHT = 6
    MOD_IV = 7
    WIRE_BOND = 8
    
    def __init__(self, session):
        """Initialization."""
        super().__init__(title="ITkDB Dashboard", session=session, help=HELP_LINK)
        self.mask = 0

        # set border width
        self.set_border_width(10)

        # Prepare dashboard
        lbl = Gtk.Label()
        lbl.set_markup("<big><b>ITkDB available commands.</b></big>")
        self.mainBox.pack_start(lbl, True, True, 0)

        grid = Gtk.Grid(column_spacing=5, row_spacing=5)
        self.mainBox.pack_start(grid, False, True, 5)

        irow = 0
        lbl = Gtk.Label()
        lbl.set_markup("<b>Tests</b>")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, irow, 1, 1)

        irow += 1
        btnTest = Gtk.Button(label="Upload Single Test")
        btnTest.connect("clicked", self.upload_test)
        grid.attach(btnTest, 0, irow, 1, 1)

        btnTest = Gtk.Button(label="Upload Multiple Tests")
        btnTest.connect("clicked", self.upload_multiple_tests)
        grid.attach(btnTest, 1, irow, 1, 1)

        irow += 1
        btnGnd = Gtk.Button(label="Petal Reception")
        btnGnd.connect("clicked", self.petal_gnd)
        grid.attach(btnGnd, 0, irow, 1, 1)

        btnWeight = Gtk.Button(label="GlueWeight")
        btnWeight.connect("clicked", self.glue_weight)
        grid.attach(btnWeight, 1, irow, 1, 1)

        irow += 1
        btnModIV = Gtk.Button(label="Sensor/Module IV")
        btnModIV.connect("clicked", self.module_IV)
        grid.attach(btnModIV, 0, irow, 1, 1)

        btnWireBond = Gtk.Button(label="Wire Bond")
        btnWireBond.connect("clicked", self.wire_bond)
        grid.attach(btnWireBond, 1, irow, 1, 1)



        irow += 1
        grid.attach(Gtk.Label(), 0, irow, 1, 1)

        irow += 1
        lbl = Gtk.Label()
        lbl.set_markup("<b>Shipments</b>")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, irow, 1, 1)

        irow += 1
        sendS = Gtk.Button(label="Create Shipment")
        sendS.connect("clicked", self.create_shipment)
        grid.attach(sendS, 0, irow, 1, 1)

        recS = Gtk.Button(label="Receive Shipment")
        recS.connect("clicked", self.receive_shipment)
        grid.attach(recS, 1, irow, 1, 1,)

        self.mainBox.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, True, 5)

        self.show_all()

    def upload_test(self, *args):
        """Launch upload test."""
        bitn = DashWindow.UPLOAD_TEST
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = UploadTest.UploadTest(self.session, help=HELP_LINK)
        W.connect("destroy", self.app_closed, bitn)

    def upload_multiple_tests(self, *args):
        """Launch upload multiple test."""
        bitn = DashWindow.UPLOAD_MANY_TESTS
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = UploadMultipleTests.UploadMultipleTests(self.session, help=HELP_LINK)
        W.connect("destroy", self.app_closed, bitn)

    def create_shipment(self, *args):
        """Launch createShipment."""
        bitn = DashWindow.CREATE_SHIPMNT
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = CreateShipments.CreateShipments(self.session, help=HELP_LINK)
        W.connect("destroy", self.app_closed, bitn)

    def receive_shipment(self, *args):
        """Launch getShipments."""
        bitn = DashWindow.RECV_SHIPMNT
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = GetShipments.ReceiveShipments(self.session, help=HELP_LINK)
        W.connect("destroy", self.app_closed, bitn)

    def petal_gnd(self, *args):
        """Petal GND/VI test."""
        bitn = DashWindow.PETAL_GND
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = PetalReceptionTests.PetalReceptionTests(self.session, help=HELP_LINK)
        W.connect("destroy", self.app_closed, bitn)

    def glue_weight(self, *args):
        """Glue Weight test."""
        bitn = DashWindow.GLUE_WEIGHT
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = GlueWeight.GlueWeight(self.session, help=HELP_LINK)
        W.connect("destroy", self.app_closed, bitn)

    def module_IV(self, *args):
        """Module IV tests."""
        bitn = DashWindow.MOD_IV
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = UploadModuleIV.IVwindow(self.session, help=HELP_LINK)
        W.connect("destroy", self.app_closed, bitn)

    def wire_bond(self, *args):
        """Module IV tests."""
        bitn = DashWindow.WIRE_BOND
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = WireBondGui.WireBond(session=self.session, title="Wirebond", help=HELP_LINK)
        W.connect("destroy", self.app_closed, bitn)

    def app_closed(self, *args):
        """Application window closed. Clear mask."""
        bt = 1 << args[1]
        self.mask &= ~bt
        # print(bt, self.mask)


def main():
    # DB login
    dlg = ITkDBlogin.ITkDBlogin()
    client = dlg.get_client()
    if client is None:
        print("Could not connect to DB with provided credentials.")
        dlg.die()
        sys.exit()

    client.user_gui = dlg

    dashW = DashWindow(client)
    dashW.connect("destroy", Gtk.main_quit)
    try:
        Gtk.main()

    except KeyboardInterrupt:
        print("Arrrgggg!!!")

    dlg.die()


if __name__ == "__main__":
    main()
