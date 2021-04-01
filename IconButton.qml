import QtQuick 2.0
import QtQuick.Controls 2.3

Rectangle {
    id: icon_button

    property var source
    property bool draggable: false
    property bool replicate: false
    property bool disabled: false
    property bool noborder: false
    property var duplicateOwner
    property string label: ""

    property alias pressed: dragArea.pressed

    height: 70
    width: height

    border.width: noborder ? 0 : 4
    radius: height/2

    Image {
        id: icon
        width: parent.width * (noborder ? 1 : 0.8)
        height: width
        sourceSize.width: width
        sourceSize.height: height
        anchors.centerIn: parent
        fillMode: Image.PreserveAspectFit
        source: parent.source
    }

    Text {
        id: icon_label
        text: parent.label
        styleColor: "#ffffff"
        style: Text.Outline
        font.pixelSize: 20/70 * parent.height
        anchors.bottom: icon.bottom
        anchors.bottomMargin: 0
        anchors.horizontalCenter: icon.horizontalCenter
    }

    MouseArea {
            id: dragArea

            enabled: !icon_button.disabled
            anchors.fill: parent

            drag.target: draggable ? parent:null
            onPressed: {
                    //console.log("Clicked!");
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
