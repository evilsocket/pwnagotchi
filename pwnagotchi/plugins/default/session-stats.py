import os
import logging
import threading
from datetime import datetime
from pwnagotchi import plugins
from flask import render_template_string
from flask import jsonify

TEMPLATE = """
{% extends "base.html" %}
{% set active_page = "plugins" %}
{% block title %}
    Session stats
{% endblock %}

{% block styles %}
    <link rel="stylesheet" href="/css/jquery.jqplot.min.css"/>
    <link rel="stylesheet" href="/css/jquery.jqplot.css"/>
{% endblock %}

{% block scripts %}
     <script type="text/javascript" src="/js/jquery.jqplot.min.js"></script>
     <script type="text/javascript" src="/js/jquery.jqplot.js"></script>
     <script type="text/javascript" src="/js/plugins/jqplot.mobile.js"></script>
     <script type="text/javascript" src="/js/plugins/jqplot.json2.js"></script>
     <script type="text/javascript" src="/js/plugins/jqplot.dateAxisRenderer.js"></script>
     <script type="text/javascript" src="/js/plugins/jqplot.highlighter.js"></script>
     <script type="text/javascript" src="/js/plugins/jqplot.cursor.js"></script>
     <script type="text/javascript" src="/js/plugins/jqplot.enhancedLegendRenderer.js"></script>
{% endblock %}

{% block script %}
    $(document).ready(function(){
      var ajaxDataRenderer = function(url, plot, options) {
	var ret = null;
	$.ajax({
	  async: false,
	  url: url,
	  dataType:"json",
	  success: function(data) {
	    ret = data;
	  }
	});
	return ret;
      };

      function loadData(url, elm, title) {
          var data = ajaxDataRenderer(url);
          var plot_os = $.jqplot(elm, data.values,{
            title: title,
            stackSeries: true,
            seriesDefaults: {
                showMarker: false,
                fill: true,
                fillAndStroke: true
            },
            legend: {
                show: true,
                renderer: $.jqplot.EnhancedLegendRenderer,
                placement: 'outsideGrid',
                labels: data.labels,
                location: 's',
                rendererOptions: {
                  numberRows: '2',
                },
                rowSpacing: '0px'
            },
            axes:{
                xaxis:{
                    renderer:$.jqplot.DateAxisRenderer,
                    tickOptions:{formatString:'%H:%M:%S'}
                },
                yaxis:{
                    min: 0,
                    tickOptions:{formatString:'%.2f'}
                }
            },
            highlighter: {
                show: true,
                sizeAdjust: 7.5
            },
            cursor:{
                show: true,
                tooltipLocation:'sw'
            }
          }).replot({
            axes:{
                xaxis:{
                    renderer:$.jqplot.DateAxisRenderer,
                    tickOptions:{formatString:'%H:%M:%S'}
                },
                yaxis:{
                    min: 0,
                    tickOptions:{formatString:'%.2f'}
                }
            }
            });
      }

      function loadAll() {
          loadData('/plugins/session-stats/os', 'chart_os', 'OS')
          loadData('/plugins/session-stats/temp', 'chart_temp', 'Temp')
          loadData('/plugins/session-stats/nums', 'chart_nums', 'Wifi')
          loadData('/plugins/session-stats/duration', 'chart_duration', 'Sleeping')
          loadData('/plugins/session-stats/epoch', 'chart_epoch', 'Epochs')
      }

      loadAll();
      setInterval(loadAll, 60000);
    });
{% endblock %}

{% block content %}
    <div id="chart_os" style="height:400px;width:100%; "></div>
    <div id="chart_temp" style="height:400px;width:100%; "></div>
    <div id="chart_nums" style="height:400px;width:100%; "></div>
    <div id="chart_duration" style="height:400px;width:100%; "></div>
    <div id="chart_epoch" style="height:400px;width:100%; "></div>
{% endblock %}
"""

class SessionStats(plugins.Plugin):
    __author__ = '33197631+dadav@users.noreply.github.com'
    __version__ = '0.1.0'
    __license__ = 'GPL3'
    __description__ = 'This plugin displays stats of the current session.'

    def __init__(self):
        self.ready = False
        self.lock = threading.Lock()
        self.options = dict()
        self.stats = dict()

    def on_loaded(self):
        """
        Gets called when the plugin gets loaded
        """
        logging.info("Session-stats plugin loaded.")
        self.ready = True

    def on_unloaded(self, ui):
        pass

    def on_epoch(self, agent, epoch, epoch_data):
        """
        Save the epoch_data to self.stats
        """
        with self.lock:
            self.stats[datetime.now().strftime("%H:%M:%S")] = epoch_data

    @staticmethod
    def extract_key_values(data, subkeys):
        result = dict()
        result['values'] = list()
        result['labels'] = subkeys
        for plot_key in subkeys:
            v = [ [ts,d[plot_key]] for ts, d in data.items()]
            result['values'].append(v)
        return result

    def on_webhook(self, path, request):
        if not path or path == "/":
            return render_template_string(TEMPLATE)

        if path == "os":
            extract_keys = ['cpu_load','mem_usage',]
        elif path == "temp":
            extract_keys = ['temperature']
        elif path == "nums":
            extract_keys = [
                'missed_interactions',
                'num_hops',
                'num_peers',
                'tot_bond',
                'avg_bond',
                'num_deauths',
                'num_associations',
                'num_handshakes',
            ]
        elif path == "duration":
            extract_keys = [
                'duration_secs',
                'slept_for_secs',
            ]
        elif path == "epoch":
            extract_keys = [
                'blind_for_epochs',
                'inactive_for_epochs',
                'active_for_epochs',
            ]



        with self.lock:
            return jsonify(SessionStats.extract_key_values(self.stats, extract_keys))
