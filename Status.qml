import QtQuick 2.0
import QtGraphicalEffects 1.12

Item {
    id: element
    width: 60
    height: 40



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
            color: naoqi.connected ? 'green' : 'red'
    }

    Image {
            id: battery
            anchors.left: connection.right
            anchors.leftMargin: 0
            source: naoqi.battery < 0.1 ? "res/battery/battery-10.svg":
                    naoqi.battery < 0.2 ? "res/battery/battery-20.svg":
                    naoqi.battery < 0.3 ? "res/battery/battery-30.svg":
                    naoqi.battery < 0.4 ? "res/battery/battery-40.svg":
                    naoqi.battery < 0.5 ? "res/battery/battery-50.svg":
                    naoqi.battery < 0.6 ? "res/battery/battery-60.svg":
                    naoqi.battery < 0.7 ? "res/battery/battery-70.svg":
                    naoqi.battery < 0.8 ? "res/battery/battery-80.svg":
                    naoqi.battery < 0.9 ? "res/battery/battery-90.svg":
                    "res/battery/battery.svg"

         fillMode: Image.PreserveAspectFit
            sourceSize: Qt.size(parent.width, parent.height)
    }

}
