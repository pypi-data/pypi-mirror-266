/* We want to override JB.Map to add our own maps instead.
 * We do this by (ab)using the JS property system to override the setter, so
 * that JB.Map won't actually set the new function. This means we don't have to
 * source-patch the gmutils.js file.
 */
"use strict";

(() => {
    let ourMap = function(makemap) {
        var dieses = this;
        var id = makemap.id;
        var mapcanvas = makemap.mapdiv;
        dieses.id = id;
        dieses.makemap = makemap;
        dieses.mapcanvas = mapcanvas;
        this.cluster_zoomhistory = [];

        // The change function is doing weird things and expects the OSM layer
        // to be there, which leads to exceptions and the map not working at
        // all if the OSM layer is disabled. We fix this by simply not caring
        // about the change function.
        // See https://gitlab.com/dunj3/fietsboek/-/issues/27
        this.change = (_) => {};

        // Map anlegen

        const mycp = '<a href="https://www.j-berkemeier.de/GPXViewer" title="GPX Viewer '+JB.GPX2GM.ver+'">GPXViewer</a> | ';

        this.baseLayers = {};
        this.overlayLayers = {};

        for (let layer of TILE_LAYERS) {
            if (layer.type === "base") {
                this.baseLayers[layer.name] = L.tileLayer(layer.url, {
                    maxZoom: layer.zoom,
                    attribution: layer.attribution,
                });
            } else if (layer.type === "overlay") {
                this.overlayLayers[layer.name] = L.tileLayer(layer.url, {
                    attribution: layer.attribution,
                });
            }
        }

        // https://tileserver.4umaps.com/${z}/${x}/${y}.png
        // zoomlevel 16
        // https://www.4umaps.com/

        this.baseLayers[JB.GPX2GM.strings[JB.GPX2GM.parameters.doclang].noMap]= L.tileLayer(JB.GPX2GM.Path+"Icons/Grau256x256.png", { 
            maxZoom: 22,
            attribution: mycp
        });

        this.layerNameTranslate = {
            satellit: "Satellit",
            satellite: "Satellit",
            osm: "OSM",
            osmde: "OSMDE",
            opentopo: "Open Topo",
            topplusopen: "TopPlusOpen",
            cycle: "Cycle",
            landscape: "Landscape",
            outdoors: "Outdoors",
            keinekarte: "Keine Karte",
            pasdecarte: "Pas de carte",
            nomap: "No Map",
            ning\u00FAnmapa: "Ning\u00FAn Mapa",
            nessunamappa: "Nessuna mappa",
            opensea: "Open Sea",
            hiking: "Hiking",
            cycling: "Cycling",
        }

        // ['hiking', 'cycling', 'mtb', 'skating', 'slopes', 'riding'];

        var genugplatz = JB.platzgenug(makemap.mapdiv);

        this.map = L.map(mapcanvas, { 
            //		layers: osm, 
            closePopupOnClick: false,
            scrollWheelZoom: genugplatz & makemap.parameters.scrollwheelzoom,
            tap: genugplatz,
            keyboard: genugplatz,
            touchZoom: true,
            dragging: true,
            // Make sure we get the first layer in there
            layers: Object.values(this.baseLayers)[0],
        } );

        JB.handle_touch_action(dieses,genugplatz);

        if(makemap.parameters.unit=="si") L.control.scale({imperial:false}).addTo(this.map); // Mit Maßstab km
        else L.control.scale({metric:false}).addTo(this.map); // Mit Maßstab ml

        var ctrl_layer = null;
        var showmaptypecontroll_save = makemap.parameters.showmaptypecontroll;
        JB.onresize(mapcanvas,function(w,h) {
            makemap.parameters.showmaptypecontroll = (w>200 && h>190 && showmaptypecontroll_save);
            if(makemap.parameters.showmaptypecontroll) {
                if(!ctrl_layer) ctrl_layer = L.control.layers(dieses.baseLayers, dieses.overlayLayers).addTo(dieses.map);
            }
            else {
                if(ctrl_layer) {
                    ctrl_layer.remove();
                    ctrl_layer = null;
                }
            }
        },true);

        // Button für Full Screen / normale Größe
        var fullscreen = false;
        if(makemap.parameters.fullscreenbutton) {
            var fsb = document.createElement("button");
            fsb.style.backgroundColor = "transparent";
            fsb.style.border = "none"; 
            fsb.style.padding = "7px 7px 7px 0";
            fsb.style.cursor = "pointer";
            var fsbim = document.createElement("img");
            fsbim.width = 31;
            fsbim.height = 31;
            fsbim.src = JB.GPX2GM.Path+"Icons/fullscreen_p.svg";
            fsb.title = fsbim.title = fsbim.alt = JB.GPX2GM.strings[JB.GPX2GM.parameters.doclang].fullScreen;
            fsbim.large = false;
            var ele = mapcanvas.parentNode;
            fsb.onclick = function() {
                this.blur();
                if(fsbim.large) {
                    document.body.style.overflow = "";
                    fsbim.src = JB.GPX2GM.Path+"Icons/fullscreen_p.svg";
                    fsb.title = fsbim.title = fsbim.alt = JB.GPX2GM.strings[JB.GPX2GM.parameters.doclang].fullScreen;
                    ele.style.left = ele.oleft + "px";
                    ele.style.top = ele.otop + "px";
                    ele.style.width = ele.owidth + "px";
                    ele.style.height = ele.oheight + "px";
                    ele.style.margin = ele.omargin;
                    ele.style.padding = ele.opadding;
                    window.setTimeout(function() {
                        JB.removeClass("JBfull",ele);
                        ele.style.position = ele.sposition; 
                        ele.style.left = ele.sleft;
                        ele.style.top = ele.stop;
                        ele.style.width = ele.swidth;
                        ele.style.height = ele.sheight;
                        //ele.style.zIndex = ele.szindex;
                    },1000);
                    JB.handle_touch_action(dieses,genugplatz);
                    fullscreen = false;
                }
                else {
                    document.body.style.overflow = "hidden";
                    fsbim.src = JB.GPX2GM.Path+"Icons/fullscreen_m.svg";
                    fsb.title = fsbim.title = fsbim.alt = JB.GPX2GM.strings[JB.GPX2GM.parameters.doclang].normalSize;
                    var scrollY = 0;
                    if(document.documentElement.scrollTop && document.documentElement.scrollTop!=0)  scrollY = document.documentElement.scrollTop;
                    else if(document.body.scrollTop && document.body.scrollTop!=0)  scrollY = document.body.scrollTop;
                    else if(window.scrollY) scrollY = window.scrollY;
                    else if(window.pageYOffset) scrollY = window.pageYOffset;
                    var rect = JB.getRect(ele);
                    ele.oleft = rect.left;
                    ele.otop =  rect.top - scrollY;
                    ele.owidth = rect.width;
                    ele.oheight = rect.height;
                    //ele.szindex = ele.style.zIndex;
                    ele.sposition = ele.style.position;
                    ele.omargin = ele.style.margin;
                    ele.opadding = ele.style.padding;
                    ele.sleft = ele.style.left;
                    ele.stop = ele.style.top;
                    ele.swidth = ele.style.width;
                    ele.sheight = ele.style.height;
                    ele.style.position = "fixed";
                    ele.style.left = ele.oleft+"px";
                    ele.style.top = ele.otop+"px";
                    ele.style.width = ele.owidth+"px";
                    ele.style.height = ele.oheight+"px";
                    //ele.style.zIndex = "1001";
                    window.setTimeout(function() {
                        JB.addClass("JBfull",ele);
                        ele.style.width = "100%";
                        ele.style.height = "100%";
                        ele.style.left = "0px";
                        ele.style.top = "0px";
                        ele.style.margin = "0px";
                        ele.style.padding = "0px";
                    },100);
                    dieses.map.scrollWheelZoom.enable();
                    JB.handle_touch_action(dieses,true);
                    makemap.mapdiv.focus();
                    fullscreen = true;
                }
                fsbim.large = !fsbim.large;
            };
            fsb.appendChild(fsbim);
            fsb.index = 0;
            L.Control.Fsbutton = L.Control.extend({
                onAdd: function(map) {
                    return fsb;
                }
            });
            var fsbutton = new L.Control.Fsbutton({ position: 'topright' });
            fsbutton.addTo(this.map);
        } // fullscreenbutton

        // Button für Traffic-Layer
        if(makemap.parameters.trafficbutton) {
            console.warn("Traffic-Layer wird unter Leaflet (noch) nicht unterstützt.");
        }

        // Button für Anzeige aktuelle Position
        if(makemap.parameters.currentlocationbutton) {
            var clb = document.createElement("button");
            clb.style.backgroundColor = "white";
            clb.style.border = "none"; 
            clb.style.width = "28px"; 
            clb.style.height = "28px";
            clb.style.margin = "10px 10px 0 0";
            clb.style.borderRadius = "2px";
            clb.style.cursor = "pointer";
            clb.title = JB.GPX2GM.strings[JB.GPX2GM.parameters.doclang].showCurrentLocation;
            var clbimg = document.createElement("img");
            clbimg.style.position = "absolute";
            clbimg.style.top = "50%";
            clbimg.style.left = "50%";
            clbimg.style.transform = "translate(-50%, -50%)";
            clbimg.src = JB.GPX2GM.Path+"Icons/whereami.svg";
            var wpid = -1, marker = null, first;
            clb.onclick = function() {
                this.blur();
                if (navigator.geolocation) {
                    var geolocpos = function(position) {
                        var lat = position.coords.latitude;
                        var lon = position.coords.longitude;
                        marker.setLatLng([lat,lon]);
                        if(first) { 
                            dieses.map.setView([lat,lon]);
                            first = false;
                        }
                    }
                    var geolocerror = function(error) {
                        var errorCodes = ["Permission Denied","Position unavailible","Timeout"];
                        var errorString = (error.code<=3)?errorCodes[error.code-1]:"Error code: "+error.code;
                        JB.Debug_Info("Geolocation-Dienst fehlgeschlagen!",errorString+". "+error.message,true);
                    }
                    first = true;
                    if(!marker) marker = dieses.Marker({lat:0,lon:0},JB.icons.CL)[0];
                    if ( wpid == -1 ) {
                        clb.title = JB.GPX2GM.strings[JB.GPX2GM.parameters.doclang].hideCurrentLocation;
                        wpid = navigator.geolocation.watchPosition(geolocpos,geolocerror,{enableHighAccuracy:true, timeout: 5000, maximumAge: 60000});
                        marker.addTo(dieses.map); 
                        JB.Debug_Info("","Geolocation-Dienst wird eingerichtet.",false);
                    }
                    else {
                        clb.title = JB.GPX2GM.strings[JB.GPX2GM.parameters.doclang].showCurrentLocation;
                        navigator.geolocation.clearWatch(wpid);
                        wpid = -1;
                        marker.remove();
                        JB.Debug_Info("","Geolocation-Dienst wird abgeschaltet.",false);
                    }
                }
                else JB.Debug_Info("geolocation","Geolocation wird nicht unterstützt!",true);
            } // click-Handler
            clb.appendChild(clbimg);
            L.Control.Clbutton = L.Control.extend({
                onAdd: function(map) {
                    return clb;
                }
            });
            var clbutton = new L.Control.Clbutton({ position: 'topright' });
            clbutton.addTo(this.map);
        } // currentlocationbutton

        // Scalieren nach MAP-Resize
        dieses.zoomstatus = {};
        dieses.zoomstatus.iszoomed = false;
        dieses.zoomstatus.zoom_changed = function() {
            dieses.zoomstatus.iszoomed = true; 
            dieses.zoomstatus.level = dieses.map.getZoom();
            dieses.zoomstatus.w = mapcanvas.offsetWidth;
            dieses.zoomstatus.h = mapcanvas.offsetHeight;
        }
        dieses.zoomstatus.move_end = function() {
            dieses.zoomstatus.iszoomed = true; 
            dieses.mapcenter = dieses.map.getCenter();
        }
        dieses.map.on("moveend", dieses.zoomstatus.move_end);
        JB.onresize(mapcanvas,function(w,h) {
            if(w*h==0) return;
            dieses.map.invalidateSize();
            dieses.map.setView(dieses.mapcenter);
            dieses.map.off("zoomend", dieses.zoomstatus.zoom_changed);
            if(dieses.zoomstatus.iszoomed) {
                var dz = Math.round(Math.min(Math.log(w/dieses.zoomstatus.w)/Math.LN2,Math.log(h/dieses.zoomstatus.h)/Math.LN2));
                dieses.map.setZoom(dieses.zoomstatus.level+dz);
            }
            else {
                if(dieses.bounds) {
                    dieses.map.fitBounds(dieses.bounds,{padding:[20,20]});
                    dieses.map.setView(dieses.mapcenter);
                    dieses.zoomstatus.level = dieses.map.getZoom();
                    dieses.zoomstatus.w = w;
                    dieses.zoomstatus.h = h;
                }
            }
            if(!fullscreen) {
                genugplatz = JB.platzgenug(makemap.mapdiv);
                JB.handle_touch_action(dieses,genugplatz);
            }
        });
    };
    window.JB = window.JB || {};
    Object.defineProperty(window.JB, "Map", {
        get() { return ourMap; },
        set(_) {},
    });
})();
