//
//  ViewController.swift
//  TTS
//
//  Created by Jaideep on 11/10/25.
//



import UIKit
import Speech
import AVFoundation
import NaturalLanguage

class ViewController: UIViewController, SFSpeechRecognizerDelegate {
    let audioEngine = AVAudioEngine()
    let speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
    var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    var recognitionTask: SFSpeechRecognitionTask?
    let tagger = NLTagger(tagSchemes: [.nameType])
    var organizationImageView: UIImageView!

    // Vonage media manager
    var vonageManager: VonageMediaManager?
    var videoContainerView: UIView!

    // TODO: Replace these with your actual Vonage credentials
    private let vonageApiKey = "YOUR_API_KEY"
    private let vonageSessionId = "YOUR_SESSION_ID"
    private let vonageToken = "YOUR_TOKEN"
    
    override func viewDidLoad() {
        super.viewDidLoad()
        speechRecognizer?.delegate = self

        // Setup video container view for Vonage
        setupVideoContainerView()

        // Setup organization image view
        setupOrganizationImageView()

        // Initialize Vonage manager
        setupVonageManager()

        // Request permissions before starting
        requestSpeechRecognitionPermission()
    }

    func setupVideoContainerView() {
        videoContainerView = UIView()
        videoContainerView.backgroundColor = .black
        videoContainerView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(videoContainerView)

        // Position video container at the top half of the screen
        NSLayoutConstraint.activate([
            videoContainerView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            videoContainerView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            videoContainerView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            videoContainerView.heightAnchor.constraint(equalTo: view.heightAnchor, multiplier: 0.5)
        ])
    }

    func setupVonageManager() {
        vonageManager = VonageMediaManager(
            apiKey: vonageApiKey,
            sessionId: vonageSessionId,
            token: vonageToken
        )

        // Connect to Vonage session
        vonageManager?.connect { [weak self] success, error in
            if success {
                print("Connected to Vonage session")

                // Start publishing video
                DispatchQueue.main.async {
                    self?.vonageManager?.startPublishing(in: self?.videoContainerView ?? UIView()) { published in
                        if published {
                            print("Started publishing video")
                        } else {
                            print("Failed to start publishing")
                        }
                    }
                }
            } else {
                print("Failed to connect to Vonage session: \(error?.localizedDescription ?? "Unknown error")")
            }
        }
    }

    func setupOrganizationImageView() {
        organizationImageView = UIImageView()
        organizationImageView.contentMode = .scaleAspectFit
        organizationImageView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(organizationImageView)

        // Center the image view in the parent view
        NSLayoutConstraint.activate([
            organizationImageView.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            organizationImageView.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            organizationImageView.widthAnchor.constraint(equalToConstant: 200),
            organizationImageView.heightAnchor.constraint(equalToConstant: 200)
        ])
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

                    // Analyze the transcribed text for organizations
                    self.analyzeTextForOrganizations(caption)
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
    
    func analyzeTextForOrganizations(_ text: String) {
        tagger.string = text

        var organizations: [String] = []

        tagger.enumerateTags(in: text.startIndex..<text.endIndex,
                           unit: .word,
                           scheme: .nameType,
                           options: [.omitWhitespace, .omitPunctuation, .joinNames]) { tag, tokenRange in
            if let tag = tag, tag == .organizationName {
                let organization = String(text[tokenRange])
                organizations.append(organization)
                print("Found organization: \(organization)")
            }
            return true
        }

        // Check for images for each organization found
        for organization in organizations {
            loadOrganizationImage(for: organization)
        }
    }

    func loadOrganizationImage(for organizationName: String) {
        // Format the organization name to match asset naming convention
        // e.g., "Apple" -> "Apple-Org"
        let imageName = "\(organizationName)-Org"

        // Try to load the image from assets
        if let image = UIImage(named: imageName) {
            DispatchQueue.main.async {
                // Display in UIImageView
                self.organizationImageView.image = image
                print("Loaded image: \(imageName)")

                // Apply as video background using Vonage Media Transformer
                self.vonageManager?.applyBackgroundImage(image)
                print("Applied background image to video: \(imageName)")
            }
        } else {
            print("Image not found in assets: \(imageName)")

            // Clear background if no image found
            DispatchQueue.main.async {
                self.organizationImageView.image = nil
                self.vonageManager?.clearBackground()
            }
        }
    }

    func speechRecognizer(_ recognizer: SFSpeechRecognizer, didFinishRecognition recognitionResult: SFSpeechRecognitionResult, error: Error?) {
        // Handle final result if needed
    }
}

