import logging
import json
import toml
import _thread
from pwnagotchi import restart, plugins
from pwnagotchi.utils import save_config
from flask import abort
from flask import render_template_string

INDEX = """
{% extends "base.html" %}
{% set active_page = "plugins" %}
{% block title %}
    Webcfg
{% endblock %}

{% block meta %}
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, user-scalable=0" />
{% endblock %}

{% block styles %}
{{ super() }}
<style>
    #divTop {
        position: -webkit-sticky;
        position: sticky;
        top: 0px;
        width: 100%;
        font-size: 16px;
        padding: 5px;
        border: 1px solid #ddd;
        margin-bottom: 5px;
    }

    #searchText {
        width: 100%;
    }

    table {
        table-layout: auto;
        width: 100%;
    }

    table, th, td {
      border: 1px solid black;
      border-collapse: collapse;
    }

    th, td {
      padding: 15px;
      text-align: left;
    }

    table tr:nth-child(even) {
      background-color: #eee;
    }

    table tr:nth-child(odd) {
     background-color: #fff;
    }

    table th {
      background-color: black;
      color: white;
    }

    .remove {
        background-color: #f44336;
        color: white;
        border: 2px solid #f44336;
        padding: 4px 8px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 12px;
        margin: 4px 2px;
        -webkit-transition-duration: 0.4s; /* Safari */
        transition-duration: 0.4s;
        cursor: pointer;
    }

    .remove:hover {
        background-color: white;
        color: black;
    }

    #btnSave {
        position: -webkit-sticky;
        position: sticky;
        bottom: 0px;
        width: 100%;
        background-color: #0061b0;
        border: none;
        color: white;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        cursor: pointer;
        float: right;
    }

    #divTop {
        display: table;
        width: 100%;
    }
    #divTop > * {
        display: table-cell;
    }
    #divTop > span {
        width: 1%;
    }
    #divTop > input {
        width: 100%;
    }

    @media screen and (max-width:700px) {
        table, tr, td {
            padding:0;
            border:1px solid black;
        }

        table {
            border:none;
        }

        tr:first-child, thead, th {
            display:none;
            border:none;
        }

        tr {
            float: left;
            width: 100%;
            margin-bottom: 2em;
        }

        table tr:nth-child(odd) {
            background-color: #eee;
        }

        td {
            float: left;
            width: 100%;
            padding:1em;
        }

        td::before {
            content:attr(data-label);
            word-wrap: break-word;
            background: #eee;
            border-right:2px solid black;
            width: 20%;
            float:left;
            padding:1em;
            font-weight: bold;
            margin:-1em 1em -1em -1em;
        }

        .del_btn_wrapper {
            content:attr(data-label);
            word-wrap: break-word;
            background: #eee;
            border-right:2px solid black;
            width: 20%;
            float:left;
            padding:1em;
            font-weight: bold;
            margin:-1em 1em -1em -1em;
        }
    }
</style>
{% endblock %}

{% block content %}
    <div id="divTop">
        <input type="text" id="searchText" placeholder="Search for options ..." title="Type an option name">
        <span><select id="selAddType"><option value="text">Text</option><option value="number">Number</option></select></span>
        <span><button id="btnAdd" type="button" onclick="addOption()">+</button></span>
    </div>
    <button id="btnSave" type="button" onclick="saveConfig()">Save and restart</button>
    <div id="content"></div>
{% endblock %}

{% block script %}
        function addOption() {
          var input, table, tr, td, divDelBtn, btnDel, selType, selTypeVal;
          input = document.getElementById("searchText");
          inputVal = input.value;
          selType = document.getElementById("selAddType");
          selTypeVal = selType.options[selType.selectedIndex].value;
          table = document.getElementById("tableOptions");
          if (table) {
            tr = table.insertRow();
            // del button
            divDelBtn = document.createElement("div");
            divDelBtn.className = "del_btn_wrapper";
            td = document.createElement("td");
            td.setAttribute("data-label", "");
            btnDel = document.createElement("Button");
            btnDel.innerHTML = "X";
            btnDel.onclick = function(){ delRow(this);};
            btnDel.className = "remove";
            divDelBtn.appendChild(btnDel);
            td.appendChild(divDelBtn);
            tr.appendChild(td);
            // option
            td = document.createElement("td");
            td.setAttribute("data-label", "Option");
            td.innerHTML = inputVal;
            tr.appendChild(td);
            // value
            td = document.createElement("td");
            td.setAttribute("data-label", "Value");
            input = document.createElement("input");
            input.type = selTypeVal;
            input.value = "";
            td.appendChild(input);
            tr.appendChild(td);

            input.value = "";
          }
        }

        function saveConfig(){
            // get table
            var table = document.getElementById("tableOptions");
            if (table) {
                var json = tableToJson(table);
                sendJSON("webcfg/save-config", json, function(response) {
                    if (response) {
                        if (response.status == "200") {
                            alert("Config got updated");
                        } else {
                            alert("Error while updating the config (err-code: " + response.status + ")");
                        }
                    }
                });
            }
        }
        var searchInput = document.getElementById("searchText");
        searchInput.onkeyup = function() {
            var filter, table, tr, td, i, txtValue;
            filter = searchInput.value.toUpperCase();
            table = document.getElementById("tableOptions");
            if (table) {
                tr = table.getElementsByTagName("tr");

                for (i = 0; i < tr.length; i++) {
                    td = tr[i].getElementsByTagName("td")[1];
                    if (td) {
                        txtValue = td.textContent || td.innerText;
                        if (txtValue.toUpperCase().indexOf(filter) > -1) {
                            tr[i].style.display = "";
                        }else{
                            tr[i].style.display = "none";
                        }
                    }
                }
            }
        }

        function sendJSON(url, data, callback) {
          var xobj = new XMLHttpRequest();
          var csrf = "{{ csrf_token() }}";
          xobj.open('POST', url);
          xobj.setRequestHeader("Content-Type", "application/json");
          xobj.setRequestHeader('x-csrf-token', csrf);
          xobj.onreadystatechange = function () {
                if (xobj.readyState == 4) {
                  callback(xobj);
                }
          };
          xobj.send(JSON.stringify(data));
        }

        function loadJSON(url, callback) {
          var xobj = new XMLHttpRequest();
          xobj.overrideMimeType("application/json");
          xobj.open('GET', url, true);
          xobj.onreadystatechange = function () {
                if (xobj.readyState == 4 && xobj.status == "200") {
                  callback(JSON.parse(xobj.responseText));
                }
          };
          xobj.send(null);
        }

        // https://stackoverflow.com/questions/19098797/fastest-way-to-flatten-un-flatten-nested-json-objects
        function unFlattenJson(data) {
            "use strict";
            if (Object(data) !== data || Array.isArray(data))
                return data;
            var result = {}, cur, prop, idx, last, temp, inarray;
            for(var p in data) {
                cur = result, prop = "", last = 0, inarray = false;
                do {
                    idx = p.indexOf(".", last);
                    temp = p.substring(last, idx !== -1 ? idx : undefined);
                    inarray = temp.startsWith('#') && !isNaN(parseInt(temp.substring(1)))
                    cur = cur[prop] || (cur[prop] = (inarray ? [] : {}));
                    if (inarray){
                        prop = temp.substring(1);
                    }else{
                        prop = temp;
                    }
                    last = idx + 1;
                } while(idx >= 0);
                cur[prop] = data[p];
            }
            return result[""];
        }

        function flattenJson(data) {
            var result = {};
            function recurse (cur, prop) {
                if (Object(cur) !== cur) {
                    result[prop] = cur;
                } else if (Array.isArray(cur)) {
                     for(var i=0, l=cur.length; i<l; i++)
                         recurse(cur[i], prop ? prop+".#"+i : ""+i);
                    if (l == 0)
                        result[prop] = [];
                } else {
                    var isEmpty = true;
                    for (var p in cur) {
                        isEmpty = false;
                        recurse(cur[p], prop ? prop+"."+p : p);
                    }
                    if (isEmpty)
                        result[prop] = {};
                }
            }
            recurse(data, "");
            return result;
        }

        function delRow(btn) {
            var tr = btn.parentNode.parentNode.parentNode;
            tr.parentNode.removeChild(tr);
        }

        function jsonToTable(json) {
            var table = document.createElement("table");
            table.id = "tableOptions";

            // create header
            var tr = table.insertRow();
            var thDel = document.createElement("th");
            thDel.innerHTML = "";
            var thOpt = document.createElement("th");
            thOpt.innerHTML = "Option";
            var thVal = document.createElement("th");
            thVal.innerHTML = "Value";
            tr.appendChild(thDel);
            tr.appendChild(thOpt);
            tr.appendChild(thVal);

            var td, divDelBtn, btnDel;
            // iterate over keys
            Object.keys(json).forEach(function(key) {
                tr = table.insertRow();
                // del button
                divDelBtn = document.createElement("div");
                divDelBtn.className = "del_btn_wrapper";
                td = document.createElement("td");
                td.setAttribute("data-label", "");
                btnDel = document.createElement("Button");
                btnDel.innerHTML = "X";
                btnDel.onclick = function(){ delRow(this);};
                btnDel.className = "remove";
                divDelBtn.appendChild(btnDel);
                td.appendChild(divDelBtn);
                tr.appendChild(td);
                // option
                td = document.createElement("td");
                td.setAttribute("data-label", "Option");
                td.innerHTML = key;
                tr.appendChild(td);
                // value
                td = document.createElement("td");
                td.setAttribute("data-label", "Value");
                if(typeof(json[key])==='boolean'){
                    input = document.createElement("select");
                    input.setAttribute("id", "boolSelect");
                    tvalue = document.createElement("option");
                    tvalue.setAttribute("value", "true");
                    ttext = document.createTextNode("True")
                    tvalue.appendChild(ttext);
                    fvalue = document.createElement("option");
                    fvalue.setAttribute("value", "false");
                    ftext = document.createTextNode("False");
                    fvalue.appendChild(ftext);
                    input.appendChild(tvalue);
                    input.appendChild(fvalue);
                    input.value = json[key];
                    document.body.appendChild(input);
                    td.appendChild(input);
                    tr.appendChild(td);
                } else {
                    input = document.createElement("input");
                    if(Array.isArray(json[key])) {
                        input.type = 'text';
                        input.value = '[]';
                    }else{
                        input.type = typeof(json[key]);
                        input.value = json[key];
                    }
                    td.appendChild(input);
                    tr.appendChild(td);
                }
            });

            return table;
        }

        function tableToJson(table) {
            var rows = table.getElementsByTagName("tr");
            var i, td, key, value;
            var json = {};

            for (i = 0; i < rows.length; i++) {
                td = rows[i].getElementsByTagName("td");
                if (td.length == 3) {
                    // td[0] = del button
                    key = td[1].textContent || td[1].innerText;
                    var input = td[2].getElementsByTagName("input");
                    var select = td[2].getElementsByTagName("select");
                    if (input && input != undefined && input.length > 0 ) {
                        if (input[0].type == "text") {
                            if (input[0].value.startsWith("[") && input[0].value.endsWith("]")) {
                                json[key] = JSON.parse(input[0].value);
                            }else{
                                json[key] = input[0].value;
                            }
                        }else if (input[0].type == "number") {
                            json[key] = Number(input[0].value);
                        }
                    } else if(select && select != undefined && select.length > 0) {
                        var myValue = select[0].options[select[0].selectedIndex].value;
                        json[key] = myValue === 'true';
                    }
                }
            }
            return unFlattenJson(json);
        }

        loadJSON("webcfg/get-config", function(response) {
            var flat_json = flattenJson(response);
            var table = jsonToTable(flat_json);
            var divContent = document.getElementById("content");
            divContent.innerHTML = "";
            divContent.appendChild(table);
        });
{% endblock %}
"""

