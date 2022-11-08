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



# Audio: https://notevibes.com/cabinet.php  voice "Rina"

from QtGPIO import LOW, HIGH
from PersonalitySimple import Personality as PersonalitySimple
from PyQt5.QtCore import pyqtSlot, pyqtSignal, pyqtProperty, QVariant
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import json
import requests
import time
import math

class Payout(QObject):
  vendCents=0 # IN CENTS!!
  #payoutComplete = pyqtSignal(name="payoutComplete")

  def run(self):
      print("\n\n\n*** PAYOUT RUN ****")
      payout = self.parent.app.config.value("Vending.Payout")
      payoutTime = self.parent.app.config.value("Vending.PayoutTime")
      dollars=0
      quarters=0
      if payout == "Dollars":
        dollars = self.vendCents / 100
      elif payout == "Quarters":
        quarters = self.vendCents / 25
      elif payout == "Both":
        dollars = math.floor(self.vendCents / 100)
        quarters = int((self.vendCents/25) - (dollars*4))
        print(f"DO PAOUT CENTS={self.vendCents} DOLLARDs={dollars} QUARTERS={quarters}")

      for i in range(0,dollars):
        self.parent.pins_out[2].set(HIGH)
        print("** DOLLAR")
        time.sleep(payoutTime)
        self.parent.pins_out[2].set(LOW)
        time.sleep(payoutTime)

      for i in range(0,quarters):
        self.parent.pins_out[3].set(HIGH)
        print("** QUARTER")
        time.sleep(payoutTime)
        self.parent.pins_out[3].set(LOW)
        time.sleep(payoutTime)

      print(f"PAYOUT COMPLETE {quarters} {dollars}")
      #self.payoutComplete.emit()
      self.parent.slotUIEvent("payoutComplete")

# Query Balance
class BalanceWorker(QObject):
    parent = None

    def run(self):
        try:
          """Long-running task."""
          print ("START BalanceWorker")
          url = self.parent.app.config.value("Auth.VendingUrlPrefix")
          username = self.parent.app.config.value("Auth.HttpAuthUser")
          password = self.parent.app.config.value("Auth.HttpAuthPassword")
          name = self.parent.activeMemberRecord.name
          tag = self.parent.activeMemberRecord.tag
          url = f"{url}/queryBalance/{name}" # FIXME!
          print ("BalanceWorker VENDING URL UIS",url,name,tag)
          self.parent.vendingReason="Attempt"
          self.parent.vendingStatus=False
          with requests.get(url, auth=(username, password)) as conn:
            print ("CONTENT GOT",conn.content)
            print ("START END SLEEP")
            if (conn.status_code >= 200) and (conn.status_code <=299):
              # Check result
              self.parent.balance=0
              try:
                vendresult = json.loads(conn.content)
                print ("BalanceWorker",vendresult)
                if vendresult['status'] != 'success':
                  self.parent.vendingResult=vendresult['description']
                  # TODO HANDLE BALANCE ERROR
                else:
                  self.parent.balance=vendresult['balance']
                  self.parent.lastLog=vendresult['lastLog']
              except BaseException as e:
                  self.parent.vendingResult="Malformed Response"
                  print ("BalanceWorker Vend Excetion",e)
            else:
              self.parent.vendingResult=f"HTTP Error {conn.status_code}"
        except BaseException as e:
            self.parent.vendingResult=str(e)
            print ("BalanceWorker",e,type(e),dir(e))
        #print ("BalanceWorker Emit",self.parent.balance)
        self.parent.gotBalance.emit(self.parent.balance/100)
        self.parent.slotUIEvent("gotBalance")

