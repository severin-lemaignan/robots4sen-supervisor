import QtQuick 2.10
import QtQuick.Window 2.10
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.3

import Naoqi 1.0


Window {
    id: window
    visible: true
    width: 2736
    height: 1824
    title: qsTr("robots4SEN supervisor")


    Page {
        id: main
        anchors.fill: parent


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

        Status {
            id: status
            x: 15
            y: 15
        }

        Rectangle {
            anchors.right: record_btn.horizontalCenter
            height: record_btn.height
            anchors.top: record_btn.top
            anchors.left: parent.left

            color: "#f66151"
        }

        Rectangle {
            id: record_modal
            z: 10
            anchors.fill: parent
            visible: false

            color: "#cc000000"

            Image {
                id: mic
                anchors.centerIn: parent
                source: "res/microphone.svg"
                width: 100
                height: width
                sourceSize.width: width
                sourceSize.height: height
            }

            Text {
                anchors.horizontalCenter: mic.horizontalCenter
                anchors.top: mic.bottom
                anchors.topMargin: 30

                font.pointSize: 12

                //text: (audiorecorder.duration/1000).toFixed(2) + "s"
                text: "(release to stop recording)"
                color: "#cccccc"
            }



        }


        IconButton {
            id: record_btn

            anchors.left: status.left
            anchors.top: status.bottom
            anchors.topMargin: 30
            height: 100

            noborder: true

            source: "res/microphone.svg"

            AudioRecorder {
                id: audiorecorder
                location: "default.ogg"
            }

            onPressedChanged: {
                if (pressed) {
                    var dateTime = new Date().toLocaleString(Qt.locale("en_GB"), "yyyy-MM-dd-HH-mm-ss");
                    audiorecorder.location = "./audionote-" + dateTime + ".ogg"
                    audiorecorder.record();
                    record_modal.visible = true;
                }
                else {
                    audiorecorder.stop();
                    record_modal.visible = false;
                }
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
