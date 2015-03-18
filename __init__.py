# -*- coding: utf-8 -*-
"""
/***************************************************************************
 tiss
                                 A QGIS plugin
 The plugin presents the tiss-indicatrix (quick-and-dirty Tissot-indicatrix realization) introduced by Szabó & Wirth.
The tiss-indicatrix uses circles of constant (in this case 800 kilometers) radius instead of the original infinitesimal circles.
We projects the tiss-circles from a reference sphere to a selected projection. The software uses On The Fly (OTF) transformation method.
Then we can study the distortions of the circles in a blink. The QGIS contains approximately 2 700 categorized projections.
Special thanks to Matyas Gede for his useful advises.
                             -------------------
        begin                : 2015-03-15
        copyright            : (C) 2015 by Ervin Wirth, Peter Kun
        email                : wirthervin@gmail.com, kunpeter01@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load tiss class from file tiss.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .indicatrix_mapper import tiss
    return tiss(iface)
