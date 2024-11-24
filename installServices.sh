#!/bin/bash

cp WiRocPunchEvaluatorTCPServer.service /etc/systemd/system/
cp WiRocPunchEvaluatorWebServer.service /etc/systemd/system/
systemctl enable /etc/systemd/system/WiRocPunchEvaluatorTCPServer.service
systemctl enable /etc/systemd/system/WiRocPunchEvaluatorWebServer.service
systemctl start WiRocPunchEvaluatorTCPServer.service
systemctl start WiRocPunchEvaluatorWebServer.service