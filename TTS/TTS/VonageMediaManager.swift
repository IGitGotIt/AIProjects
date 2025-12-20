//
//  VonageMediaManager.swift
//  TTS
//
//  Created by Claude Code
//

import Foundation
import OpenTok
import UIKit

/// Manager class that abstracts Vonage/OpenTok API interactions
class VonageMediaManager: NSObject {

    // MARK: - Properties

    private var session: OTSession?
    private var publisher: OTPublisher?
    private var subscriber: OTSubscriber?
    private var backgroundTransformer: BackgroundImageTransformer?

    // Session credentials (replace with your actual credentials)
    private let apiKey: String
    private let sessionId: String
    private let token: String

    // MARK: - Initialization

    init(apiKey: String, sessionId: String, token: String) {
        self.apiKey = apiKey
        self.sessionId = sessionId
        self.token = token
        super.init()
    }

    // MARK: - Session Management

    /// Initialize and connect to Vonage session
    func connect(completion: @escaping (Bool, Error?) -> Void) {
        session = OTSession(apiKey: apiKey, sessionId: sessionId, delegate: self)

        var error: OTError?
        session?.connect(withToken: token, error: &error)

        if let error = error {
            completion(false, error)
        }
    }

    /// Disconnect from the session
    func disconnect() {
        session?.disconnect(nil)
    }

    // MARK: - Publisher Management

    /// Create and publish video stream
    func startPublishing(in view: UIView, completion: @escaping (Bool) -> Void) {
        let settings = OTPublisherSettings()
        settings.name = UIDevice.current.name

        guard let publisher = OTPublisher(delegate: self, settings: settings) else {
            completion(false)
            return
        }

        self.publisher = publisher

        var error: OTError?
        session?.publish(publisher, error: &error)

        if let error = error {
            print("Failed to publish: \(error.localizedDescription)")
            completion(false)
            return
        }

        // Add publisher view to the provided view
        if let publisherView = publisher.view {
            publisherView.frame = view.bounds
            publisherView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
            view.addSubview(publisherView)
        }

        completion(true)
    }

    /// Stop publishing
    func stopPublishing() {
        if let publisher = publisher {
            session?.unpublish(publisher, error: nil)
            publisher.view?.removeFromSuperview()
            self.publisher = nil
        }
    }

    // MARK: - Video Transformer Management

    /// Apply background image transformer to the published video
    func applyBackgroundImage(_ image: UIImage) {
        guard let publisher = publisher else {
            print("Publisher not initialized")
            return
        }

        // Remove existing transformer if any
        if let existingTransformer = backgroundTransformer {
            publisher.videoTransformers.remove(existingTransformer)
        }

        // Create and add new transformer
        backgroundTransformer = BackgroundImageTransformer(backgroundImage: image)
        publisher.videoTransformers.append(backgroundTransformer!)

        print("Background image transformer applied")
    }

    /// Remove background image transformer
    func removeBackgroundTransformer() {
        guard let publisher = publisher,
              let transformer = backgroundTransformer else {
            return
        }

        publisher.videoTransformers.remove(transformer)
        backgroundTransformer = nil

        print("Background image transformer removed")
    }

    /// Clear/reset background to show original video
    func clearBackground() {
        removeBackgroundTransformer()
    }
}

// MARK: - OTSessionDelegate

extension VonageMediaManager: OTSessionDelegate {

    func sessionDidConnect(_ session: OTSession) {
        print("Session connected")
    }

    func sessionDidDisconnect(_ session: OTSession) {
        print("Session disconnected")
    }

    func session(_ session: OTSession, didFailWithError error: OTError) {
        print("Session failed: \(error.localizedDescription)")
    }

    func session(_ session: OTSession, streamCreated stream: OTStream) {
        print("Stream created")

        // Subscribe to stream if needed
        subscriber = OTSubscriber(stream: stream, delegate: self)

        var error: OTError?
        session.subscribe(subscriber!, error: &error)

        if let error = error {
            print("Failed to subscribe: \(error.localizedDescription)")
        }
    }

    func session(_ session: OTSession, streamDestroyed stream: OTStream) {
        print("Stream destroyed")
    }
}

// MARK: - OTPublisherDelegate

extension VonageMediaManager: OTPublisherDelegate {

    func publisher(_ publisher: OTPublisherKit, didFailWithError error: OTError) {
        print("Publisher failed: \(error.localizedDescription)")
    }

    func publisher(_ publisher: OTPublisherKit, streamCreated stream: OTStream) {
        print("Publisher stream created")
    }

    func publisher(_ publisher: OTPublisherKit, streamDestroyed stream: OTStream) {
        print("Publisher stream destroyed")
    }
}

// MARK: - OTSubscriberDelegate

extension VonageMediaManager: OTSubscriberDelegate {

    func subscriber(_ subscriber: OTSubscriberKit, didFailWithError error: OTError) {
        print("Subscriber failed: \(error.localizedDescription)")
    }
}
