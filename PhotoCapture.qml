import QtQuick 2.0
import QtMultimedia 5.4

Rectangle {
    id : cameraUI


    color: "black"

    Camera {
            id: camera
            captureMode: Camera.CaptureStillImage

            imageCapture {
                    onImageCaptured: {
                        captureLabel.opacity = 1;
                        hideLabel.running = true;
                    }
            }

    }
    VideoOutput {
            id: viewfinder
            visible: true

            anchors.centerIn: parent
            width: parent.width - 50
            height: parent.height - 50

            source: camera
            autoOrientation: true

            Text {
                    id: captureLabel
                    color: "#60b414"
                    text: qsTr("Image captured")
                    font.bold: true
                    font.family: "Verdana"
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.horizontalCenter: parent.horizontalCenter
                    font.pixelSize: 36

                    opacity: 0

                    NumberAnimation on opacity {
                            id: hideLabel
                            to: 0.
                            duration: 2000
                    }

            }
    }

    Rectangle {
            id: shutter
            width: height
            height: 85
            border.color: "#fb4444"
            border.width: 4
            opacity: 0.7
            color:  "black"
            radius: height/2
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 20

            MouseArea {
                    id: mouseArea
                    anchors.fill: parent
                    onClicked: {
                            camera.imageCapture.capture();
                    }
            }
    Rectangle {
            width: height
            height: 60
            color: "#fb4444"
            radius: height/2
            anchors.centerIn: parent

    }
    }

}

/*##^##
Designer {
    D{i:0;autoSize:true;height:480;width:640}
}
##^##*/
