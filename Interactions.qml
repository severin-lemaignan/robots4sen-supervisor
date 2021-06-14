import QtQuick 2.0
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.5


Item {
    id: interactions


    Text {
        id: activity_label
        text: "Currently doing: <b>" + (naoqi_supervisor.currentActivity ? naoqi_supervisor.currentActivity : "no activity") + "</b>"
        font.pixelSize: 40
        anchors.left: parent.left
        anchors.leftMargin: 300
        anchors.top: parent.top
        anchors.topMargin: 50
    }

    Text {
        id: interactions_label
        text: "<b>Initiate interaction:<b>"
        font.pixelSize: 40
        anchors.left: parent.left
        anchors.leftMargin: 300
        anchors.top: activity_label.bottom
        anchors.topMargin: 50
    }

    Row {
        id: interactions_row
        spacing: 20
        height: 150
        anchors.left: parent.left
        anchors.leftMargin: 300
        anchors.top: interactions_label.bottom
        anchors.topMargin: 50
 
        IconButton {
            source: "res/account.svg"
            noborder: false
            height: 150
            label: "single"
            onClicked: {
                naoqi_supervisor.start_single_interaction();
            }
        }

        IconButton {
            source: "res/account-multiple.svg"
            noborder: false
            height: 150
            label: "small"
            onClicked: {
                naoqi_supervisor.start_small_group_interaction();
            }
        }

        IconButton {
            source: "res/account-group.svg"
            noborder: false
            height: 150
            label: "large"
            onClicked: {
                naoqi_supervisor.start_large_group_interaction();
            }
        }

        IconButton {
            height: 150

            noborder:true
            source: "res/stop-circle.svg"
            label: "stop"
            onClicked: {
                naoqi_supervisor.interruptCurrentActivity();
            }

        }


    }


    Text {
        id: nb_children_label
        text: "<b># children engaged:</b>"
        font.pixelSize: 40
        anchors.left: parent.left
        anchors.leftMargin: 300
        anchors.top: interactions_row.bottom
        anchors.topMargin: 50
    }

    Row {
        spacing: 20
        anchors.left: parent.left
        anchors.leftMargin: 300
        anchors.top: nb_children_label.bottom
        anchors.topMargin: 50
        height: 150
 
        IconButton {
            source: "res/numeric-0.svg"
            height: 150
            onClicked: {
                naoqi_supervisor.nb_children = 0;
            }

            color: naoqi_supervisor.nb_children == 0 ? "orange": "white"
            borderwidth: naoqi_supervisor.detected_nb_children == 0 ? 8 : 4
        }

        IconButton {
            source: "res/numeric-1.svg"
            height: 150
            onClicked: {
                naoqi_supervisor.nb_children = 1;
            }

            color: naoqi_supervisor.nb_children == 1 ? "green": "white"
            borderwidth: naoqi_supervisor.detected_nb_children == 1 ? 8 : 4
        }

        IconButton {
            source: "res/numeric-2.svg"
            height: 150
            onClicked: {
                naoqi_supervisor.nb_children = 2;
            }
            color: naoqi_supervisor.nb_children == 2 ? "green": "white"
            borderwidth: naoqi_supervisor.detected_nb_children == 2 ? 8 : 4
        }

        IconButton {
            source: "res/numeric-3.svg"
            height: 150
            onClicked: {
                naoqi_supervisor.nb_children = 3;
            }
            color: naoqi_supervisor.nb_children == 3 ? "green": "white"
            borderwidth: naoqi_supervisor.detected_nb_children == 3 ? 8 : 4
        }

        IconButton {
            source: "res/numeric-4.svg"
            height: 150
            onClicked: {
                naoqi_supervisor.nb_children = 4;
            }
            color: naoqi_supervisor.nb_children == 4 ? "green": "white"
            borderwidth: naoqi_supervisor.detected_nb_children == 4 ? 8 : 4
        }

        IconButton {
            source: "res/numeric-5.svg"
            height: 150
            onClicked: {
                naoqi_supervisor.nb_children = 5;
            }
            color: naoqi_supervisor.nb_children == 5 ? "green": "white"
            borderwidth: naoqi_supervisor.detected_nb_children == 5 ? 8 : 4
        }

        IconButton {
            source: "res/numeric-6.svg"
            height: 150
            onClicked: {
                naoqi_supervisor.nb_children = 6;
            }
            color: naoqi_supervisor.nb_children == 6 ? "green": "white"
            borderwidth: naoqi_supervisor.detected_nb_children == 6 ? 8 : 4
        }


    }

}

