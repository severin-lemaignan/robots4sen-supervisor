import QtQuick 2.0
import QtQuick.Controls 2.3

import Naoqi 1.0

Item {

    property double meters_to_px: 100 // 1m == 100px

    property bool is_tracked: false
    property bool is_seen: true

    property alias person_id: person.person_id

    Person {
        id: person

        // person.x and person.y are in real-world meters. Need conversion.

        Component.onCompleted: {
            console.log("New person added: " + person_id);
        }
    }

    IconButton {
        id: icon

        x: person.x * meters_to_px
        y: -person.y * meters_to_px

        height: 0.3 * meters_to_px
        noborder: !is_tracked
        border.color: "red"

        label: "(" + person.x.toFixed(2) + ", " + person.y.toFixed(2) + ")"

        Behavior on x { PropertyAnimation {} }
        Behavior on y { PropertyAnimation {} }

        opacity: is_seen ? 1 : 0
        Behavior on opacity { PropertyAnimation { duration: 5000} }

        source: person.age == "child" ? "res/baby-face-outline.svg" : (person.age == "adult" ? "res/account.svg" : "res/account-unsure.svg")

        Rectangle {
            id: indicator
            anchors.left: parent.left
            anchors.top: parent.top

            width: 12
            height: width
            radius: width/2

            color: person.known ? 'green' : 'orange'
        }

        onPressedChanged: {
            if (is_tracked) {
                naoqi.request_track(""); // cancel tracking
            }
            else {
                naoqi.request_track(person.id);
            }
        }


    }


    signal disappearedPerson(string person_id)

    onDisappearedPerson: {
        if (person_id == person.person_id) {
            console.log("I, Person " + person_id + ", have disappeared!");
            is_seen = false;
        }
    }

}
