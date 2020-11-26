import QtQuick 2.0
import QtQuick.Controls 2.3

Rectangle {
    property var source
    property bool draggable: false
    property bool replicate: false
    property var duplicateOwner

    height: 70
    width: height

    border.width: 4
    radius: height/2


    Image {
        width: 0.8 * parent.width
        height: 0.8 * parent.height
        sourceSize.width: width
        sourceSize.height: height
        anchors.centerIn: parent
        fillMode: Image.PreserveAspectFit
        source: parent.source
    }

    MouseArea {
            id: dragArea
            anchors.fill: parent

            drag.target: draggable ? parent:null
            onPressed: {
                    console.log("Clicked!");
                    if (replicate) duplicateObject(x=mouse.x, y=mouse.y);
            }
    }

    function duplicateObject(x, y) {

        var pos = dragArea.mapToItem(duplicateOwner, x - width/2, y - height/2)
        var component = Qt.createComponent("IconButton.qml");
        var duplicate = component.createObject(duplicateOwner, {source: source,
                                                                draggable: true,
                                                                replicate: false,
                                                                x: pos.x,
                                                                y: pos.y,
                                                                dragActive: true});

        if (duplicate == null) {
            // Error Handling
            console.log("Error creating object");
        }
        else {
            console.log("Copy created!")
        }
    }
}

/*##^##
Designer {
    D{i:1;anchors_height:49;anchors_width:49}
}
##^##*/
