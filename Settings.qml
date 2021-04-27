import QtQuick 2.0
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.5

Item {

    Item {
            id: settings
            anchors.left: parent.left
            width: parent.width * 0.45
            height: parent.height

            IconButton {
                    id: rest
                    source: "res/robot-angry-outline.svg"
                    anchors.centerIn: parent
                    noborder: false
                    label: "rest"
                    height: parent.width * 0.25
                    onPressedChanged: {
                        if (pressed) {
                            naoqi.rest();
                        }
                    }
            }
            IconButton {
                    id: wakeup
                    source: "res/robot-angry-outline.svg"
                    anchors.left: rest.right
                    anchors.leftMargin: 30
                    anchors.top: rest.top
                    noborder: false
                    label: "wake up"
                    height: parent.width * 0.25
                    onPressedChanged: {
                        if (pressed) {
                            naoqi.wakeup();
                        }
                    }
            }
            IconButton {
                    id: arm_stiffness 
                    source: "res/robot-angry-outline.svg"
                    anchors.left: wakeup.right
                    anchors.leftMargin: 30
                    anchors.top: rest.top
                    noborder: false
                    label: "toggle arm stif."
                    height: parent.width * 0.25
                    onPressedChanged: {
                        if (pressed) {
                            naoqi.toggleArmsStiffness();
                        }
                    }
            }

    }

}

