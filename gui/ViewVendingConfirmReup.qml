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
    function moneyString(val) {
        var dollars   = Math.floor(val);
        var cents = (val * 100) - (dollars * 100)

        if (cents < 10) {cents = "0" + cents;}
        return dollars.toString() + '.' + cents  ;
    }
    id: root
    name: "Vending Confirm Reup"

    color: "#0000cc"


    Connections {
        target: personality
	onVendingConfirmReup: {
		// curBal, thisPurch, svgChg, addAmt, totalChg, newBal
		// Doesn't do anything??
                curBalanceText.text = moneyString(curBal)
                purchaseText.text = moneyString(thisPurch)
                amountText.text = moneyString(addAmt)
                surchargeText.text = moneyString(svgChg)
                totalText.text = moneyString(totalChg)
                newBalanceText.text = moneyString(newBal)
		status.keyReturnLabel = "Pay"
	   }
	}

    function _show() {
      showTimer.start();
      sound.vendingConfirmAudio.play();
      status.keyEscActive = true; 
      status.keyReturnActive = true; 
      status.keyDownActive = false;
      status.keyUpActive = false;
      status.keyReturnLabel = "Pay"

    }

    function done() {
		showTimer.stop();
		status.keyReturnLabel =  "\u25cf"
    }

    function keyEscape(pressed) {
	if (pressed) { 
		showTimer.stop();
		status.keyReturnLabel =  "\u25cf"
	        sound.vendingCanceledAudio.play();
		appWindow.uiEvent('VendingAborted'); 
	};
      return true;
    }
    function keyReturn(pressed) {
	if (pressed) { 
		showTimer.stop();
	        sound.vendingConfirmAudio.stop();
		status.keyReturnLabel =  "\u25cf"
		appWindow.uiEvent('VendingAccepted'); 
	};
      return true;
    }

    Timer {
        id: showTimer
        interval: 20000
        repeat: false
        running: false
        onTriggered: {
            keyEscape(true);
        }
    }

    SequentialAnimation {
        running: shown
        loops: 1
        ColorAnimation {
            target: root
            property: "color"
            from: "#000000"
            to: "#0000cc"
            duration: 1000
        }
    }

    ColumnLayout {
        spacing:2

    Item {
        Layout.preferredWidth: 160
        Layout.maximumHeight: 8
        Layout.preferredHeight: 8
        Label {
            width: parent.width
            Layout.fillWidth: true
            Layout.fillHeight: true
            text: "Press \"Pay\" To Confirm"
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: 12  
            font.weight: Font.Bold
            color: "#ffff00"
        }
    }
      
    RowLayout {
        Layout.preferredHeight: 10
        Layout.maximumHeight: 10
        Item {
          Layout.preferredWidth: 96
             Label {
                          width: parent.width
                          text: "Cur Balance:"
                          horizontalAlignment: Text.AlignRight
                          font.pixelSize: 12
                          color: "#ffffff"
                          font.weight: Font.Normal
                                          
             }
        }    
        Item {
          Layout.preferredWidth: 128
             Label {
                 id: curBalanceText
                 text:"--"
                          horizontalAlignment: Text.AlignRight
                          font.pixelSize: 12
                          color: "#ffffff"
             }
        }    
    } // End Rowlayout

RowLayout {
            Layout.preferredHeight: 10
        Layout.maximumHeight: 10
//visible: applySurcharge
    Item {
    Layout.preferredWidth: 96
       Label {
                    width: parent.width
                    text: "This Purchase:"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: 12
                    color: "#ff8080"
                    font.weight: Font.Normal
                                    
       }
        
    }    
    Item {
    Layout.preferredWidth: 128
       Label {
	   id: purchaseText
           text:"--"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: 12
                    color: "#ff8080"
                    font.weight: Font.Bold
       }
        
    }    
}

RowLayout {
        Layout.preferredHeight: 10
        Layout.maximumHeight: 10
    Item {
    Layout.preferredWidth: 96
       Label {
                    width: parent.width
                    text: "Amount to Add:"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: 12
                    color: "#ffff00"
                    font.weight: Font.Normal
                                    
       }
        
    }    
    Item {
    Layout.preferredWidth: 128
       Label {
	   id: amountText
           text:"$-.--"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: 12
                    color: "#00ff00"
                    font.weight: Font.Normal
       }
    }    
}
RowLayout {
        Layout.preferredHeight: 10
        Layout.maximumHeight: 10
    Item {
    Layout.preferredWidth: 96
       Label {
                    width: parent.width
                    text: "Service Fee:"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: 12
                    color: "#ffff00"
                    font.weight: Font.Normal
                                    
       }
        
    }    
    Item {
    Layout.preferredWidth: 128
       Label {
	   id: surchargeText
           text:"-.--"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: 12
                    color: "#00ff00"
                    font.weight: Font.Normal
       }
        
    }    
}

RowLayout {
        Layout.preferredHeight: 10
        Layout.maximumHeight: 10
    Item {
    Layout.preferredWidth: 96
       Label {
                    width: parent.width
                    text: "Total Charge:"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: 12
                    color: "#ffff00"
                    font.weight: Font.Normal
                                    
       }
        
    }    
    Item {
    Layout.preferredWidth: 128
       Label {
	   id: totalText
           text:"-.--"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: 12
                    color: "#00ff00"
                    font.weight: Font.Bold
       }
    }    
}





RowLayout {
    Layout.preferredHeight: 10
    Layout.maximumHeight: 10
    Item {
    Layout.preferredWidth: 96
       Label {
                    width: parent.width
                    text: "New Balance:"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: 12
                    color: "#ffffff"
                    font.weight: Font.Normal
                                    
       }
        
    }    
    Item {
    Layout.preferredWidth: 128
       Label {
	   id: newBalanceText
           text:"--"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: 12
                    color: "#ffffff"
                    font.weight: Font.Normal
       }
        
    }    
}

        }
}
