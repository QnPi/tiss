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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from indicatrix_mapper_dialog_base import Ui_Tiss
import numpy

#FORM_CLASS, _ = uic.loadUiType(os.path.join(
 #   os.path.dirname(__file__), 'indicatrix_mapper_dialog_base.ui'))


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
        self.FunAllSignals()
        self.FunInputs()



    def FunAllSignals(self):
        self.connect(self.btnRun, SIGNAL("clicked()"), self.FunExecute)

    def FunInputs(self):
        # circle parameters
        self.res =  self.spbCircleSeg.value() # circle segments no.
        self.resl = self.spbLineSeg.value() # line segments no.
        self.radius = self.spbRadius.value() # tiss circle radius
        self.R = 6371.007 # sphere radius, constant
        # latitude resolution 
        self.maxlat = self.spbLatMax.value() 
        self.minlat = self.spbLatMin.value() 
        self.innerplat = self.spbLatRes.value()
        # longitude resolution
        self.minlon = self.spbLongMin.value() 
        self.maxlon = self.spbLongMax.value() 
        self.innerplon =  self.spbLongRes.value() 
            
    def FunExecute(self):
        self.FunInputs()
        self.FunAddTissCircleLayer()
        self.FunAddTissLineLayer()
        

    def FunAddTissCircleLayer(self):
        # create layer
        self.vl = QgsVectorLayer("Polygon?crs=epsg:4047", "circles", "memory")
        self.pr = self.vl.dataProvider()
        # changes are only possible when editing the layer
        self.vl.startEditing()
        # add fields
        self.pr.addAttributes([QgsField("lon", QVariant.Double),QgsField("lat", QVariant.Double)])
        #calculate polygons
        self.FunCalcTissCircles()
        # commit to stop editing the layer
        self.vl.commitChanges()
        # update layer's extent when new features have been added
        # because change of extent in provider is not propagated to the layer
        self.vl.updateExtents()
        # add layer to the legend
        QgsMapLayerRegistry.instance().addMapLayer(self.vl)

    def FunAddTissLineLayer(self):
	# create layer
	self.vl = QgsVectorLayer("LineString?crs=epsg:4047", "lines", "memory")
	self.pr = self.vl.dataProvider()
	# changes are only possible when editing the layer
	self.vl.startEditing()
	# add fields
	self.pr.addAttributes([QgsField("lon", QVariant.Double),QgsField("lat", QVariant.Double)])
	#calculate tiss lines
	self.FunCalcTissLines()
	# commit to stop editing the layer
	self.vl.commitChanges()
	# update layer's extent when new features have been added
	# because change of extent in provider is not propagated to the layer
	self.vl.updateExtents()
	# add layer to the legend
	QgsMapLayerRegistry.instance().addMapLayer(self.vl)

    def FunCalcTissCircles(self):
        # set up inner points
        latlist = numpy.linspace(self.minlat, self.maxlat, num = (self.innerplat+2))
        lonlist = numpy.linspace(self.minlon, self.maxlon, num = (self.innerplon+2))
        # arc of the radius on sphere
        r = self.radius/self.R
        # calculate half circle arc with given resolution
        alfalist = list(numpy.linspace(0, numpy.pi, num = self.res, endpoint = False))
        alfalist.pop(0)
        for lons in lonlist:
            for lats in latlist:
                lon = lons
                lat =  lats
                tlon = numpy.radians(lon)
                tlat = numpy.radians(lat)
                t0 =  numpy.pi/2 - tlat
                rightlist = []
                leftlist = []
                mergedlist = []
                startPoint  = []
                middlePoint  = []
                for alfa in alfalist:
                    # calculating the latitudes
                    tpf = numpy.arccos( numpy.cos(r)*numpy.cos(t0)+numpy.sin(r)*numpy.sin(t0)*numpy.cos(alfa) )
                    dFi = numpy.degrees(t0-tpf)
                    # calculating the longitudes
                    dLambda = numpy.degrees(numpy.arccos( (numpy.cos(r) - numpy.cos(t0) * numpy.cos(tpf)) / (numpy.sin(t0) * numpy.sin(tpf))))
                    rightlist.append(QgsPoint(lon+dLambda,lat+dFi))
                    leftlist.append(QgsPoint(lon-dLambda,lat+dFi))
                leftlist.reverse()
                startPoint.append(QgsPoint(lon,lat+numpy.degrees(r)))
                middlePoint.append(QgsPoint(lon,lat-numpy.degrees(r)))
                mergedlist = list(startPoint + rightlist + middlePoint + leftlist )
                
                # add a feature
                fet = QgsFeature()
                fet.setGeometry(QgsGeometry.fromPolygon([mergedlist]))
                fet.setAttributes([float(lon), float(lat)])
                self.pr.addFeatures([fet])


    def FunCalcTissLines(self):
        # set up inner points
        latlist = numpy.linspace(self.minlat, self.maxlat, num = (self.innerplat+2))
        lonlist = numpy.linspace(self.minlon, self.maxlon, num = (self.innerplon+2))
        r = self.radius/self.R
        for lons in lonlist:
            for lats in latlist:
                lon = lons
                lat = lats
                tlon = numpy.radians(lon)
                tlat = numpy.radians(lat)
                ## creating line features
                # calculate horizontal limit
                lres = self.resl
                vlinelist = list(numpy.linspace((lat-numpy.degrees(r)), (lat+numpy.degrees(r)), num = lres))
                # parallel circle
                parallelRadius = numpy.cos(tlat)*self.R
                hlinelist = list(numpy.linspace((lon - numpy.degrees(self.radius/parallelRadius)), (lon + numpy.degrees(self.radius/parallelRadius)), num = lres))
                vlist = []
                hlist = []
                for v in vlinelist:
                    vlist.append(QgsPoint(lon,v))
                for h in hlinelist:
                    hlist.append(QgsPoint(h,lat))
                fetv = QgsFeature()
                feth = QgsFeature()
                fetv.setGeometry(QgsGeometry.fromPolyline(vlist))
                feth.setGeometry(QgsGeometry.fromPolyline(hlist))
                fetv.setAttributes([float(lon), float(lat)])
                feth.setAttributes([float(lon), float(lat)])
                self.pr.addFeatures([fetv])
                self.pr.addFeatures([feth])


        
