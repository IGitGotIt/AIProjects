//
//  ViewController.swift
//  ImageClassifier
//
//  Created by Jaideep on 11/10/25.
//


import UIKit
import AVFoundation
import Vision
import CoreML

class ViewController: UIViewController, AVCaptureVideoDataOutputSampleBufferDelegate {
    let session = AVCaptureSession()
    let model: VNCoreMLModel
    let videoOutput = AVCaptureVideoDataOutput()
    
    override init(nibName nibNameOrNil: String?, bundle nibBundleOrNil: Bundle?) {
        let config = MLModelConfiguration()
        let inception = try! Inceptionv3(configuration: config)
        model = try! VNCoreMLModel(for: inception.model)
        super.init(nibName: nibNameOrNil, bundle: nibBundleOrNil)
    }
    
    required init?(coder: NSCoder) {
        let config = MLModelConfiguration()
        let inception = try! Inceptionv3(configuration: config)
        model = try! VNCoreMLModel(for: inception.model)
        super.init(coder: coder)
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupCamera()
    }
    
    func setupCamera() {
        guard let device = AVCaptureDevice.default(for: .video) else { return }
        guard let input = try? AVCaptureDeviceInput(device: device) else { return }
        
        session.addInput(input)
        videoOutput.setSampleBufferDelegate(self, queue: DispatchQueue(label: "videoQueue"))
        session.addOutput(videoOutput)
        session.startRunning()
    }
    
    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        let request = VNCoreMLRequest(model: model) { request, error in
            guard let results = request.results as? [VNClassificationObservation],
                  let top = results.first else { return }
            let desc = "Detected: \(top.identifier) (\(String(format: "%.2f", top.confidence * 100))%)"
            print(desc) // Or update UI/accessibility
            UIAccessibility.post(notification: .announcement, argument: desc) // Accessibility metadata
        }
        try? VNImageRequestHandler(cvPixelBuffer: pixelBuffer).perform([request])
    }
}


