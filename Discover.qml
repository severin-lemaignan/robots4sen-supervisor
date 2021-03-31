import QtQuick 2.0
import QtQuick.Controls 2.3

Item {
    id: discovery
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

    Item {
        id: stage
        anchors.fill: parent

    Image {
        id: proxemics
        anchors.fill: parent
        source: "res/pepper-proxemics.svg"
        fillMode: Image.PreserveAspectFit
    }

    Timer {
        interval: 500; running: false; repeat: true
        onTriggered: {
            console.log("People:");
            for(var idx in naoqi.people){
                console.log("Person " + naoqi.people[idx].id + " at " + naoqi.people[idx].x + ", " + naoqi.people[idx].y);

            }
        }
    }



    }


    Component.onCompleted: naoqi.people.onNewPerson.connect(discovery.newPerson)

    signal newPerson(QtObject person)

    onNewPerson: {
            console.log("tiptop: " + person.id + " arrived");
            var component = Qt.createComponent("IconButton.qml");
            //var icon = component.createObject(discovery, {x: Qt.binding(function(){person.x}), y: Qt.binding(function(){person.y}),source: "res/baby-face-outline.svg"});
            var icon = component.createObject(discovery, {source: "res/baby-face-outline.svg"});

            person.x_changed.connect(discovery.valChanged);
            person.x_changed.connect(icon.test);
        }


    signal valChanged(double val)

    onValChanged: {
        console.log("got val: " + val);
    }
}
