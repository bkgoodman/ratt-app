# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
#  _____       ______________
# |  __ \   /\|__   ____   __|
# | |__) | /  \  | |    | |
# |  _  / / /\ \ | |    | |
# | | \ \/ ____ \| |    | |
# |_|  \_\/    \_\_|    |_|    ... RFID ALL THE THINGS!
#
# A resource access control and telemetry solution for Makerspaces
#
# Developed at MakeIt Labs - New Hampshire's First & Largest Makerspace
# http://www.makeitlabs.com/
#
# Copyright 2018 MakeIt Labs
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and assoceiated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
#
# Author: Steve Richardson (steve.richardson@makeitlabs.com)
#

from QtGPIO import LOW, HIGH
from PersonalitySimple import Personality as PersonalitySimple
from PyQt5.QtCore import pyqtSlot, pyqtSignal, pyqtProperty, QVariant
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import json
from urllib.request import urlopen
import time
class Worker(QObject):
    finished = pyqtSignal()
    downloadComplete = pyqtSignal(name="downloadComplete")
    parent = None

    def run(self):
        """Long-running task."""
        print ("START WORKER SLEEP")
        time.sleep(3)
        print ("START END WIRJER SLEEP")
        self.finished.emit()
        self.downloadComplete.emit()
        self.parent.slotUIEvent("downloadComplete")

