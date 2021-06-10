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
                    onClicked: {
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
                    id: currentActivity
                    height: parent.height/4
                    anchors.left: parent.left
                    anchors.leftMargin: 50
                    anchors.right: parent.right
                    anchors.rightMargin: 50
                    anchors.top: parent.top

                    Text {
                        id: activity_label
                        text: "Currently doing:\n" + (naoqi_supervisor.currentActivity ? naoqi_supervisor.currentActivity : "no activity")
                        font.pixelSize: 15/70 * parent.height
                        anchors.left: parent.left
                        anchors.leftMargin: 20
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    IconButton {
                            anchors.left: activity_label.right
                            anchors.leftMargin: 50
                            anchors.verticalCenter: parent.verticalCenter

                            height: 100

                            noborder:true
                            source: "res/stop-circle.svg"
                            label: "interrupt"
                            visible: naoqi_supervisor.currentActivity ? true : false

                            onClicked: {
                                            naoqi_supervisor.interruptCurrentActivity();
                            }

                    }


            }
    
            Text {
                id: social_gestures_label
                text: "Perform social gestures:"
                font.pixelSize: 30
                    anchors.left: parent.left
                    anchors.leftMargin: 50
                    anchors.right: parent.right
                    anchors.rightMargin: 50
                    anchors.top: currentActivity.bottom
            }

            GridView {
                    id:gestures
                    height: parent.height/4
                    anchors.left: parent.left
                    anchors.leftMargin: 50
                    anchors.right: parent.right
                    anchors.rightMargin: 50
                    anchors.top: social_gestures_label.bottom
                    anchors.topMargin: 20
                    model : list_gestures
                    cellHeight: parent.width * 0.12
                    cellWidth: cellHeight

                    delegate: IconButton{
                            height:gestures.cellHeight * 0.8
                            noborder:true
                            source:image //we use this name in ListModel
                            label: action
                            onClicked: {
                                            naoqi.request_animate(action);
                            }

                    }
            }

            Text {
                id: activities_label
                text: "Start activity:"
                font.pixelSize: 30
                    anchors.left: parent.left
                    anchors.leftMargin: 50
                    anchors.right: parent.right
                    anchors.rightMargin: 50
                    anchors.top: gestures.bottom
                    anchors.topMargin: 100
            }

            GridView {
                    id:animations
                    height: parent.height/4
                    anchors.left: parent.left
                    anchors.leftMargin: 50
                    anchors.right: parent.right
                    anchors.rightMargin: 50
                    anchors.top: activities_label.bottom
                    anchors.topMargin: 50
                    model : list_activities
                    cellHeight: parent.width * 0.12
                    cellWidth: cellHeight

                    delegate: IconButton{
                            height:gestures.cellHeight * 0.8
                            noborder:true
                            source:image //we use this name in ListModel
                            label: action
                            onClicked: {
                                            naoqi.request_activity(action);
                            }

                    }
            }

            ListModel {

                    id: list_gestures
                    ListElement {
                            action: "hello"
                            image: "res/hello.svg"
                    }
                    ListElement {
                            action: "happy"
                            image: "res/happy.svg"
                    }
                    ListElement {
                            action: "calm"
                            image: "res/calm.svg"
                    }
                    ListElement {
                            action: "unknown"
                            image: "res/unknown.svg"
                    }
                    ListElement {
                            action: "explain"
                            image: "res/explain.svg"
                    }
                    ListElement {
                            action: "bored"
                            image: "res/bored.svg"
                    }
                    ListElement {
                            action: "disappointed"
                            image: "res/disappointed.svg"
                    }
                    ListElement {
                            action: "embarrassed"
                            image: "res/embarrassed.svg"
                    }
            }

            ListModel {

                    id: list_activities
                    ListElement {
                            action: "calm dances"
                            image: "res/activities/calm_dance.svg"
                    }
                    ListElement {
                            action: "cuddle"
                            image: "res/activities/cuddle.svg"
                    }
                    ListElement {
                            action: "jokes"
                            image: "res/activities/joke.svg"
                    }
                    ListElement {
                            action: "calm music"
                            image: "res/activities/music.svg"
                    }
                    ListElement {
                            action: "relaxing sounds"
                            image: "res/activities/relax.svg"
                    }
                    ListElement {
                            action: "listening"
                            image: "res/activities/speak.svg"
                    }
                    ListElement {
                            action: "story"
                            image: "res/activities/story.svg"
                    }
            }


    }

}

/*##^##
Designer {
    D{i:0;autoSize:true;formeditorZoom:0.66;height:1824;width:2736}
}
##^##*/
