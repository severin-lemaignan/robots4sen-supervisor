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
    flags: Qt.Window | Qt.FramelessWindowHint
    visibility: Window.FullScreen
    title: qsTr("robots4SEN supervisor")


    Page {
        id: main
        anchors.fill: parent


        SwipeView {
            anchors.fill:parent
            currentIndex: tabBar.currentIndex
            interactive: false // disable swipe gesture

            Interactions {
                id: interactionsTab
            }
            Discover {
                id: peopleLocalisationTab
                clip: true
            }
            Actions {
                id: actionsTab
            }
            PhotoCapture {
                id: captureTab
            }
            Settings {
                id: settingsTab
            }
        }

        Status {
            id: status
            x: 15
            y: 15
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


    MicButton {
        id: questions_mic
        name: "questions"
        source: "res/microphone-question.svg"
        record_modal: record_modal
        bg_color: "#b2ce95"

        anchors.left: status.left
        anchors.top: status.bottom
        anchors.topMargin: 30
    }

    MicButton {
        id: event_mic
        name: "event"
        source: "res/microphone-event.svg"
        record_modal: record_modal
        bg_color: "#cea695"

        anchors.left: questions_mic.left
        anchors.top: questions_mic.bottom
        anchors.topMargin: 130
    }


    MicButton {
        id: chat_mic
        name: "chat"
        source: "res/microphone-interview.svg"
        record_modal: record_modal
        bg_color: "#ad7fa8"

        anchors.left: event_mic.left
        anchors.top: event_mic.bottom
        anchors.topMargin: 130
    }

    MicButton {
        id: other_mic
        name: "other"
        record_modal: record_modal
        bg_color: "#e9b96e"

        anchors.left: chat_mic.left
        anchors.top: chat_mic.bottom
        anchors.topMargin: 130
    }

        footer: TabBar {
            id: tabBar
            contentHeight: 0.1 * parent.height

            TabButton {
                id: interactionsBtn
                display: AbstractButton.IconOnly
                icon.source: "res/atom-variant.svg"
                icon.height: parent.height * 0.7
                icon.width: parent.height * 0.7
            }

            TabButton {
                id: peopleLocalisationBtn
                display: AbstractButton.IconOnly
                icon.source: "res/access-point.svg"
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
