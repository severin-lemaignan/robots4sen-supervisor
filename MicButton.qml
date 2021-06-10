
import QtQuick 2.10
import Naoqi 1.0

Item {
    property string name: "other"
    property alias source: record_btn.source

    property var record_modal

    property color bg_color: "white"

    Rectangle {
        anchors.right: record_btn.horizontalCenter
        height: record_btn.height
        anchors.top: record_btn.top
        width:200

        color: parent.bg_color
    }

    IconButton {
        id: record_btn

        height: 100
        noborder: true

        source: "res/microphone.svg"

        AudioRecorder {
            id: audiorecorder
            location: "default.ogg"
        }

        onPressedChanged: {
            if (pressed) {
                var dateTime = new Date().toLocaleString(Qt.locale("en_GB"), "yyyy-MM-dd-HH-mm-ss");
                audiorecorder.location = "./logs/notes/" + name + "-" + dateTime + ".ogg"
                audiorecorder.record();
                record_modal.visible = true;
            }
            else {
                audiorecorder.stop();
                record_modal.visible = false;
            }
        }
    }



}

