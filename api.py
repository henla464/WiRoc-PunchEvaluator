from datetime import datetime
from flask import Flask, redirect, jsonify, request
from flask import send_file
import csv
from dataclasses import dataclass
import statistics

@dataclass
class Log:
    """Class for keeping track of an item in inventory."""
    Control: str
    CardNo: str
    DiffCardNo: int | None
    Time: str
    TimeTenthsOfSeconds: int
    DiffTime: int | None
    ReceivedTime: datetime
    DiffReceivedTime: int | None


app = Flask(__name__)

@app.route('/')
def defaultPage():
    return redirect('/logshtml/todays')


@app.route('/download/<date>')
def get_todays(date):
    theDateToUse = date
    if date == "todays":
        print("todays")
        currentDateTime = datetime.now()
        theDateToUse = str(currentDateTime)[0:10]

    return send_file(theDateToUse + ".txt", as_attachment=True)


def SortByTime(log: Log):
    return log.TimeTenthsOfSeconds


def SortByTimeReceived(log: Log):
    return log.ReceivedTime

def SortByCardNo(log: Log):
    return log.CardNo

def get_logs_array(date):
    theDateToUse = date
    if date == "todays":
        print("todays")
        currentDateTime = datetime.now()
        theDateToUse = str(currentDateTime)[0:10]

    logs = []
    with open(theDateToUse + '.txt', newline='\n') as csvfile:
        logreader = csv.reader(csvfile, delimiter=';', quotechar='"')
        next(logreader)
        for row in logreader:
            logs.append(Log(row[0], row[1], None, row[2], int(row[3]), None, datetime.fromisoformat(row[4]), None))

    lastTimeTenthsOfSeconds = 0
    logs.sort(key=SortByTime)
    for l in logs:
        if lastTimeTenthsOfSeconds != 0:
            l.DiffTime = l.TimeTenthsOfSeconds - lastTimeTenthsOfSeconds
        lastTimeTenthsOfSeconds = l.TimeTenthsOfSeconds

    lastReceivedTime: datetime | None = None
    logs.sort(key=SortByTimeReceived)
    for l in logs:
        if lastReceivedTime is not None:
            delta = (l.ReceivedTime - lastReceivedTime)
            l.DiffReceivedTime = int(delta.total_seconds() + delta.microseconds / 100000)
        lastReceivedTime = l.ReceivedTime

    lastCardNo = 0
    logs.sort(key=SortByCardNo)
    for l in logs:
        if lastCardNo != 0:
            l.DiffCardNo = int(l.CardNo) - lastCardNo
        lastCardNo = int(l.CardNo)

    return logs
@app.route('/logs/<date>')
def get_logs(date):
    logs = get_logs_array(date)
    return jsonify(logs)

@app.route('/logshtml/<date>')
def get_logshtml(date):
    logs = get_logs_array(date)

    medianDiffReceivedTime:int  = statistics.median([l.DiffReceivedTime for l in logs if l.DiffReceivedTime is not None])
    medianDiffTime: int = statistics.median([l.DiffTime for l in logs if l.DiffTime is not None])

    print("median")
    print(medianDiffReceivedTime)

    html = ("<html><head>"
            "<script type=\"text/javascript\" src=\"https://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js\"></script>"
            "<script type=\"text/javascript\" src=\"/static/TableFilter.js\"></script>"
            "<script type=\"text/javascript\" src=\"/static/jquery.tablesorter.js\"></script>"
            "<link rel=\"stylesheet\" type=\"text/css\" href=\"/static/style.css\" />"
            "<script type=\"text/javascript\">"
            "$(document).ready(function () {"
              "var tooltip = 'Quotes (\") match phrases. (not) excludes a match from the results. (or) can be used to do Or searches. I.e. [red or blue] will match either red or blue. Numeric values support >=, >, <=, <, = and != operators.';"
              "\n"
              "var optionsbasic = {"
              "columnFilters: [   "
              "      { columnName: 'CardNo', inputType: 'text', toolTipMessage: tooltip},"
              "      { columnName: 'Diff CardNo', inputType: 'text', toolTipMessage: tooltip},"
              "      { columnName: 'Time', inputType: 'text', toolTipMessage: tooltip},"
              "      { columnName: 'Time tenths of seconds', inputType: 'text', toolTipMessage: tooltip},"
              "      { columnName: 'Diff Time', inputType: 'text', toolTipMessage: tooltip},"
              "      { columnName: 'Received Time', inputType: 'text', toolTipMessage: tooltip},"
              "      { columnName: 'Diff Received Time', inputType: 'text', toolTipMessage: tooltip}"
              "  ]"
              "};\n"
              "$('#punches').tablesorter();"
              "$('#punches').tableFilter(optionsbasic);"
            "});"
            "</script></head><body><a href=\"/download/" + date + "\">Download</a>")
    html += "<table id=\"punches\" class=\"tablesorter\" border=\"1\"><thead><tr><th>CardNo</th><th>Diff CardNo</th><th>Time</th><th>Time Tenth of seconds</th><th>Diff Time Tenth of seconds</th><th>ReceivedTime</th><th>Diff ReceivedTime</th></tr></thead><tbody>"
    for l in logs:
        diffReceivedClass = "";
        if l.DiffReceivedTime is not None and l.DiffReceivedTime > 1.5*medianDiffReceivedTime:
            diffReceivedClass = " class=\"red\""
        diffTimeClass = "";
        if l.DiffTime is not None and l.DiffTime > 1.5*medianDiffTime:
            diffTimeClass = " class=\"red\""
        missedPunchClass = ""
        if l.DiffCardNo is not None and l.DiffCardNo > 1:
            missedPunchClass = " class=\"red\""

        html += f"<tr><td>{l.CardNo}</td><td{missedPunchClass}>{l.DiffCardNo}</td><td>{l.Time}</td><td>{l.TimeTenthsOfSeconds}</td><td{diffTimeClass}>{l.DiffTime}</td><td>{l.ReceivedTime}</td><td{diffReceivedClass}>{l.DiffReceivedTime}</td></tr>"
    html += "</tbody></table></body></html>"
    return html


def startFlaskServer():
    print("startflask")
    app.run(port=5000, debug=True)

