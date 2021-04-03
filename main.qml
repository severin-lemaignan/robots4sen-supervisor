import QtQuick 2.10
import QtQuick.Window 2.10
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.3

import Naoqi 1.0


Window {
    id: window
    visible: true
    width: 640
    height: 480
    title: qsTr("robots4SEN supervisor")


    Page {
        id: main
        anchors.fill: parent

        Status {
            id: status
            x: 15
            y: 15
        }

        IconButton {
            anchors.left: status.left
            anchors.top: status.bottom
            anchors.topMargin: 20
            height: status.height

            source: "res/microphone.svg"

            AudioRecorder {
                id: audiorecorder
                location: "test.ogg"
            }

            onPressedChanged: {
                if (pressed) {
                    audiorecorder.record();
                }
                else {
                    audiorecorder.stop();
                }
            }


        }

        SwipeView {
            anchors.fill:parent
            currentIndex: tabBar.currentIndex
            interactive: false // disable swipe gesture

            Discover {
                id: peopleLocalisationTab
            }
            Actions {
                id: actionsTab
            }
            Item {
                id: bookmarkTab
            }
            PhotoCapture {
                id: captureTab
            }
            Item {
                id: settingsTab
            }
        }



        footer: TabBar {
            id: tabBar
            contentHeight: 0.1 * parent.height

            TabButton {
                id: peopleLocalisationBtn
                display: AbstractButton.IconOnly
                icon.source: "res/atom-variant.svg"
                icon.height: parent.height * 0.7
                icon.width: parent.height * 0.7            }

            TabButton {
                id: actionsBtn
                display: AbstractButton.IconOnly
                icon.source: "res/hand-okay.svg"
                icon.height: parent.height * 0.7
                icon.width: parent.height * 0.7
            }

            TabButton {
                id: bookmarkBtn
                display: AbstractButton.IconOnly
                icon.source: "res/bell-alert.svg"
                icon.height: parent.height * 0.7
                icon.width: parent.height * 0.7
            }

            TabButton {
                id: captureBtn
                display: AbstractButton.IconOnly
                icon.source: "res/camera.svg"
                icon.height: parent.height * 0.7
                icon.width: parent.height * 0.7
            }

            TabButton {
                id: settingsBtn
                display: AbstractButton.IconOnly
                icon.source: "res/robot-confused-outline.svg"
                icon.height: parent.height * 0.7
                icon.width: parent.height * 0.7
            }
        }
    }


}

/*##^##
Designer {
    D{i:0;autoSize:true;height:480;width:640}
}
##^##*/
