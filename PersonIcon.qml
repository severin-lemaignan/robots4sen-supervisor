import QtQuick 2.0
import QtQuick.Controls 2.3
import Naoqi 1.0

Item {

    property double meters_to_px: 100 // 1m == 100px

    property alias person_id: person.person_id

    Person {
        id: person

        // person.x and person.y are in real-world meters. Need conversion.

        Component.onCompleted: {
            console.log("New person added: " + person_id);
        }
    }

    IconButton {

        x: person.x * meters_to_px
        y: -person.y * meters_to_px

        height: 0.3 * meters_to_px
        noborder: true

        label: "(" + person.x.toFixed(2) + ", " + person.y.toFixed(2) + ")"

        Behavior on x { PropertyAnimation {} }
        Behavior on y { PropertyAnimation {} }
        
        source: "res/baby-face-outline.svg"
    }

    signal disappearedPerson(string person_id)

    onDisappearedPerson: {
        if (person_id == person.person_id) {
            console.log("I, Person " + person_id + ", have disappeared!");
            opacity = 0.5;
        }
    }

}
