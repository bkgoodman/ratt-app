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
    name: "Vending Complete"

    color: "#0000cc"

    property bool isFailed 
    Connections {
        target: personality
	onVendingResult: {
		// status, result
		// Doesn't do anything??
                message.text = result
		//personality.vendingResult = result
		//personality.vendingStats = status
		isFailed = status
 		if (isFailed) {
		    sound.vendingSuccessAudio.play();
		} else {
		    sound.vendingFailedAudio.play();
		}
		}
	}

    function _show() {
      showTimer.start();
      status.keyEscActive = true;
      status.keyDownActive = false;
      status.keyUpActive = false;
      status.keyReturnActive = false;
      status.keyEscLabel = "\u25cf"
    }

    function done() {
		showTimer.stop();
		sound.vendingFailedAudio.stop();
		sound.vendingSuccessAudio.stop();
      		status.keyEscLabel = "\u2716"
		appWindow.uiEvent('Idle'); 
    }

    function keyEscape(pressed) {
	if (pressed) { done()};
      return true;
    }

    Timer {
        id: showTimer
        interval: 10000
        repeat: false
        running: false
        onTriggered: {
            done();
        }
    }

    SequentialAnimation {
        running: shown
        loops: 1
        ColorAnimation {
            target: root
            property: "color"
            from: "#000000"
            to: isFailed ? "#00cc00" : "#cc0000"
            duration: 2000
        }
    }
    ColumnLayout {
        anchors.fill: parent
        Label {
            Layout.fillWidth: true
            text: isFailed ? "Complete" : "Failed"
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: 24
            font.weight: Font.Bold
            color: "#ffff00"
        }
        Label {
            Layout.fillWidth: true
            text: personality.vendingResult
	    id: message
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: 14
            font.weight: Font.Normal
            color: "#ffffff"
        }

    }
}
