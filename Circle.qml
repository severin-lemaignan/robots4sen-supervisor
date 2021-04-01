import QtQuick 2.0
import QtQuick.Controls 2.3

Rectangle {
    property double meters_to_px: 100
    property double radius_m: 1

    width: 2 * radius_m * meters_to_px
    height: width
    radius: width/2
    border.width: 3
    border.color: "#66000000"
    color: "transparent"

    Text {
        text: radius_m + "m"
        color: parent.border.color
        font.pointSize: 10
        anchors.right: parent.right
        anchors.rightMargin: 5
        anchors.verticalCenter: parent.verticalCenter
    }
}

