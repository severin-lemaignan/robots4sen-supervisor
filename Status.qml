import QtQuick 2.0
import QtGraphicalEffects 1.12

Item {
    id: element
    width: 150
    height: 150



    Image {
            id: connection
            visible: false
            source: "res/robot-outline-white.svg"
            fillMode: Image.PreserveAspectFit
            sourceSize: Qt.size(parent.width, parent.height)

    }

    ColorOverlay {
            anchors.fill: connection
            source: connection
            color: naoqi.awake ? 'green' : 'red'

            MouseArea {
                id: onoff
                anchors.fill: parent
                onClicked: naoqi.awake ? naoqi.rest() : naoqi.wakeup()
            }
    }

    Image {
            id: battery
            anchors.left: connection.right
            anchors.leftMargin: 0
            visible: naoqi.connected
            source: naoqi.plugged ? (
                        naoqi.battery < 0.1 ? "res/battery/battery-charging-10.svg":
                        naoqi.battery < 0.2 ? "res/battery/battery-charging-20.svg":
                        naoqi.battery < 0.3 ? "res/battery/battery-charging-30.svg":
                        naoqi.battery < 0.4 ? "res/battery/battery-charging-40.svg":
                        naoqi.battery < 0.5 ? "res/battery/battery-charging-50.svg":
                        naoqi.battery < 0.6 ? "res/battery/battery-charging-60.svg":
                        naoqi.battery < 0.7 ? "res/battery/battery-charging-70.svg":
                        naoqi.battery < 0.8 ? "res/battery/battery-charging-80.svg":
                        naoqi.battery < 0.9 ? "res/battery/battery-charging-90.svg":
                        "res/battery/battery-charging.svg"
                    ):(
                        naoqi.battery < 0.1 ? "res/battery/battery-10.svg":
                        naoqi.battery < 0.2 ? "res/battery/battery-20.svg":
                        naoqi.battery < 0.3 ? "res/battery/battery-30.svg":
                        naoqi.battery < 0.4 ? "res/battery/battery-40.svg":
                        naoqi.battery < 0.5 ? "res/battery/battery-50.svg":
                        naoqi.battery < 0.6 ? "res/battery/battery-60.svg":
                        naoqi.battery < 0.7 ? "res/battery/battery-70.svg":
                        naoqi.battery < 0.8 ? "res/battery/battery-80.svg":
                        naoqi.battery < 0.9 ? "res/battery/battery-90.svg":
                        "res/battery/battery.svg"
                    )

         fillMode: Image.PreserveAspectFit
            sourceSize: Qt.size(parent.width, parent.height)
    }

}
