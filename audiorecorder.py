# This Python file uses the following encoding: utf-8

from PySide2.QtCore import QUrl, Slot, Signal, QObject, Property, QTimer
from PySide2.QtMultimedia import QMultimedia, QAudioRecorder, QAudioEncoderSettings,QVideoEncoderSettings

# Code partially based on: https://stackoverflow.com/a/64300056

class AudioRecorder(QObject):

    def __init__(self):
        QObject.__init__(self)

        #import PySide2
        #print(PySide2.__version__)

        self.recorder = QAudioRecorder()

        selected_audio_input = self.recorder.audioInput()

        #print("Audio Inputs:")
        #for i, audio_input in enumerate(self.recorder.audioInputs()):
        #    print("%s. %s" % (i, audio_input))
        #
        #print("selected input: " + str(selected_audio_input))

        self.recorder.setAudioInput(selected_audio_input)

        settings = QAudioEncoderSettings()

        selected_codec = "audio/x-opus"
        #print("Codecs:")
        #for i, codec in enumerate(self.recorder.supportedAudioCodecs()):

        #    print("%s. %s" % (i, codec))

        #print("selected codec: " + str(selected_codec))
        settings.setCodec(selected_codec)

        #selected_sample_rate = 0
        #print("Sample rates:")
        #sample_rates, continuous = self.recorder.supportedAudioSampleRates()
        #for i, sample_rate in enumerate(sample_rates):
        #    print("%s. %s" % (i, sample_rate))
        #settings.setSampleRate(selected_sample_rate)

        #bit_rate = 0  # other values: 32000, 64000,96000, 128000
        #settings.setBitRate(bit_rate)

        channels = -1  # other values: 1, 2, 4
        settings.setChannelCount(channels)
        settings.setQuality(QMultimedia.NormalQuality)
        settings.setEncodingMode(QMultimedia.ConstantBitRateEncoding)

        selected_container = "audio/ogg"
        #print("Containers")
        #for i, container in enumerate(self.recorder.supportedContainers()):
        #    print("%s. %s" % (i, container))

        self.recorder.setEncodingSettings(
            settings, QVideoEncoderSettings(), selected_container
        )

        filename = "test.mp3"
        self.recorder.setOutputLocation(QUrl.fromLocalFile(filename))


    @Slot()
    def record(self):
        self.recorder.record()

    @Slot()
    def stop(self):
        self.recorder.stop()