def serializer(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

class WebConfig(plugins.Plugin):
    __author__ = '33197631+dadav@users.noreply.github.com'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'This plugin allows the user to make runtime changes.'

    def __init__(self):
        self.ready = False
        self.mode = 'MANU'

    def on_config_changed(self, config):
        self.config = config
        self.ready = True

    def on_ready(self, agent):
        self.mode = 'MANU' if agent.mode == 'manual' else 'AUTO'

    def on_internet_available(self, agent):
        self.mode = 'MANU' if agent.mode == 'manual' else 'AUTO'

    def on_loaded(self):
        """
        Gets called when the plugin gets loaded
        """
        logging.info("webcfg: Plugin loaded.")


    def on_webhook(self, path, request):
        """
        Serves the current configuration
        """
        if not self.ready:
            return "Plugin not ready"

        if request.method == "GET":
            if path == "/" or not path:
                return render_template_string(INDEX)
            elif path == "get-config":
                # send configuration
                return json.dumps(self.config, default=serializer)
            else:
                abort(404)
        elif request.method == "POST":
            if path == "save-config":
                try:
                    save_config(request.get_json(), '/etc/pwnagotchi/config.toml') # test
                    _thread.start_new_thread(restart, (self.mode,))
                    return "success"
                except Exception as ex:
                    logging.error(ex)
                    return "config error", 500
        abort(404)
