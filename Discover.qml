import QtQuick 2.0
import QtQuick.Controls 2.3

Item {
    id: discovery

    readonly property double meters_to_px: 100 // 1m == 100px
    readonly property point origin: Qt.point(200,200)

    Item {
        id: stage
        anchors.fill: parent


        Rectangle {
            id: robot
            x: origin.x
            y: origin.y
            width: 10
            height: width
            radius: width/2
            color: "red"

            Circle {
                meters_to_px: meters_to_px
                radius_m: 1
                anchors.centerIn: parent
            }
            Circle {
                meters_to_px: meters_to_px
                radius_m: 2
                anchors.centerIn: parent
            }
            Circle {
                meters_to_px: meters_to_px
                radius_m: 4
                anchors.centerIn: parent
            }




            Image {
                id: proxemics
                anchors.centerIn: parent
                width: 0.4 * meters_to_px
                source: "res/pepper-top.svg"
                fillMode: Image.PreserveAspectFit
            }
        }
    }

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

    //        Image {
    //            id: proxemics
    //            anchors.fill: parent
    //            source: "res/pepper-proxemics.svg"
    //            fillMode: Image.PreserveAspectFit
    //        }
    //    }


    /////////////////////////////////////////////////////////////////////////
    // connection with the naoqi.people object to create a new 'person' when
    // detected

    signal newPerson(string person)

    Component.onCompleted: {
        naoqi.people.newPerson.connect(discovery.newPerson)
    }

    onNewPerson: {
        var cmpt = Qt.createComponent("PersonIcon.qml");
        var person = cmpt.createObject(robot, {person_id: person, 
                                               meters_to_px: meters_to_px
                                              });
        naoqi.people.disappearedPerson.connect(person.disappearedPerson)

    }
    /////////////////////////////////////////////////////////////////////////


}