# Original Payment
class Worker(QObject):
    finished = pyqtSignal()
    downloadComplete = pyqtSignal(name="downloadComplete")
    parent = None

    def run(self):
        try:
          """Long-running task."""
          print ("START WORKER SLEEP")
          time.sleep(1)
          url = self.parent.app.config.value("Auth.VendingUrlPrefix")
          username = self.parent.app.config.value("Auth.HttpAuthUser")
          password = self.parent.app.config.value("Auth.HttpAuthPassword")
          name = self.parent.activeMemberRecord.name
          tag = self.parent.activeMemberRecord.tag
          amount = self.parent.totalCharge*100
          print ("VENDING URL UIS",url,name,tag,amount)
          self.parent.vendingReason="Attempt"
          self.parent.vendingStatus=False
          headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

          if (self.parent.vendingOp == "purchase"):
            data = {"lastLog":self.parent.lastLog,'amount':amount,'prevBalance':self.parent.balance}
            url = f"{url}/chargeAccount/{name}" 
          elif (self.parent.vendingOp == "reup"):
            surcharge = self.parent.app.config.value("Vending.VendingSurcharge")
            totalCharge = self.parent.reupAmount + surcharge
            newBalance = (self.parent.balance/100) + self.parent.reupAmount - (self.parent.vendingAmount)
            data = {"lastLog":self.parent.lastLog,"addAmount": int(100*self.parent.reupAmount), "totalCharge":int(100*totalCharge), "prevBalance":self.parent.balance, 
              "serviceFee":(100*surcharge),"purchaseAmt":int(100*self.parent.vendingAmount), "newBalance":int(100*newBalance)}
            print ("VENDING REUP REQUEST",data)
            url = f"{url}/reupBalance/{name}"
          else:
            self.parent.slotUIEvent("downloadComplete")
            self.parent.vendingOp = "none"
            self.parent.lastLog = -1
            self.parent.vendingStatus=False
            self.parent.vendingResult="Internal Error"
            self.logger.error('VENDING from invalid state')
            self.parent.vendingOp = "none"
            self.finished.emit()
            self.downloadComplete.emit()
            self.parent.slotUIEvent("downloadComplete")
            return
          with requests.post(url, headers=headers,data=json.dumps(data), auth=(username, password)) as conn:
            print ("CONTENT GOT",conn.content)
            print ("START END SLEEP")
            if (conn.status_code >= 200) and (conn.status_code <=299):
              # Check result
              try:
                vendresult = json.loads(conn.content)
                print (vendresult)
                if vendresult['status'] != 'success':
                  self.parent.vendingResult=vendresult['description']
                else:
                  self.parent.vendingStatus=True
                  self.parent.vendingResult="Payment Complete"
              except BaseException as e:
                  self.parent.vendingResult="Malformed Response"
                  print ("Vend Excetion",e)
            else:
              self.parent.vendingResult=f"HTTP Error {conn.status_code}"
        except BaseException as e:
            self.parent.vendingResult=str(e)
            print (e,type(e),dir(e))
        self.parent.vendingOp = "none"
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
    STATE_VENDING_CONFIRM_REUP = 'VendingConfirmReup'
    STATE_VENDING_REUP = 'VendingReup'
    STATE_VENDING_INPROGRESS = 'VendingInProgress'
    STATE_VENDING_COMPLETE = 'VendingComplete'
    vendingAmount=1
    purchaseAmount=0
    vendingChanged = pyqtSignal(bool, str,name="vendingResult", arguments=['status','result'])
    vendingConfirmData = pyqtSignal(float,float,float, name="vendingConfirmData", arguments=['currentBalance','vendingAmount',"newBalance"])
    vendingMinMax = pyqtSignal(float, float, float, name="vendingMinMax", arguments=['vendingMinimum','vendingMaximum','interval'])
    vendingResult = "Indeterminiate"
    vendingStatus = False
    vendingOp = "none"
    gotBalance = pyqtSignal(int,name="gotBalance", arguments=['currentBalance'])
    getPurchaseData = pyqtSignal(int,float,name="getPurchaseData", arguments=['currentBalance','currentVendingAmount'])
    VendingConfirmReup = pyqtSignal(float,float,float,float,float,float,name="vendingConfirmReup", arguments=['curBal','thisPurch','svgChg','addAmt','totalChg','newBal'])

    def __init__(self, *args, **kwargs):
        PersonalitySimple.__init__(self, *args, **kwargs)
        
        self.app.rootContext().setContextProperty("vendingAmount", 1)
        self.states[self.STATE_VENDING_LIST] = self.stateVendingList
        self.states[self.STATE_VENDING_INPROGRESS] = self.stateVendingInProgress
        self.states[self.STATE_VENDING_COMPLETE] = self.stateVendingComplete
        self.states[self.STATE_VENDING_CONFIRM] = self.stateVendingConfirm
        self.states[self.STATE_VENDING_CONFIRM_REUP] = self.stateVendingConfirmReup
        self.states[self.STATE_VENDING_REUP] = self.stateVendingReup

    @pyqtProperty(float)
    def reupAmount(self):
        return self._reupAmount

    @reupAmount.setter
    def reupAmount(self, value):
        self._reupAmount = value

    @pyqtProperty(float)
    def vendingAmount(self):
        return self._vendingAmount

    @vendingAmount.setter
    def vendingAmount(self, value):
        self._vendingAmount = value

    # Emmit MANUALLY only @pyqtProperty(bool)
    #def vendingStatus(self):
    #    return self._vendingStatus

    # Emmit MANUALLY only @vendingStatus.setter
    #@vendingStatus.setter
    #def vendingStatus(self, value):
    #    self._vendingStatus = value

    # Emmit  MANUALLY only @pyqtProperty(str, notify=vendingChanged)

    #@vendingResult.setter
    #def vendingResult(self, value):
    #    self._vendingResult = value
    #    # Emit MANUALLY self.vendingChanged.emit(self._vendingStatus,self._vendingResult)

    # enable tool
    def enableTool(self):
        self.logger.debug('VENDING ENABLE TOOL')
        self.pins_out[0].set(HIGH)
        self.pins_out[1].set(HIGH)


    # disable tool
    def disableTool(self):
        self.logger.debug('VENDING DISABLE TOOL')
        self.pins_out[0].set(LOW)
        self.pins_out[1].set(LOW)



    #############################################
    ## STATE_VENDING_REUP (Repelenish)
    #############################################
    def stateVendingReup(self):
        if self.phENTER:
            self.logger.debug('VENDING ReUp Enter')
            self.getPurchaseData.emit(self.balance/100,self.vendingAmount)
            return self.goActive()

        elif self.phACTIVE:
            self.logger.debug('VENDING ReUp active')
            if self.wakereason == self.REASON_UI and self.uievent == 'VendingAborted':
                self.vendingResult = "Payment Aborted"
                self.vendingStatus = False
                self.vendingChanged.emit(self.vendingStatus,self.vendingResult)
                return self.exitAndGoto(self.STATE_VENDING_COMPLETE)
            elif self.wakereason == self.REASON_UI and self.uievent == 'ReupAccepted':
                va = float(self.reupAmount)
                print('VENDING REUP CONFIRMED',va,type(self.reupAmount))
                return self.exitAndGoto(self.STATE_VENDING_CONFIRM_REUP)
                

            return False

        elif self.phEXIT:
            self.logger.debug('VENDING CONFIRM exit')
            self.pin_led1.set(LOW)
            return self.goNextState()

    #############################################
    ## STATE_VENDING_INPROGRESS
    #############################################
    def stateVendingInProgress(self):
        if self.phENTER:
            self.thread = QThread()
            self.worker = Worker()
            self.worker.parent=self
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.thread.start()
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            xxx=  self.goActive()
            return xxx

        elif self.phACTIVE:
            self.logger.debug('VENDING INPROGRESS active')
            if self.wakereason == self.REASON_UI and self.uievent == 'VendingFailed':
                self.vendingStatus = False
                self.vendingResult = "Payment Failed"
                self.logger.debug('VENDING INPROGRESS FAILED')
                self.thread.quit()
                self.thread.wait(9999999)
                del self.thread
                self.vendingChanged.emit(self.vendingStatus,self.vendingResult)
                return self.exitAndGoto(self.STATE_VENDING_COMPLETE)
            elif self.wakereason == self.REASON_UI and self.uievent == 'VendingSuccessful':
                va = float(self.totalCharge)
                self.logger.debug('VENDING INPROGRESS SUCCCEDED')
                self.vendingStatus = True
                self.vendingResult = "Payment Complete"
                self.thread.quit()
                self.thread.wait(9999999)
                del self.thread
                self.vendingChanged.emit(self.vendingStatus,self.vendingResult)
                return self.exitAndGoto(self.STATE_VENDING_COMPLETE)
            elif self.wakereason == self.REASON_UI and self.uievent == 'downloadComplete':
                self.thread.quit()
                self.thread.wait(9999999)
                del self.thread
                self.vendingChanged.emit(self.vendingStatus,self.vendingResult)
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
            self.idleRequest=False
            self.logger.debug('VENDING COMPLETE Enter')
            name = self.activeMemberRecord.name
            amount = self.vendingAmount
            o = { "Member":name,"Amount":amount,"Success":self.vendingStatus,"Reason":self.vendingResult}
            self.app.mqtt.slotPublishSubtopic('vending/report', json.dumps(o))
            self.enableTool()


            if (self.vendingStatus == True):
              # Payout kicker
              self.payoutDone=False
              self.payoutThread = QThread()
              self.payoutWorker = Payout()
              self.payoutWorker.vendCents = amount*100
              self.payoutWorker.parent=self
              self.payoutWorker.moveToThread(self.payoutThread)
              self.payoutThread.started.connect(self.payoutWorker.run)
              self.payoutThread.start()
              print ("INITIATED PAYOUT")
            else:
              self.payoutDone=True


            return self.goActive()

        elif self.phACTIVE:
            self.logger.debug('VENDING COMPLETE active')
            if self.vendingStatus:
              if self.wakereason == self.REASON_UI and self.uievent == 'payoutComplete' and not self.payoutDone:
                self.payoutDone=True
                self.payoutThread.quit()
                self.payoutThread.wait(9999999)
                del self.payoutThread

            # "Idle" might have occured before or after payout thread complete!
            if self.wakereason == self.REASON_UI and self.uievent == 'Idle':
              self.idleRequest = True

            # If payout thread AND gui say we're done...
            if self.payoutDone and self.idleRequest:
              print('VENDING FINALLY DONE')
              self.disableTool()
              return self.exitAndGoto(self.STATE_IDLE)
                

            return False

        elif self.phEXIT:
            self.disableTool()
            self.logger.debug('VENDING COMPLETE exit')
            self.pin_led1.set(LOW)
            return self.goNextState()

    #############################################
    ## STATE_VENDING_LIST
    #############################################
    def stateVendingList(self):
        if self.phENTER:
            self.logger.debug('VENDING LIST Enter')
            self.app.rootContext().setContextProperty("vendingAmount", 1)
            self.activeMemberRecord.loggedIn = True
            self.pin_led1.set(HIGH)
            self.vendingAmount =1
            maxCharge = self.app.config.value("Vending.VendingMaximum")
            minCharge = self.app.config.value("Vending.VendingMinimum")
            increment = self.app.config.value("Vending.Increment")
            self.vendingMinMax.emit(minCharge,maxCharge,increment)

            self.thread = QThread()
            self.worker = BalanceWorker()
            self.worker.parent=self
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.thread.start()
            #self.worker.gotBalance.connect(self.worker.deleteLater)

            return self.goActive()

        elif self.phACTIVE:
            self.logger.debug('VENDING LIST active')
            if self.wakereason == self.REASON_UI and self.uievent == 'gotBalance':
                self.thread.quit()
                self.thread.wait(9999999)
                del self.thread
                #self.gotBalance.emit(777)
            if self.wakereason == self.REASON_UI and self.uievent == 'VendingAborted':
                self.vendingResult = "Payment Aborted"
                self.vendingStatus = False
                self.vendingChanged.emit(self.vendingStatus,self.vendingResult)
                return self.exitAndGoto(self.STATE_VENDING_COMPLETE)
            elif self.wakereason == self.REASON_UI and self.uievent == 'VendingConfirm':
                va = float(self.vendingAmount)
                #print('VENDING ACCEPTED',self.vendingAmount,"with balance",self.balance)
                if (self.vendingAmount*100) <= self.balance:
                  return self.exitAndGoto(self.STATE_VENDING_CONFIRM)
                else:
                  self.purchaseEmount = self.vendingAmount
                  return self.exitAndGoto(self.STATE_VENDING_REUP)
                

            return False

        elif self.phEXIT:
            self.logger.debug('VENDING LIST exit')
            self.pin_led1.set(LOW)
            return self.goNextState()

    #############################################
    ## STATE_VENDING_CONFIRM_REUP
    #############################################
    def stateVendingConfirmReup(self):
        if self.phENTER:
            self.logger.debug('VENDING CONFIRM REUP Enter')
            self.telemetryEvent.emit('personality/login', json.dumps({'allowed': True, 'member': self.activeMemberRecord.name}))
            self.activeMemberRecord.loggedIn = True
            self.pin_led1.set(HIGH)
            surcharge = self.app.config.value("Vending.VendingSurcharge")
            self.totalCharge = self.reupAmount + surcharge
            newBalance = (self.balance/100) + self.reupAmount - (self.vendingAmount)
            self.VendingConfirmReup.emit(self.balance/100,self.vendingAmount,surcharge,self.reupAmount,self.totalCharge,newBalance)
            return self.goActive()

        elif self.phACTIVE:
            self.logger.debug('VENDING CONFIRM REUP active')
            if self.wakereason == self.REASON_UI and self.uievent == 'VendingAborted':
                self.vendingResult = "Payment Aborted"
                self.vendingStatus = False
                self.vendingChanged.emit(self.vendingStatus,self.vendingResult)
                return self.exitAndGoto(self.STATE_VENDING_COMPLETE)
            elif self.wakereason == self.REASON_UI and self.uievent == 'VendingAccepted':
                self.vendingOp = "reup"
                va = float(self.vendingAmount)
                print('VENDING CONFIRMED REUP ',va,type(self.vendingAmount))
                return self.exitAndGoto(self.STATE_VENDING_INPROGRESS)
                

            return False

        elif self.phEXIT:
            self.logger.debug('VENDING CONFIRM REUP exit')
            self.pin_led1.set(LOW)
            return self.goNextState()
    #############################################
    ## STATE_VENDING_CONFIRM
    #############################################
    def stateVendingConfirm(self):
        if self.phENTER:
            self.logger.debug('VENDING CONFIRM Enter')
            self.telemetryEvent.emit('personality/login', json.dumps({'allowed': True, 'member': self.activeMemberRecord.name}))
            self.activeMemberRecord.loggedIn = True
            self.pin_led1.set(HIGH)
            surcharge = self.app.config.value("Vending.VendingSurcharge")
            self.totalCharge = self.vendingAmount 
            #self.vendingConfirmData.emit(f"${self.vendingAmount:0.2f}",f"${surcharge:0.2f}",f"${self.totalCharge:0.2f}",False if surcharge == 0 else True)
            newBal = (self.balance/100) - self.vendingAmount
            self.vendingConfirmData.emit(self.balance/100,self.vendingAmount,newBal)
            return self.goActive()

        elif self.phACTIVE:
            self.logger.debug('VENDING CONFIRM active')
            if self.wakereason == self.REASON_UI and self.uievent == 'VendingAborted':
                self.vendingResult = "Payment Aborted"
                self.vendingStatus = False
                self.vendingChanged.emit(self.vendingStatus,self.vendingResult)
                return self.exitAndGoto(self.STATE_VENDING_COMPLETE)
            elif self.wakereason == self.REASON_UI and self.uievent == 'VendingAccepted':
                va = float(self.vendingAmount)
                print('VENDING CONFIRMED',va,type(self.vendingAmount))
                self.vendingOp = "purchase"
                return self.exitAndGoto(self.STATE_VENDING_INPROGRESS)
                

            return False

        elif self.phEXIT:
            self.logger.debug('VENDING CONFIRM exit')
            self.pin_led1.set(LOW)
            return self.goNextState()
    #############################################
    ## STATE_IDLE
    #############################################
    def stateIdle(self):
        if self.phENTER:
            self.logger.info('simple stateIdle enter')
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
