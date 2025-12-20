//
//  BackgroundImageTransformer.swift
//  TTS
//
//  Custom video transformer for background image replacement
//

import Foundation
import OpenTok
import UIKit
import CoreImage
import CoreVideo

/// Custom video transformer that replaces the background with an organization logo/image
class BackgroundImageTransformer: NSObject, OTCustomVideoTransformer {

    // MARK: - Properties

    private var backgroundImage: UIImage
    private var ciContext: CIContext
    private var backgroundCIImage: CIImage?

    // MARK: - Initialization

    init(backgroundImage: UIImage) {
        self.backgroundImage = backgroundImage
        self.ciContext = CIContext()

        // Convert UIImage to CIImage for processing
        if let cgImage = backgroundImage.cgImage {
            self.backgroundCIImage = CIImage(cgImage: cgImage)
        }

        super.init()
    }

    // MARK: - OTCustomVideoTransformer Protocol

    var name: String {
        return "BackgroundImageTransformer"
    }

    /// Transform the video frame by compositing the background image
    func transform(_ videoFrame: OTVideoFrame) {
        guard let pixelBuffer = videoFrame.getPlanesData(),
              let backgroundCI = backgroundCIImage else {
            return
        }

        // Get the video frame dimensions
        let width = Int(videoFrame.format?.imageWidth ?? 0)
        let height = Int(videoFrame.format?.imageHeight ?? 0)

        guard width > 0 && height > 0 else {
            return
        }

        // Create CIImage from the video frame pixel buffer
        let videoCI = CIImage(cvPixelBuffer: pixelBuffer)

        // Scale background image to match video dimensions
        let scaleX = CGFloat(width) / backgroundCI.extent.width
        let scaleY = CGFloat(height) / backgroundCI.extent.height
        let scaledBackground = backgroundCI.transformed(by: CGAffineTransform(scaleX: scaleX, y: scaleY))

        // Composite the video frame over the background
        // This creates a simple overlay effect - for more sophisticated background replacement,
        // you would need to implement person segmentation/masking
        let composite = videoCI.composited(over: scaledBackground)

        // Render the composited image back to the pixel buffer
        ciContext.render(composite, to: pixelBuffer)
    }

    /// Update the background image dynamically
    func updateBackgroundImage(_ newImage: UIImage) {
        self.backgroundImage = newImage

        if let cgImage = newImage.cgImage {
            self.backgroundCIImage = CIImage(cgImage: cgImage)
        }
    }
}

// MARK: - OTVideoFrame Extension

extension OTVideoFrame {
    /// Helper to get the pixel buffer from the video frame
    func getPlanesData() -> CVPixelBuffer? {
        // Get the first plane (Y plane for YUV format or RGB for RGB format)
        guard let planes = planes, planes.count > 0 else {
            return nil
        }

        // For simplicity, we're working with the assumption of NV12 or similar format
        // In production, you'd need to handle different pixel formats properly

        // Create a CVPixelBuffer from the plane data
        // This is a simplified version - actual implementation may vary based on format
        let width = Int(format?.imageWidth ?? 0)
        let height = Int(format?.imageHeight ?? 0)

        var pixelBuffer: CVPixelBuffer?
        let status = CVPixelBufferCreate(
            kCFAllocatorDefault,
            width,
            height,
            kCVPixelFormatType_32BGRA,
            nil,
            &pixelBuffer
        )

        guard status == kCVReturnSuccess, let buffer = pixelBuffer else {
            return nil
        }

        // Copy plane data to pixel buffer
        CVPixelBufferLockBaseAddress(buffer, [])
        defer { CVPixelBufferUnlockBaseAddress(buffer, []) }

        if let baseAddress = CVPixelBufferGetBaseAddress(buffer) {
            let bytesPerRow = CVPixelBufferGetBytesPerRow(buffer)
            let planeData = planes[0]

            // Copy the data (simplified - actual implementation needs format conversion)
            memcpy(baseAddress, planeData, min(planeData.count, bytesPerRow * height))
        }

        return buffer
    }
}
