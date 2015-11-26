# -*- coding: utf-8 -*-
"""
/***************************************************************************
 tissDialog
                                 A QGIS plugin
 The plugin presents the tiss-indicatrix (quick-and-dirty Tissot-indicatrix realization) introduced by Szabó & Wirth.
The tiss-indicatrix uses circles of constant (in this case 800 kilometers) radius instead of the original infinitesimal circles.
We projects the tiss-circles from a reference sphere to a selected projection. The software uses On The Fly (OTF) transformation method.
Then we can study the distortions of the circles in a blink. The QGIS contains approximately 2 700 categorized projections.
Special thanks to Matyas Gede for his useful advises.
                             -------------------
        begin                : 2015-03-15
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Ervin Wirth, Peter Kun
        email                : wirthervin@gmail.com, kunpeter01@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from indicatrix_mapper_dialog_base import Ui_Tiss
import numpy

# FORM_CLASS, _ = uic.loadUiType(os.path.join(
# os.path.dirname(__file__), 'indicatrix_mapper_dialog_base.ui'))


class tissDialog(QDialog, Ui_Tiss):
    def __init__(self):
        """Constructor."""
        QDialog.__init__(self)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.ui = Ui_Tiss()
        self.all_signals()
        self.inputs()
        self.spbRadiusDg.setValue(6)

    def all_signals(self):
        self.connect(self.btnRun, SIGNAL("clicked()"), self.fun_execute)
        self.connect(self.spbRadiusDg, SIGNAL("valueChanged(double)"), self.deg_to_km)
        self.connect(self.spbRadiusKm, SIGNAL("valueChanged(double)"), self.km_to_deg)
        self.connect(self.spbLongMin, SIGNAL("valueChanged(double)"), self.min_lon_change)
        self.connect(self.spbLongMax, SIGNAL("valueChanged()"), self.max_lon_change)
        self.connect(self.spbLatMin, SIGNAL("valueChanged()"), self.min_lat_change)
        self.connect(self.spbLatMax, SIGNAL("valueChanged()"), self.max_lat_change)

    def inputs(self):
        # circle parameters
        self.res = self.spbCircleSeg.value()  # circle segments no.
        self.resl = self.spbLineSeg.value()  # line segments no.
        self.radius = self.spbRadiusKm.value()  # tiss circle radius
        self.R = float(self.spbRadius.value()) / 1000  # sphere radius, constant
        # R = 6372.200 # in case of unknown radii you have to create the layer twice...
        # R = 6371.007
        # latitude resolution
        self.maxlat = self.spbLatMax.value()
        self.maxlat2 = self.spbLatMax_2.value()
        self.minlat = self.spbLatMin.value()
        self.minlat2 = self.spbLatMin_2.value()
        self.innerplat = self.spbLatRes.value()
        self.innerplat2 = self.spbLatRes_2.value()
        # longitude resolution
        self.minlon = self.spbLongMin.value()
        self.minlon2 = self.spbLongMin_2.value()
        self.maxlon = self.spbLongMax.value()
        self.maxlon2 = self.spbLongMax_2.value()
        self.innerplon = self.spbLongRes.value()
        self.innerplon2 = self.spbLongRes_2.value()
        # poles checkbox
        self.npolep = self.chkBoxNPole.isChecked()
        self.spolep = self.chkBoxSPole.isChecked()
        self.auxp = self.chkBoxAux.isChecked()
		

    def km_to_deg(self):
        dg = self.spbRadiusKm.value() / (2 * self.R * numpy.pi) * 360
        self.spbRadiusDg.setValue(dg)

    def deg_to_km(self):
        self.spbLatRes.setMinimum(self.spbRadiusDg.value() * 2)
        self.spbLongRes.setMinimum(self.spbRadiusDg.value() * 2)
        # calculate kilometer field
        km = self.spbRadiusDg.value() / 360 * 2 * self.R * numpy.pi
        self.spbRadiusKm.setValue(km)
        self.spbLatMax.setMaximum(90 - self.spbRadiusDg.value())
        self.spbLatMin.setMinimum(-90 + self.spbRadiusDg.value())

    def max_lat_change(self):
        self.spbLatMin.setMaximum(self.spbLatMax.value() - 1)

    def min_lat_change(self):
        self.spbLatMax.setMinimum(self.spbLatMin.value() + 1)

    def max_lon_change(self):
        self.spbLongMin.setMaximum(self.spbLongMax.value() - 1)

    def min_lon_change(self):
        QMessageBox.information(None, "DEBUG:", str(self.spbLongMax.Minimum()))
        self.spbLongMax.setMinimum(self.spbLongMin.value() + 1)

    def fun_execute(self):
        self.inputs()
        self.tiss_circle_layer()
        self.tiss_line_layer()

    def tiss_circle_layer(self):
        # Create projection
        wkt = 'GEOGCS["unnamed ellipse",DATUM["unknown",SPHEROID["unnamed",' + str(
            int(self.R * 1000)) + ',0]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
        # Sometimes (new R) you have to reset the USER:X CRS to the layer...
        self.vl = QgsVectorLayer("Polygon?crs=" + wkt, "tisses", "memory")
        self.vl2 = QgsVectorLayer("MultiPoint?crs=" + wkt, "auxpoints", "memory")
        self.pr = self.vl.dataProvider()
        self.pr2 = self.vl2.dataProvider()
        # changes are only possible when editing the layer
        self.vl.startEditing()
        self.vl2.startEditing()
        # add fields
        self.pr.addAttributes([QgsField("lon", QVariant.Double), QgsField("lat", QVariant.Double)])
        self.pr2.addAttributes([QgsField("lon", QVariant.Double), QgsField("lat", QVariant.Double)])
        # calculate polygons
        self.tiss_circles()
        # here we need a switch about poles, then function called
        if self.npolep:
            self.tiss_north_pole()
        if self.spolep:
            self.tiss_south_pole()
        if self.auxp:
            self.vl2.commitChanges()
            self.vl2.updateExtents()
            mNoSimplification = QgsVectorSimplifyMethod()
            mNoSimplification.setSimplifyHints(QgsVectorSimplifyMethod.NoSimplification)
            self.vl2.setSimplifyMethod(mNoSimplification)
            QgsMapLayerRegistry.instance().addMapLayer(self.vl2)
        # commit to stop editing the layer
        self.vl.commitChanges()
        # update layer's extent when new features have been added
        # because change of extent in provider is not propagated to the layer
        self.vl.updateExtents()
        # no simplify
        mNoSimplification = QgsVectorSimplifyMethod()
        mNoSimplification.setSimplifyHints(QgsVectorSimplifyMethod.NoSimplification)
        self.vl.setSimplifyMethod(mNoSimplification)
        # add layer to the legend
        QgsMapLayerRegistry.instance().addMapLayer(self.vl)

    def tiss_line_layer(self):
        # Create projection
        wkt = 'GEOGCS["unnamed ellipse",DATUM["unknown",SPHEROID["unnamed",' + str(
            int(self.R * 1000)) + ',0]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
        # Sometimes (new R) you have to reset the USER:X CRS to the layer...
        self.vl = QgsVectorLayer("LineString?crs=" + wkt, "graticule", "memory")
        self.pr = self.vl.dataProvider()
        # changes are only possible when editing the layer
        self.vl.startEditing()
        self.pr.addAttributes([QgsField("lon", QVariant.Double), QgsField("lat", QVariant.Double)])
        # calculate tiss lines
        self.tiss_lines()
        # commit to stop editing the layer
        self.vl.commitChanges()
        # update layer's extent when new features have been added
        # because change of extent in provider is not propagated to the layer
        self.vl.updateExtents()
        # no simplify
        mNoSimplification = QgsVectorSimplifyMethod()
        mNoSimplification.setSimplifyHints(QgsVectorSimplifyMethod.NoSimplification)
        self.vl.setSimplifyMethod(mNoSimplification)
        # add layer to the legend
        QgsMapLayerRegistry.instance().addMapLayer(self.vl)

    def tiss_north_pole(self):
        deg = self.radius / (self.R * numpy.pi) * 180
        lonlist = list(numpy.linspace(-180, 180, num=self.res))
        # north pole
        pointlist = []
        for lon in lonlist:
            pointlist.append(QgsPoint(lon, 90 - deg))
        # add a feature
        fet = QgsFeature()
        fet.setGeometry(QgsGeometry.fromPolygon([pointlist]))
        fet.setAttributes([float(-1), float(90)])
        self.pr.addFeatures([fet])

    def tiss_south_pole(self):
        deg = self.radius / (self.R * numpy.pi) * 180
        lonlist = list(numpy.linspace(-180, 180, num=self.res))
        # south pole
        pointlist = []
        for lon in lonlist:
            pointlist.append(QgsPoint(lon, - 90 + deg))
        # add a feature
        fet = QgsFeature()
        fet.setGeometry(QgsGeometry.fromPolygon([pointlist]))
        fet.setAttributes([float(-1), float(90)])
        self.pr.addFeatures([fet])

    def tiss_circles(self):
        # set up inner points
        latlist = range(self.minlat, self.maxlat + self.innerplat, self.innerplat)
        lonlist = range(self.minlon, self.maxlon + self.innerplat, self.innerplon)
        # arc of the radius on sphere
        r = self.radius / self.R
        # calculate half circle arc with given resolution
        alfalist = list(numpy.linspace(0, numpy.pi, num=self.res, endpoint=False))
        alfalist.pop(0)
        for lon in lonlist:
            for lat in latlist:
                t0 = numpy.pi / 2 - numpy.radians(lat)
                rightlist = []
                leftlist = []
                startpoint = []
                middlePoint = []
                for alfa in alfalist:
                    # calculating the latitudes with spherical law of cosines
                    tpf = numpy.arccos(numpy.cos(r) * numpy.cos(t0) + numpy.sin(r) * numpy.sin(t0) * numpy.cos(alfa))
                    dFi = numpy.degrees(tpf)
                    # calculating the longitudes with spherical law of sines
                    dLambda = numpy.degrees(numpy.arcsin(numpy.sin(alfa) * numpy.sin(r) / numpy.sin(tpf)))
                    rightlist.append(QgsPoint(lon + dLambda, 90 - dFi))
                    leftlist.append(QgsPoint(lon - dLambda, 90 - dFi))
                leftlist.reverse()
                startpoint.append(QgsPoint(lon, lat + numpy.degrees(r)))
                middlePoint.append(QgsPoint(lon, lat - numpy.degrees(r)))
                mergedlist = list(startpoint + rightlist + middlePoint + leftlist)
                # add a feature
                fet = QgsFeature()
                fet2 = QgsFeature()
                fet.setGeometry(QgsGeometry.fromPolygon([mergedlist]))
                fet2.setGeometry(QgsGeometry.fromMultiPoint(mergedlist))
                fet.setAttributes([float(lon), float(lat)])
                fet2.setAttributes([float(lon), float(lat)])
                self.pr.addFeatures([fet])
                self.pr2.addFeatures([fet2])

    def tiss_lines(self):
        # set up inner points
        latlist = range(self.minlat2, self.maxlat2 +  self.innerplat2, self.innerplat2)
        lonlist = range(self.minlon2, self.maxlon2 + self.innerplat2, self.innerplon2)
        lres = self.resl
        for lon in lonlist:
            vlinelist = list(numpy.linspace(self.minlat2, self.maxlat2, num=lres))
            vlist = []
            for v in vlinelist:
                vlist.append(QgsPoint(lon, v))
            fetv = QgsFeature()
            fetv.setGeometry(QgsGeometry.fromPolyline(vlist))
            fetv.setAttributes([float(lon), float(0)])
            self.pr.addFeatures([fetv])
        for lat in latlist:
            vlinelist = list(numpy.linspace(self.minlon2, self.maxlon2, num=lres))
            vlist = []
            for v in vlinelist:
                vlist.append(QgsPoint(v, lat))
            fetv = QgsFeature()
            fetv.setGeometry(QgsGeometry.fromPolyline(vlist))
            fetv.setAttributes([float(0), float(lat)])
            self.pr.addFeatures([fetv])