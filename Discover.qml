import QtQuick 2.0
import QtQuick.Controls 2.3

Item {
    id: discovery

    readonly property double meters_to_px: 300 // 1m == 200px
    readonly property point origin: Qt.point(400,parent.height/2)

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
                meters_to_px: discovery.meters_to_px
                radius_m: 1
                anchors.centerIn: parent
            }
            Circle {
                meters_to_px: discovery.meters_to_px
                radius_m: 2
                anchors.centerIn: parent
            }
            Circle {
                meters_to_px: discovery.meters_to_px
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

            onClicked: {
                    naoqi.people.createMockPerson("adult");
            }
        }

        IconButton {
            id: child
            source: "res/baby-face-outline.svg"

            onClicked: {
                    naoqi.people.createMockPerson("child");
            }

        }


        IconButton {
            id: remove
            source: "res/account-off.svg"
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

    signal newPerson(string person, bool robot_tracked, string age)

    Component.onCompleted: {
        naoqi.people.newPerson.connect(discovery.newPerson)
    }

    onNewPerson: {
        var cmpt = Qt.createComponent("PersonIcon.qml");
        var person = cmpt.createObject(robot, {person_id: person, 
                                               robot_tracked: robot_tracked,
                                               age: age,
                                               meters_to_px: meters_to_px
                                              });
        naoqi.people.disappearedPerson.connect(person.disappearedPerson)

    }
    /////////////////////////////////////////////////////////////////////////


}
