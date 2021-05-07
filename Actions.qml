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

            GridView {
                    id:gestures
                    height: parent.height/2
                    anchors.left: parent.left
                    anchors.leftMargin: 50
                    anchors.right: parent.right
                    anchors.rightMargin: 50
                    anchors.top: parent.top
                    model : list_gestures
                    cellHeight: parent.width * 0.2
                    cellWidth: cellHeight

                    delegate: IconButton{
                            height:gestures.cellHeight * 0.8
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

            GridView {
                    id:animations
                    height: parent.height/4
                    anchors.left: parent.left
                    anchors.leftMargin: 50
                    anchors.right: parent.right
                    anchors.rightMargin: 50
                    anchors.top: gestures.bottom
                    anchors.topMargin: 50
                    model : list_animations
                    cellHeight: parent.width * 0.2
                    cellWidth: cellHeight

                    delegate: IconButton{
                            height:gestures.cellHeight * 0.8
                            noborder:true
                            source:image //we use this name in ListModel
                            label: action.split("/")[1]
                            onPressedChanged: {
                                        if (pressed) {
                                            naoqi.request_behaviour(action);
                                        }
                            }

                    }
            }

            GridView {
                    id:activities
                    height: parent.height/4
                    anchors.left: parent.left
                    anchors.leftMargin: 50
                    anchors.right: parent.right
                    anchors.rightMargin: 50
                    anchors.top: animations.bottom
                    anchors.topMargin: 50
                    model : list_activities
                    cellHeight: parent.width * 0.2
                    cellWidth: cellHeight

                    delegate: IconButton{
                            height:gestures.cellHeight * 0.8
                            noborder:true
                            source:image //we use this name in ListModel
                            label: action
                            onPressedChanged: {
                                        if (pressed) {
                                            naoqi.request_activity(action);
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
                            action: "embarrassed"
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


            ListModel {

                    id: list_animations
                    ListElement {
                            action: "robots4sen-brl/elephant"
                            image: "res/robot-angry-outline.svg"
                    }
                    ListElement {
                            action: "robots4sen-brl/saxophone"
                            image: "res/robot-love-outline.svg"
                    }
                    ListElement {
                            action: "robots4sen-brl/dance-taichi"
                            image: "res/robot-love-outline.svg"
                    }
            }

            ListModel {

                    id: list_activities
                    ListElement {
                            action: "stories"
                            image: "res/robot-angry-outline.svg"
                    }
            }


    }

}

/*##^##
Designer {
    D{i:0;autoSize:true;formeditorZoom:0.66;height:1824;width:2736}
}
##^##*/
