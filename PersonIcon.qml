import QtQuick 2.0
import QtQuick.Controls 2.3

import Naoqi 1.0

Item {

    property double meters_to_px: 100 // 1m == 100px

    property bool robot_tracked: true // if true, the person's position is tracked by the robot; if false, manually tracked on the tablet
    property bool is_tracked: false
    property bool is_lost: person.state == "lost"
    property bool is_seen: !(person.state in ["lost", "disappearing"])

    property alias person_id: person.person_id

    property alias age: person.age

    Person {
        id: person

        // person.x and person.y are in real-world meters. Need conversion.

        Component.onCompleted: {
            console.log("New person added: " + person_id);
        }
    }

    IconButton {
        id: icon

        // if robot_tracked, then *bind* x to person.x; otherwise, simply initially
        // set x to person.x, but do not bind it so that we can instead update x 
        // and y by dragging on the screen.
        Component.onCompleted : {
            if (robot_tracked) {
                console.log("Person <" + person.person_id + ">automatically tracked by the robot");
                x = Qt.binding(function() {return person.x * meters_to_px;});
                y = Qt.binding(function() {return -person.y * meters_to_px;});
            }
            else {
                x = person.x * meters_to_px;
                y = -person.y * meters_to_px;
            }
        }

        color: person.state == "engaged" ? "green" : (person.state == "disengaging" ? "orange" : "transparent")
        height: 0.3 * meters_to_px
        noborder: !is_tracked
        border.color: "red"

        draggable: !robot_tracked

        label: person.state + " (" + person.x.toFixed(2) + ", " + person.y.toFixed(2) + ")"

        Behavior on x { PropertyAnimation {} }
        Behavior on y { PropertyAnimation {} }

        opacity: is_lost ? 0 : 1
        Behavior on opacity { PropertyAnimation { duration: 5000} }

        source: is_seen ? (age == "child" ? "res/baby-face-outline.svg" : (age == "adult" ? "res/account.svg" : "res/account-unsure.svg")) : "res/account-unsure.svg"

        Rectangle {
            id: indicator
            anchors.left: parent.left
            anchors.top: parent.top

            width: 12
            height: width
            radius: width/2

            color: ["unknown","seen"].indexOf(person.state) == -1  ? 'green' : 'orange'
        }

        onClicked: {
            if (is_tracked) {
                naoqi.request_track(""); // cancel tracking
            }
            else {
                naoqi.request_track(person.id);
            }
        }

        onPressAndHold: {
            console.log("User " + person.person_id + " deleted");
            person.delete()
        }

        onXChanged: {
            if (!robot_tracked) {
                person.setlocation([x/meters_to_px,-y/meters_to_px,0]);
            }
        }
        onYChanged: {
            if (!robot_tracked) {
                person.setlocation([x/meters_to_px,-y/meters_to_px,0]);
            }
        }

    }


}
