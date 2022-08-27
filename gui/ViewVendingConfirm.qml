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
    name: "Vending Confirm"

    color: "#0000cc"

    property string vendingAmount
    property string surchargeAmount
    property string totalAmount
    property bool applySurcharge


    Connections {
        target: personality
	onVendingConfirmData: {
		// vendingAmount, surchargeAmount, totalAmount, hasSurcharge
		// Doesn't do anything??
                amountText.text = vendingAmount
                surchargeText.text = surchargeAmount
                totalText.text = totalAmount
		applySurcharge = hasSurcharge 
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

    }

    function done() {
		showTimer.stop();
		appWindow.uiEvent('VendingAccepted'); 
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

	Item {
        Layout.preferredWidth: 160
        Layout.maximumHeight: 12
        Layout.preferredHeight: 12
        Label {
            width: parent.width
            Layout.fillWidth: true
            Layout.fillHeight: true
            text: "Confirm Payment"
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: 18  
            font.weight: Font.Bold
            color: "#ffff00"
        }
	}
        
      
RowLayout {
            Layout.preferredHeight: 10
    Item {
    Layout.preferredWidth: 96
       Label {
                    width: parent.width
                    text: "Vending:"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: 14
                    color: "#ffff00"
                    font.weight: Font.Normal
                                    
       }
        
    }    
    Item {
    Layout.preferredWidth: 128
       Label {
	   id: amountText
           text:"--"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: 14
                    color: "#ffffff"
       }
        
    }    
}

RowLayout {
            Layout.preferredHeight: 10
visible: applySurcharge
    Item {
    Layout.preferredWidth: 96
       Label {
                    width: parent.width
                    text: "Surcharge:"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: 14
                    color: "#ffff00"
                    font.weight: Font.Normal
                                    
       }
        
    }    
    Item {
    Layout.preferredWidth: 128
       Label {
	   id: surchargeText
           text:"--"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: 14
                    color: "#ffffff"
       }
        
    }    
}
RowLayout {
            Layout.preferredHeight: 18
    Item {
    Layout.preferredWidth: 96
       Label {
                    width: parent.width
                    text: "Total:"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: 14
                    color: "#ffff00"
                    font.weight: Font.Bold
                                    
       }
        
    }    
    Item {
    Layout.preferredWidth: 128
       Label {
	   id: totalText
           text:"--"
                    horizontalAlignment: Text.AlignRight
                    font.pixelSize: 14
                    color: "#00ff00"
                    font.weight: Font.Bold
       }
        
    }    
}


RowLayout {
            Layout.preferredHeight: 22
    Item {
        Layout.preferredWidth: 160
        Layout.maximumHeight: 18
        Layout.preferredHeight: 18

       Label {
                    width: parent.width
                    text: "Press \"Pay\" to Confirm"
                    horizontalAlignment: Text.AlignHCenter
                    font.pixelSize: 10
                    color: "#ffff00"
                    font.weight: Font.Normal
                                    
       }
        
    } 
    }
        }
        }
