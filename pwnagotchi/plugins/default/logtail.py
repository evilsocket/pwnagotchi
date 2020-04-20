import os
import logging
import threading
from itertools import islice
from time import sleep
from datetime import datetime,timedelta
from pwnagotchi import plugins
from pwnagotchi.utils import StatusFile
from flask import render_template_string
from flask import jsonify
from flask import abort
from flask import Response


TEMPLATE = """
{% extends "base.html" %}
{% set active_page = "plugins" %}
{% block title %}
    Logtail
{% endblock %}

{% block styles %}
    {{ super() }}
    <style>
        * {
            box-sizing: border-box;
        }
        #filter {
            width: 100%;
            font-size: 16px;
            padding: 12px 20px 12px 40px;
            border: 1px solid #ddd;
            margin-bottom: 12px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            border: 1px solid #ddd;
        }
        th, td {
            text-align: left;
            padding: 12px;
            width: 1px;
            white-space: nowrap;
        }
        td:nth-child(2) {
            text-align: center;
        }
        thead, tr:hover {
            background-color: #f1f1f1;
        }
        tr {
            border-bottom: 1px solid #ddd;
        }
        div.sticky {
            position: -webkit-sticky;
            position: sticky;
            top: 0;
            display: table;
            width: 100%;
        }
        div.sticky > * {
            display: table-cell;
        }
        div.sticky > span {
            width: 1%;
        }
        div.sticky > input {
            width: 100%;
        }
        tr.default {
            color: black;
        }
        tr.info {
            color: black;
        }
        tr.warning {
            color: darkorange;
        }
        tr.error {
            color: crimson;
        }
        tr.debug {
            color: blueviolet;
        }
        .ui-mobile .ui-page-active {
            overflow: visible;
            overflow-x: visible;
        }
    </style>
{% endblock %}

{% block script %}
    var table = document.getElementById('table');
    var filter = document.getElementById('filter');
    var filterVal = filter.value.toUpperCase();

    var xhr = new XMLHttpRequest();
    xhr.open('GET', '{{ url_for('plugins') }}/logtail/stream');
    xhr.send();
    var position = 0;
    var data;
    var time;
    var level;
    var msg;
    var colorClass;

    function handleNewData() {
        var messages = xhr.responseText.split('\\n');
        filterVal = filter.value.toUpperCase();
        messages.slice(position, -1).forEach(function(value) {

            if (value.charAt(0) != '[') {
                msg = value;
                time = '';
                level = '';
            } else {
                data = value.split(']');
                time = data.shift() + ']';
                level = data.shift() + ']';
                msg = data.join(']');

                switch(level) {
                    case ' [INFO]':
                        colorClass = 'info';
                        break;
                    case ' [WARNING]':
                        colorClass = 'warning';
                        break;
                    case ' [ERROR]':
                        colorClass = 'error';
                        break;
                    case ' [DEBUG]':
                        colorClass = 'debug';
                        break;
                    default:
                        colorClass = 'default';
                        break;
                }
            }

            var tr = document.createElement('tr');
            var td1 = document.createElement('td');
            var td2 = document.createElement('td');
            var td3 = document.createElement('td');

            td1.textContent = time;
            td2.textContent = level;
            td3.textContent = msg;

            tr.appendChild(td1);
            tr.appendChild(td2);
            tr.appendChild(td3);

            tr.className = colorClass;

            if (filterVal.length > 0 && value.toUpperCase().indexOf(filterVal) == -1) {
                tr.style.display = "none";
            }

            table.appendChild(tr);
        });
        position = messages.length - 1;
    }

    var scrollingElement = (document.scrollingElement || document.body)
    function scrollToBottom () {
       scrollingElement.scrollTop = scrollingElement.scrollHeight;
    }

    var timer;
    var scrollElm = document.getElementById('autoscroll');
    timer = setInterval(function() {
        handleNewData();
        if (scrollElm.checked) {
            scrollToBottom();
        }
        if (xhr.readyState == XMLHttpRequest.DONE) {
            clearInterval(timer);
        }
    }, 1000);

    var typingTimer;
    var doneTypingInterval = 1000;

    filter.onkeyup = function() {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(doneTyping, doneTypingInterval);
    }

    filter.onkeydown = function() {
        clearTimeout(typingTimer);
    }

    function doneTyping() {
        document.body.style.cursor = 'progress';
        var tr, tds, td, i, txtValue;
        filterVal = filter.value.toUpperCase();
        tr = table.getElementsByTagName("tr");
        for (i = 1; i < tr.length; i++) {
            txtValue = tr[i].textContent || tr[i].innerText;
            if (txtValue.toUpperCase().indexOf(filterVal) > -1) {
                tr[i].style.display = "table-row";
            } else {
                tr[i].style.display = "none";
            }
        }
        document.body.style.cursor = 'default';
    }
{% endblock %}

{% block content %}
    <div class="sticky">
        <input type="text" id="filter" placeholder="Search for ..." title="Type in a filter">
        <span><input checked type="checkbox" id="autoscroll"></span>
        <span><label for="autoscroll"> Autoscroll to bottom</label><br></span>
    </div>
    <table id="table">
        <thead>
            <th>
                Time
            </th>
            <th>
                Level
            </th>
            <th>
                Message
            </th>
        </thead>
    </table>
{% endblock %}
"""


class Logtail(plugins.Plugin):
    __author__ = '33197631+dadav@users.noreply.github.com'
    __version__ = '0.1.0'
    __license__ = 'GPL3'
    __description__ = 'This plugin tails the logfile.'

    def __init__(self):
        self.lock = threading.Lock()
        self.options = dict()
        self.ready = False

    def on_config_changed(self, config):
        self.config = config
        self.ready = True

    def on_loaded(self):
        """
        Gets called when the plugin gets loaded
        """
        logging.info("Logtail plugin loaded.")


    def on_webhook(self, path, request):
        if not self.ready:
            return "Plugin not ready"

        if not path or path == "/":
            return render_template_string(TEMPLATE)

        if path == 'stream':
            def generate():
                with open(self.config['main']['log']['path']) as f:
                    yield ''.join(f.readlines()[-self.options.get('max-lines', 4096):])
                    while True:
                        yield f.readline()

            return Response(generate(), mimetype='text/plain')

        abort(404)
