import QtQuick 2.0
import QtQuick.Controls 2.3
import Naoqi 1.0

Item {

    property alias person_id: person.person_id

    Person {
        id: person

        Component.onCompleted: {
            console.log("New person added: " + person_id);
        }
    }

    IconButton {

        x: person.x
        y: person.y

        Behavior on x { PropertyAnimation {} }
        Behavior on y { PropertyAnimation {} }
        
        source: "res/baby-face-outline.svg"
    }

}
