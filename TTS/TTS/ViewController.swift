//
//  ViewController.swift
//  TTS
//
//  Created by Jaideep on 11/10/25.
//



import UIKit
import Speech
import AVFoundation

class ViewController: UIViewController, SFSpeechRecognizerDelegate {
    let audioEngine = AVAudioEngine()
    let speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
    var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    var recognitionTask: SFSpeechRecognitionTask?
    
    override func viewDidLoad() {
        super.viewDidLoad()
        speechRecognizer?.delegate = self
        
        // Request permissions before starting
        requestSpeechRecognitionPermission()
    }
    
    func requestSpeechRecognitionPermission() {
        SFSpeechRecognizer.requestAuthorization { authStatus in
            DispatchQueue.main.async {
                switch authStatus {
                case .authorized:
                    self.startCaptionsAutomatically()
                case .denied, .restricted, .notDetermined:
                    print("Speech recognition not authorized")
                @unknown default:
                    print("Unknown authorization status")
                }
            }
        }
    }
    
    func startCaptionsAutomatically() {
        try? startRecording()
    }
    
    @IBAction func startCaptions(_ sender: UIButton?) {
        try? startRecording() // Call this on button tap
    }
    
    func startRecording() throws {
        // Cancel any existing task
        recognitionTask?.cancel()
        recognitionTask = nil
        
        // Configure audio session
        let audioSession = AVAudioSession.sharedInstance()
        try audioSession.setCategory(.record, mode: .measurement, options: .duckOthers)
        try audioSession.setActive(true, options: .notifyOthersOnDeactivation)
        
        // Create a new recognition request
        recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
        guard let recognitionRequest = recognitionRequest else {
            throw NSError(domain: "SpeechRecognition", code: 1, userInfo: [NSLocalizedDescriptionKey: "Unable to create recognition request"])
        }
        
        recognitionRequest.shouldReportPartialResults = true
        
        // Configure audio engine
        let inputNode = audioEngine.inputNode
        
        // Remove any existing tap first
        inputNode.removeTap(onBus: 0)
        
        // Get the native format of the input node
        let recordingFormat = inputNode.outputFormat(forBus: 0)
        
        // Ensure the format is valid
        guard recordingFormat.sampleRate > 0 && recordingFormat.channelCount > 0 else {
            throw NSError(domain: "AudioFormat", code: 2, userInfo: [NSLocalizedDescriptionKey: "Invalid audio format"])
        }
        
        // Install tap on the input node
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, _ in
            recognitionRequest.append(buffer)
        }
        
        // Prepare and start the audio engine
        audioEngine.prepare()
        try audioEngine.start()
        
        // Start the recognition task
        recognitionTask = speechRecognizer?.recognitionTask(with: recognitionRequest) { result, error in
            if let result = result {
                let caption = result.bestTranscription.formattedString
                DispatchQueue.main.async {
                    print("Caption: \(caption)") // Update UI label here
                }
            }
            
            if error != nil || result?.isFinal == true {
                self.audioEngine.stop()
                inputNode.removeTap(onBus: 0)
                self.recognitionRequest = nil
                self.recognitionTask = nil
                
                // Optionally restart if this was just a final result
                if result?.isFinal == true && error == nil {
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                        try? self.startRecording()
                    }
                }
            }
        }
    }
    
    func speechRecognizer(_ recognizer: SFSpeechRecognizer, didFinishRecognition recognitionResult: SFSpeechRecognitionResult, error: Error?) {
        // Handle final result if needed
    }
}

