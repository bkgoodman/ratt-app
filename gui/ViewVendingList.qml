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
    name: "Vending"

    property real vendingAmount: 1.00
    property string vendingAmountString: "1.00"
    property real vendingMin: 0
    property real vendingMax: 10

    Connections {
        target: personality
	onVendingMinMax: {
		vendingMin = vendingMinimum
		vendingMax = vendingMaximum
		}
}


    function _show() {
      status.keyEscActive = true;
      status.keyReturnActive = true;
      status.keyUpActive = true;
      status.keyDownActive = true;

      sound.generalAlertAudio.play();
      vendingAmount = 1;
      timeoutTimer.start();
      status.keyEscLabel = "\u2716"
      status.keyReturnLabel = "OK"
    }

    function moneyString(val) {
        var dollars   = Math.floor(val);
        var cents = (val - dollars)*100;

        if (cents < 10) {cents = "0" + cents;}
        return dollars.toString() + '.' + cents  ;
    }

    function _hide() {
      timeoutTimer.stop();

      sound.generalAlertAudio.stop();

    }

    function keyEscape(pressed) {
      if (pressed ) {
	      vendingAmount=1;
	      vendingAmountString = moneyString(vendingAmount)
	      appWindow.uiEvent('VendingAborted'); 
	}
      return true;
    }

    function keyUp(pressed) {
      if (pressed) {
	if (vendingAmount < vendingMax) {
        vendingAmount += 0.25
	}
        vendingAmountString = moneyString(vendingAmount)
        appWindow.uiEvent('VendingKeyUp');
      }
      return true;
    }
    function keyDown(pressed) {
     if (pressed) {
        vendingAmount -= 0.25
	if (vendingAmount < vendingMin) {  vendingAmount = vendingMin}
        vendingAmountString = moneyString(vendingAmount)
        appWindow.uiEvent('VendingKeyDown');
      }
      return true;
    }


    function keyReturn(pressed) {
        if (pressed) {
          personality.vendingAmount = vendingAmount
          vendingAmount=1;
          vendingAmountString = moneyString(vendingAmount)
          appWindow.uiEvent('VendingConfirm');
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
        Label {
            Layout.fillWidth: true
            text: "Enter Amount"
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: 18
            font.weight: Font.Bold
            color: "#ffffff"
        }
        Label {
            Layout.fillWidth: true
            id: vendAmount
            text: "$"+vendingAmountString
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: 20
            font.weight: Font.DemiBold
            color: "#ffff00"
        }
        Label {
            Layout.fillWidth: true
            text: "Use arrows to adjust\nPress OK to Pay"
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: 12
            font.weight: Font.Demi
            color: "#ffffff"
        }
    }
}
