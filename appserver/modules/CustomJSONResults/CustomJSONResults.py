#
# Splunk UI module python renderer
# This module is imported by the module loader (lib.module.ModuleMapper) into
# the splunk.appserver.mrsparkle.controllers.module.* namespace.
#

import cherrypy
import controllers.module as module

import splunk, splunk.search, splunk.util, splunk.entity
import json
from splunk.appserver.mrsparkle.lib import jsonresponse
import lib.util as util
import lib.i18n as i18n

import logging
logger = logging.getLogger('splunk.module.CustomJSONResults')

import math
import cgi



class CustomJSONResults(module.ModuleHandler):
    
    def generateResults(self, host_app, client_app, sid, count=10000, 
            offset=0, entity_name='results'):

        count = max(int(count), 0)
        offset = max(int(offset), 0)
        if not sid:
            raise Exception('CustomJSONResults.generateResults - sid not passed!')

        try:
            job = splunk.search.getJob(sid)
        except splunk.ResourceNotFound, e:
            logger.error('CustomJSONResults could not find the job %s. Exception: %s' % (sid, e))
            return _('<p class="resultStatusMessage">Could not retrieve search data.</p>')
        
        fieldNames = [ '_time', 'LatLong', 'Speed__OBD' ]
        
        dataset = getattr(job, entity_name)[offset: offset+count]

        outputKML = []

        # 0  - 20      blueLine
        # 20 - 40      greenLine
        # 40 - 65      orangeLine
        # 65 - 80      redLine
        # 80 +         purpleLine

        outputPlacemarkPoints = []
        outputPlacemarkColors = [ '#0000FF' ]
        outputPlacemarkTmp = []
        currentColor = "#0000FF"
        thisColor    = "#0000FF"


          # var flightPlanCoordinates = [
          #     new google.maps.LatLng(37.772323, -122.214897),
          #     new google.maps.LatLng(21.291982, -157.821856),
          #     new google.maps.LatLng(-18.142599, 178.431),
          #     new google.maps.LatLng(-27.46758, 153.027892)
          # ];
          # var flightPath = new google.maps.Polyline({
          #   path: flightPlanCoordinates,
          #   strokeColor: '#FF0000',
          #   strokeOpacity: 1.0,
          #   strokeWeight: 2
          # });


        outputJSON = []
        firstPointPosted = True
        firstPoint = ""
        latlong = ""
        for i, result in enumerate(dataset):
            


            latlong = str(result.get("LatLong",None))

            if latlong == "0.0,0.0":
                continue

            latlong = "new google.maps.LatLng(" + latlong + ")"
            speed = float(str(result.get("Speed__OBD",0)))


            if firstPointPosted:
                firstPointPosted = False
                firstPoint = latlong
                #outputKML.append("this.map.setCenter(" + latlong + ");\n")
                outputKML.append("""
                    var startPoint = new google.maps.Marker({
                        position: %s,
                        map: this.map,
                        title: "Trip Start"
                    });
                """ % latlong)


            if speed < 20:
                thisColor = "#6bb7c8" # blue
            elif speed < 40:
                thisColor = "#fac61d" # yellow
            elif speed < 70:
                thisColor = "#7fac61" # green
            elif speed < 90:
                thisColor = "#d85e3d" # red
            else:
                thisColor = "#956e96" # purple


            if thisColor == currentColor:
                outputPlacemarkTmp.append(latlong)
            else:
                # build out and append a Placemark group
                outputPlacemarkTmp.append(latlong)

                outputKML.append("""
                    var tmp = new google.maps.Polyline({
                        path: [%s],
                        strokeColor: '%s',
                        strokeOpacity: 1,
                        strokeWeight: 7
                    });
                    tmp.setMap(this.map);
                """ % (', '.join(outputPlacemarkTmp), currentColor ))

                del outputPlacemarkTmp[:]
                outputPlacemarkTmp = []
                outputPlacemarkTmp.append(latlong)
                currentColor = thisColor

        if outputPlacemarkTmp:
                outputKML.append("""
                    var tmp = new google.maps.Polyline({
                        path: [%s],
                        strokeColor: '%s',
                        strokeOpacity: 0.9,
                        strokeWeight: 7
                    });
                    tmp.setMap(this.map);
                """ % (', '.join(outputPlacemarkTmp), currentColor ))




        outputKML.append("""
            var endPoint = new google.maps.Marker({
                position: %s,
                map: this.map,
                title: "Trip End"
            });

            var boundList = new Array(%s, %s);
            var bounds = new google.maps.LatLngBounds();
            for (var i = 0, LtLgLen = boundList.length; i < LtLgLen; i++) {
                bounds.extend(boundList[i]);
            }

            this.map.fitBounds(bounds);

        """ % (latlong, firstPoint, latlong))


            # For building JSON Output
            # tmpDict = {}
            # for field in fieldNames:
            #     fieldValue = result.get(field, None)
            #     tmpDict[str(field)] = str(fieldValue)

            # outputJSON.append(tmpDict)


        cherrypy.response.headers['Content-Type'] = 'text/plain'
        #return json.dumps(outputJSON, sort_keys=True, indent=2)
        return  "\n\n".join(outputKML) 
#        return self.render_json(outputJSON)
        
    def render_json(self, response_data, set_mime='text/json'):
        cherrypy.response.headers['Content-Type'] = set_mime

        if isinstance(response_data, jsonresponse.JsonResponse):
            response = response_data.toJson().replace("</", "<\\/")
        else:
            response = json.dumps(response_data).replace("</", "<\\/")

        # Pad with 256 bytes of whitespace for IE security issue. See SPL-34355
        return ' ' * 256  + '\n' + response