class Personality(PersonalitySimple):
    #############################################
    ## Tool Personality: Vending Mill
    #############################################
    PERSONALITY_DESCRIPTION = 'Vending'
    STATE_VENDING_LIST = 'VendingList'
    STATE_VENDING_CONFIRM = 'VendingConfirm'
    STATE_VENDING_INPROGRESS = 'VendingInProgress'
    STATE_VENDING_COMPLETE = 'VendingComplete'
    vendingAmount=1
    vendingChanged = pyqtSignal(bool, str,name="vendingResult", arguments=['status','result'])
    _vendingResult = "Default"
    _vendingStatus = False

    def __init__(self, *args, **kwargs):
        PersonalitySimple.__init__(self, *args, **kwargs)
        
        self.app.rootContext().setContextProperty("vendingAmount", 1)
        self.states[self.STATE_VENDING_LIST] = self.stateVendingList
        self.states[self.STATE_VENDING_INPROGRESS] = self.stateVendingInProgress
        self.states[self.STATE_VENDING_COMPLETE] = self.stateVendingComplete


    @pyqtProperty(float)
    def vendingAmount(self):
        return self._vendingAmount

    @vendingAmount.setter
    def vendingAmount(self, value):
        self._vendingAmount = value

    @pyqtProperty(bool)
    def vendingStatus(self):
        return self._vendingStatus

    @vendingStatus.setter
    def vendingStatus(self, value):
        self._vendingStatus = value
        self.vendingChanged.emit(self._vendingStatus,self._vendingResult)

    @pyqtProperty(str, notify=vendingChanged)
    def vendingResult(self):
        return self._vendingResult

    @vendingResult.setter
    def vendingResult(self, value):
        self._vendingResult = value
        self.vendingChanged.emit(self._vendingStatus,self._vendingResult)

    # enable tool
    def enableTool(self):
        self.logger.debug('VENDING ENABLE TOOL')
        self.pins_out[0].set(HIGH)


    # disable tool
    def disableTool(self):
        self.logger.debug('VENDING DISABLE TOOL')
        self.pins_out[0].set(LOW)
        self.pins_out[1].set(LOW)




    #############################################
    ## STATE_VENDING_INPROGRESS
    #############################################
    def stateVendingInProgress(self):
        if self.phENTER:
            self.logger.debug('VENDING INPROGRESS Enter')
            xxx=  self.goActive()
            #with urlopen("https://sunlightlabs.github.io/congress/legislators?api_key='(myapikey)") as conn:
            #   print (conn.read())
            #   time.sleep(11)
            self.thread = QThread()
            self.worker = Worker()
            self.worker.parent=self
            self.worker.moveToThread(self.thread)
            self.thread.start()
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            return xxx

        elif self.phACTIVE:
            self.logger.debug('VENDING INPROGRESS active')
            if self.wakereason == self.REASON_UI and self.uievent == 'VendingFailed':
                self.vendingStatus = False
                self.vendingResult = "Payment Failed"
                self.logger.debug('VENDING INPROGRESS FAILED')
                return self.exitAndGoto(self.STATE_VENDING_COMPLETE)
            elif self.wakereason == self.REASON_UI and self.uievent == 'VendingSuccessful':
                va = float(self.vendingAmount)
                self.logger.debug('VENDING INPROGRESS SUCCCEDED')
                self.vendingStatus = True
                self.vendingResult = "Payment Complete"
                return self.exitAndGoto(self.STATE_VENDING_COMPLETE)
            elif self.wakereason == self.REASON_UI and self.uievent == 'downloadComplete':
                return self.exitAndGoto(self.STATE_VENDING_COMPLETE)
                

            return False

        elif self.phEXIT:
            self.logger.debug('VENDING INPROGRESS exit')
            self.pin_led1.set(LOW)
            return self.goNextState()

    #############################################
    ## STATE_VENDING_COMPLETE
    #############################################
    def stateVendingComplete(self):
        if self.phENTER:
            self.logger.debug('VENDING COMPLETE Enter')
            return self.goActive()

        elif self.phACTIVE:
            self.logger.debug('VENDING COMPLETE active')
            if self.wakereason == self.REASON_UI and self.uievent == 'Idle':
                print('VENDING FINALLY DONE')
                self.disableTool()
                return self.exitAndGoto(self.STATE_IDLE)
                

            return False

        elif self.phEXIT:
            self.logger.debug('VENDING COMPLETE exit')
            self.pin_led1.set(LOW)
            return self.goNextState()

    #############################################
    ## STATE_VENDING_LIST
    #############################################
    def stateVendingList(self):
        if self.phENTER:
            self.logger.debug('VENDING LOGIN Enter')
            self.app.rootContext().setContextProperty("vendingAmount", 1)
            self.telemetryEvent.emit('personality/login', json.dumps({'allowed': True, 'member': self.activeMemberRecord.name}))
            self.activeMemberRecord.loggedIn = True
            self.pin_led1.set(HIGH)
            self.vendingAmount =1
            return self.goActive()

        elif self.phACTIVE:
            self.logger.debug('VENDING LOGIN active')
            if self.wakereason == self.REASON_UI and self.uievent == 'VendingAborted':
                self.vendingResult = "Payment Aborted"
                self.vendingStatus = False
                return self.exitAndGoto(self.STATE_VENDING_COMPLETE)
            elif self.wakereason == self.REASON_UI and self.uievent == 'VendingAccepted':
                va = float(self.vendingAmount)
                print('VENDING ACCEPTED',va,type(self.vendingAmount))
                return self.exitAndGoto(self.STATE_VENDING_INPROGRESS)
                

            return False

        elif self.phEXIT:
            self.logger.debug('VENDING LOGIN exit')
            self.pin_led1.set(LOW)
            return self.goNextState()

    #############################################
    ## STATE_IDLE
    #############################################
    def stateIdle(self):
        if self.phENTER:
            self.logger.info('simple stateIdle enter')
            if self.activeMemberRecord.loggedIn:
                self.telemetryEvent.emit('personality/logout', json.dumps({'member': self.activeMemberRecord.name, 'reason': 'other'}))
            self.activeMemberRecord.clear()
            self.wakeOnRFID(True)
            self.pin_led1.set(LOW)
            self.pin_led2.set(LOW)
            if self.wasLockedOut:
                return self.exitAndGoto(self.STATE_LOCK_OUT)
            self.wakeOnTimer(enabled=True, interval=500, singleShot=True)
            return self.goActive()

        elif self.phACTIVE:

            if self._monitorToolPower and not self.toolPowered():
                return self.exitAndGoto(self.STATE_TOOL_NOT_POWERED)

            if self.wakereason == self.REASON_TIMER:
                if self.pin_led1.get() == LOW:
                    self.pin_led1.set(HIGH)
                    self.wakeOnTimer(enabled=True, interval=500, singleShot=True)
                else:
                    self.pin_led1.set(LOW)
                    self.wakeOnTimer(enabled=True, interval=1500, singleShot=True)
            elif self.wakereason == self.REASON_RFID_ALLOWED:
                self.endorsementsChanged.emit()
                return self.exitAndGoto(self.STATE_VENDING_LIST)
            elif self.wakereason == self.REASON_RFID_DENIED:
                return self.exitAndGoto(self.STATE_ACCESS_DENIED)
            elif self.wakereason == self.REASON_RFID_ERROR:
                return self.exitAndGoto(self.STATE_RFID_ERROR)
            elif self.wakereason == self.REASON_UI and self.uievent == 'IdleBusy':
                return self.exitAndGoto(self.STATE_IDLE_BUSY)
            elif self.wakereason == self.REASON_UI and self.uievent == 'ReportIssue':
                return self.exitAndGoto(self.STATE_REPORT_ISSUE)


            # otherwise thread goes back to waiting
            return False

        elif self.phEXIT:
            self.pin_led1.set(LOW)
            self.wakeOnTimer(False)
            self.wakeOnRFID(False)
            return self.goNextState()
