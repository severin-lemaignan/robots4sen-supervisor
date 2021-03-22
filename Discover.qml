import QtQuick 2.0
import QtQuick.Controls 2.3

Item {
    id: discovery
    Row {
        id: menu
        anchors.rightMargin: 10
        anchors.topMargin: 10
        anchors.top: parent.top

        anchors.right: parent.right
        spacing: 9

        IconButton {
            id: adult
            source: "res/account.svg"
            replicate: true
            duplicateOwner: stage
        }

        IconButton {
            id: child
            source: "res/baby-face-outline.svg"
            replicate: true
            duplicateOwner: stage
        }


        IconButton {
            id: remove
            source: "res/account-off.svg"
             replicate: true
            duplicateOwner: stage
       }
    }

    Item {
        id: stage
        anchors.fill: parent

    Image {
        id: proxemics
        anchors.fill: parent
        source: "res/pepper-proxemics.svg"
        fillMode: Image.PreserveAspectFit
    }
    }


}
