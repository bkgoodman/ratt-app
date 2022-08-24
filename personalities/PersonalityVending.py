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
import json

class Personality(PersonalitySimple):
    #############################################
    ## Tool Personality: Vending Mill
    #############################################
    PERSONALITY_DESCRIPTION = 'Vending'
    STATE_VENDING_LIST = 'VendingList'
    STATE_VENDING_CONFIRM = 'VendingConfirm'
    vendingAmount=1

    def __init__(self, *args, **kwargs):
        PersonalitySimple.__init__(self, *args, **kwargs)
        
        self.app.rootContext().setContextProperty("vendingAmount", 1)
        self.states[self.STATE_VENDING_LIST] = self.stateVendingList

    @pyqtProperty(float)
    def vendingAmount(self):
        return self._vendingAmount

    @vendingAmount.setter
    def vendingAmount(self, value):
        self._vendingAmount = value
        #self.toolActiveFlagChanged.emit()

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
                self.disableTool()
                return self.exitAndGoto(self.STATE_IDLE)
            elif self.wakereason == self.REASON_UI and self.uievent == 'VendingAccepted':
                va = float(self.vendingAmount)
                print('VENDING ACCEPTED',va,type(self.vendingAmount))
                

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
