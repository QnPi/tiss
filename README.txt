How to use the plugin? First off all we have to mention do not use more, than plus or minus 90 degrees in the latitude field,by the way we hope you can't. Thus, at the latitude and longitude parameters, please fill the minimum and maximum values, like in a mesh grid. So we you You write 30 to minimum longitude and 90 to maximum with 1 inner point, then you will see three columns (30, 60, 90 degrees) as result. The -180 and 180 borders of longitude are come from the 360 degree circle, so you should not set a value out of this range. If you set 1 inner point in this case, it's calculated by a linear interpolation, so it took place at 0 (Greenwich meridian). The lines and circle segments means the preciseness of the circle and the axes (parallel of latitude, meridian line). By increasing their segment-value they are getting more precise, exact.

The radius parameter means the magnitude of projecting tiss circles. The term tiss (introduced by Szabó and Wirth) comes after Tissot.

Authors:

Ervin Wirth,
Technical University of Budapest, Photogrammetry and Geoinformatics Department, PhD student

Kun Peter,
Institute if Geodesy, Cartography and Remote Sensing, GIS developer
