import QtQuick 2.10
import QtQuick.Window 2.10
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.3


Window {
    id: window
    visible: true
    width: 640
    height: 480
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
            Rectangle {
                color: "blue"
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
                icon.source: "qrc:/res/atom-variant.svg"
                icon.height: parent.height * 0.7
                icon.width: parent.height * 0.7            }

            TabButton {
                id: actionsBtn
                display: AbstractButton.IconOnly
                icon.source: "qrc:/res/hand-okay.svg"
                icon.height: parent.height * 0.7
                icon.width: parent.height * 0.7
            }

            TabButton {
                id: bookmarkBtn
                display: AbstractButton.IconOnly
                icon.source: "qrc:/res/bell-alert.svg"
                icon.height: parent.height * 0.7
                icon.width: parent.height * 0.7
           }

            TabButton {
                id: captureBtn
                display: AbstractButton.IconOnly
                icon.source: "qrc:/res/camera.svg"
                icon.height: parent.height * 0.7
                icon.width: parent.height * 0.7
            }

            TabButton {
                id: settingsBtn
                display: AbstractButton.IconOnly
                icon.source: "qrc:/res/robot-confused-outline.svg"
                icon.height: parent.height * 0.7
                icon.width: parent.height * 0.7
            }
        }
       }


}

/*##^##
Designer {
    D{i:2;anchors_width:240;anchors_x:35;anchors_y:27}D{i:1;anchors_height:400;anchors_width:200}
}
##^##*/
