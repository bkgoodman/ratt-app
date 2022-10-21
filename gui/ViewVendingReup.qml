// --------------------------------------------------------------------------
//  _____       ______________
// |  __ \   /\|__   ____   __|
// | |__) | /  \  | |    | |
// |  _  / / /\ \ | |    | |
// | | \ \/ ____ \| |    | |
// |_|  \_\/    \_\_|    |_|    ... RFID ALL THE THINGS!
//
// A resource access control and telemetry solution for Makerspaces
//
// Developed at MakeIt Labs - New Hampshire's First & Largest Makerspace
// http://www.makeitlabs.com/
//
// Copyright 2018 MakeIt Labs
//
// Permission is hereby granted, free of charge, to any person obtaining a
// copy of this software and associated documentation files (the "Software"),
// to deal in the Software without restriction, including without limitation
// the rights to use, copy, modify, merge, publish, distribute, sublicense,
// and/or sell copies of the Software, and to permit persons to whom the
// Software is furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
// WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
// CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
// --------------------------------------------------------------------------
//
// Author: Steve Richardson (steve.richardson@makeitlabs.com)
//

import QtQuick 2.6
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.3

View {
    id: root
    name: "Recharge"

    property real reupAmount: 5.00
    property real vendingAmount
    property string reupAmountString: "5.00"
    property string newBalanceString: "-.--"
    property real vendingMin: 0
    property real vendingMax: 10
    property real vendingIncrement: 0.25
    property int balance: 0

    Connections {
        target: personality
	onVendingMinMax: {
		vendingMin = vendingMinimum
		vendingMax = vendingMaximum
		vendingIncrement = vendingIncrement
                console.info("GOT CURRENT BALANCE MinMax")
		}
	onGetPurchaseData: {
                // currentBalance, currentVendingAmount
                balance=currentBalance
                vendingAmount=currentVendingAmount
                console.info("GOT PURCHASE DATA")
                reupAmountString = moneyString(reupAmount)
                newBalanceString = moneyString((balance)+reupAmount-vendingAmount)
		}
}


    function _show() {
      status.keyEscActive = true;
      status.keyReturnActive = true;
      status.keyUpActive = true;
      status.keyDownActive = true;

      sound.vendingListAudio.play();
      reupAmount = 5;
      timeoutTimer.start();
      status.keyEscLabel = "\u2716"
      status.keyReturnLabel = "OK"
    }

    function moneyString(val) {
        var dollars   = Math.floor(val);
        var cents = Math.floor(val*100) - Math.floor(dollars*100);

        if (cents < 10) {cents = "0" + cents;}
        return dollars.toString() + '.' + cents  ;
    }

    function _hide() {
      timeoutTimer.stop();

      sound.vendingListAudio.stop();

    }

    function keyEscape(pressed) {
      if (pressed ) {
	      reupAmount=1;
	      reupAmountString = moneyString(reupAmount)
	      newBalanceString = moneyString(reupAmount)
	      sound.vendingCanceledAudio.play();
	      appWindow.uiEvent('VendingAborted'); 
	}
      return true;
    }

    function keyUp(pressed) {
      if (pressed) {
        timeoutTimer.restart();
	if (reupAmount < vendingMax) {
        reupAmount += vendingIncrement
	}
        reupAmountString = moneyString(reupAmount)
        console.info(balance,reupAmount,vendingAmount, (balance)+reupAmount-vendingAmount)
        newBalanceString = moneyString((balance)+reupAmount-vendingAmount)
        appWindow.uiEvent('VendingKeyUp');
      }
      return true;
    }
    function keyDown(pressed) {
     if (pressed) {
        timeoutTimer.restart()
        if ((balance+reupAmount-(vendingAmount+vendingIncrement)) >= 0) {
          reupAmount -= vendingIncrement
          var newamt = (balance)+reupAmount-vendingAmount
          if (reupAmount < vendingMin) {  reupAmount = vendingMin}
          reupAmountString = moneyString(reupAmount)
          newBalanceString = moneyString(newamt)
          appWindow.uiEvent('VendingKeyDown');
        }
        
      }
      return true;
    }


    function keyReturn(pressed) {
        if (pressed) {
          personality.reupAmount = reupAmount
          reupAmount=1;
          reupAmountString = moneyString(reupAmount)
          appWindow.uiEvent('ReupAccepted');
        } 
      return true;
    }


    Timer {
      id: timeoutTimer
      interval: 25000
      running: false
      repeat: false
      onTriggered: {
          stop();
          //appWindow.uiEvent('VendingAborted');
          console.info("VendingReup Timeout Timer\n");
          keyEscape(true);
      }
    }


    SequentialAnimation {
        running: shown
        loops: Animation.Infinite
        ColorAnimation {
            target: root
            property: "color"
            from: "#004400"
            to: "#004444"
            duration: 5000
        }
        ColorAnimation {
            target: root
            property: "color"
            from: "#004444"
            to: "#004400"
            duration: 5000
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 2
        Label {
            Layout.fillWidth: true
            Layout.maximumHeight: 10
            Layout.preferredHeight: 10
            text: "Current Balance: $"+moneyString(balance)
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: 10
            font.weight: Font.Bold
            color: "#ffff00"
        }
        Label {
            Layout.fillWidth: true
            Layout.maximumHeight: 10
            Layout.preferredHeight: 10
            text: "Purchase: $"+moneyString(vendingAmount)
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: 10
            font.weight: Font.Bold
            color: "#ff8080"
        }
        Label {
            Layout.fillWidth: true
            Layout.maximumHeight: 18
            Layout.preferredHeight: 18
            text: "Amount to Add"
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: 18
            font.weight: Font.Bold
            color: "#80ff80"
        }
        Label {
            Layout.fillWidth: true
            Layout.maximumHeight: 18
            Layout.preferredHeight: 18

            id: vendAmount
            text: "$"+reupAmountString
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: 18
            font.weight: Font.DemiBold
            color: "#80ff80"
        }
        Label {
            Layout.fillWidth: true
            Layout.maximumHeight: 10
            Layout.preferredHeight: 10
            text: "New Balance: $"+newBalanceString
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: 10
            font.weight: Font.Normal
            color: "#ffff00"
        }
        Label {
            Layout.fillWidth: true
            text: "Select amount then press OK"
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: 10
            font.weight: Font.Normal
            color: "#ffffff"
        }
    }
}
