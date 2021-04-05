import QtQuick 2.0
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.5

Item {

    Item {
            id: directions
            anchors.left: parent.left
            width: parent.width * 0.45
            height: parent.height

            IconButton {
                    id: pepper
                    source: "res/pepper-top.svg"
                    rotation: -90
                    anchors.centerIn: parent
                    noborder: true
                    height: parent.width * 0.25
                    onPressedChanged: {
                            naoqi.move("STOP", true);
                    }
            }

            IconButton {
                    id: btn_down
                    source: "res/down.svg"
                    height: parent.width * 0.25
                    anchors.top: pepper.bottom
                    anchors.topMargin: 20
                    anchors.horizontalCenter: pepper.horizontalCenter
                    onPressedChanged: {
                            naoqi.move("BACKWARDS", pressed);
                    }
            }
            IconButton {
                    id: btn_left
                    source: "res/left.svg"
                    height: parent.width * 0.25
                    anchors.right: pepper.left
                    anchors.rightMargin: 20
                    anchors.verticalCenter: pepper.verticalCenter

                    onPressedChanged: {
                            naoqi.move("LEFT", pressed)
                    }
            }
            IconButton {
                    id: btn_right
                    source: "res/right.svg"
                    height: parent.width * 0.25
                    anchors.left: pepper.right
                    anchors.leftMargin: 20
                    anchors.verticalCenter: pepper.verticalCenter

                    onPressedChanged: {
                            naoqi.move("RIGHT", pressed)
                    }
            }
            IconButton {
                    id: btn_up
                    source: "res/up.svg"
                    height: parent.width * 0.25
                    anchors.bottom: pepper.top
                    anchors.bottomMargin: 20
                    anchors.horizontalCenter: pepper.horizontalCenter

                    onPressedChanged: {
                            naoqi.move("FORWARDS", pressed);
                    }
            }
            IconButton {
                    id: btn_turn_left
                    source: "res/turn-left.svg"
                    height: parent.width * 0.25
                    anchors.bottom: btn_right.top
                    anchors.bottomMargin: 15
                    anchors.horizontalCenter: btn_right.horizontalCenter

                    onPressedChanged: {
                            naoqi.move("TURN_LEFT", pressed)
                    }
            }
            IconButton {
                    id: btn_turn_right
                    source: "res/turn-right.svg"
                    height: parent.width * 0.25
                    anchors.bottom: btn_left.top
                    anchors.bottomMargin: 15
                    anchors.horizontalCenter: btn_left.horizontalCenter

                    onPressedChanged: {
                            naoqi.move("TURN_RIGHT", pressed)
                    }
            }
    }
    Rectangle {
            id: separator
            anchors.left: directions.right
            height: parent.height
            width:5
            color: "#666"
    }

    Item {
            id: other_actions
            anchors.left: separator.right
            anchors.right: parent.right
            height: parent.height
            Item {
                       visible:false
                    id: expressions
                    height: 86
                    anchors.left: parent.left
                    anchors.right: parent.right

                    Text {
                            id: label_expression
                            text: qsTr("Expressions")
                            anchors.leftMargin: 10
                            anchors.left: parent.left
                            anchors.top: parent.top
                            font.pixelSize: parent.width * 0.05
                    }

                    Item {
                            height: 81
                            anchors.top: label_expression.bottom
                            anchors.topMargin: 10
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.leftMargin: 10
                            anchors.rightMargin: 10



                            IconButton {
                                    id: btn_expr_neutral
                                    source: "res/robot-outline.svg"
                                    anchors.left: parent.left
                                    anchors.leftMargin: 10

                                    height: parent.width * 0.15
                                    Layout.fillWidth: true
                                    onPressedChanged: {
                                            console.log("Neutral")
                                    }
                                    noborder:true
                            }
                            IconButton {
                                    id: btn_expr_excited
                                    source: "res/robot-excited-outline.svg"
                                    anchors.left: btn_expr_neutral.right
                                    anchors.leftMargin: 10

                                    height: parent.width * 0.15
                                    noborder:true
                                    onPressedChanged: {
                                            console.log("Excited")
                                    }
                            }
                            IconButton {
                                    id: btn_expr_love
                                    source: "res/robot-love-outline.svg"
                                    anchors.left: btn_expr_excited.right
                                    anchors.leftMargin: 10
                                    height: parent.width * 0.15
                                    noborder:true
                                    onPressedChanged: {
                                            console.log("Love")
                                    }
                            }
                            IconButton {
                                    id: btn_expr_angry
                                    source: "res/robot-angry-outline.svg"
                                    anchors.left: btn_expr_love.right
                                    anchors.leftMargin: 10
                                    height: parent.width * 0.15
                                    noborder:true
                                    onPressedChanged: {
                                            console.log("Angry")
                                    }
                            }

                    }
            }
            Item {
                    id: gestures
                    height: 88
                    anchors.top: expressions.bottom
                    anchors.topMargin: 10
                    anchors.left: parent.left
                    anchors.right: parent.right

                    Text {
                            id: label_gestures
                            text: qsTr("Social gestures")
                            anchors.leftMargin: 10
                            anchors.left: parent.left
                            anchors.top: parent.top
                            font.pixelSize: parent.width * 0.05
                    }
                    ListView{
                            id:slider
                            height: 70
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.top: label_gestures.bottom
                            spacing: 10
                            orientation: ListView.Horizontal
                            boundsBehavior: Flickable.StopAtBounds
                            flickableDirection: Flickable.HorizontalFlick
                            clip:true//setting it make item outside of view invisible
                            model : list_gestures
                            delegate: IconButton{
                                    noborder:true
                                    source:image //we use this name in ListModel
                                    label: action
                                    onPressedChanged: {
                                                if (pressed) {
                                                    naoqi.request_animate(action);
                                                }
                                    }

                            }
                    }
                    ListModel {

                            id: list_gestures
                            ListElement {
                                    action: "unknown"
                                    image: "res/robot-angry-outline.svg"
                            }
                            ListElement {
                                    action: "hello"
                                    image: "res/robot-love-outline.svg"
                            }
                            ListElement {
                                    action: "calm"
                                    image: "res/robot-angry-outline.svg"
                            }
                            ListElement {
                                    action: "bored"
                                    image: "res/robot-love-outline.svg"
                            }
                            ListElement {
                                    action: "disappointed"
                                    image: "res/robot-angry-outline.svg"
                            }
                            ListElement {
                                    action: "embarassed"
                                    image: "res/robot-love-outline.svg"
                            }
                            ListElement {
                                    action: "happy"
                                    image: "res/robot-angry-outline.svg"
                            }
                            ListElement {
                                    action: "explain"
                                    image: "res/robot-love-outline.svg"
                            }
                    }

            }

            Item {
                    id: activities
                    anchors.top: gestures.bottom
                    anchors.topMargin: 10
                    anchors.left: parent.left
                    anchors.right: parent.right

                    Text {
                            id: label_activities
                            text: qsTr("Activities")
                            anchors.leftMargin: 10
                            anchors.left: parent.left
                            anchors.top: parent.top
                            font.pixelSize: parent.width * 0.05
                    }
                    ListView{
                            id:list_view_activities
                            height: 70
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.top: label_activities.bottom
                            spacing: 10
                            orientation: ListView.Horizontal
                            boundsBehavior: Flickable.StopAtBounds
                            flickableDirection: Flickable.HorizontalFlick
                            clip:true//setting it make item outside of view invisible
                            model : list_activities
                            delegate: IconButton{
                                    noborder:true
                                    source:image //we use this name in ListModel
                                    onPressedChanged: {
                                            console.log("Hello");
                                    }
                            }
                    }
                    ListModel {

                            id: list_activities
                            ListElement {
                                    image: "res/robot-angry-outline.svg"
                            }
                            ListElement {
                                    image: "res/robot-love-outline.svg"
                            }
                            ListElement {
                                    image: "res/robot-angry-outline.svg"
                            }
                            ListElement {
                                    image: "res/robot-love-outline.svg"
                            }
                            ListElement {
                                    image: "res/robot-angry-outline.svg"
                            }
                            ListElement {
                                    image: "res/robot-love-outline.svg"
                            }
                            ListElement {
                                    image: "res/robot-angry-outline.svg"
                            }
                            ListElement {
                                    image: "res/robot-love-outline.svg"
                            }
                    }

            }

    }

}

/*##^##
Designer {
    D{i:0;autoSize:true;height:480;width:640}
}
##^##*/
