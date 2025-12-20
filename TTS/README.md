# TTS (Speech-to-Text with Vonage Video Background Transformers)

An iOS application that performs real-time speech recognition and automatically displays organization logos as video backgrounds using Vonage Media Processor API.

## Features

- **Real-time Speech Recognition**: Continuous speech-to-text transcription using Apple's Speech framework
- **Natural Language Processing**: Automatic organization name detection using Apple's Natural Language framework
- **Dynamic Video Backgrounds**: Organization logos displayed as video backgrounds via Vonage Media Transformers
- **Live Captions**: Real-time caption display with auto-restart capability

## How It Works

1. The app continuously listens to speech input and transcribes it in real-time
2. Natural Language Processing analyzes the transcribed text to identify organization names
3. When an organization is detected (e.g., "Apple"), the app:
   - Loads the corresponding image from Assets (`Apple-Org`)
   - Displays it in a UIImageView on screen
   - Applies it as a video background using Vonage Media Transformer

## Architecture

### Files

- **ViewController.swift**: Main view controller handling speech recognition, NLP, and UI coordination
- **VonageMediaManager.swift**: Abstraction layer for Vonage/OpenTok API interactions
- **BackgroundImageTransformer.swift**: Custom video transformer for background image replacement

### Key Components

#### VonageMediaManager
Provides a simple interface to Vonage Video API:
- Session management (connect/disconnect)
- Publisher management (start/stop publishing)
- Video transformer operations (apply/remove background images)

#### BackgroundImageTransformer
Implements `OTCustomVideoTransformer` protocol to:
- Replace video backgrounds with custom images
- Handle real-time video frame processing
- Support dynamic background updates

## Setup Instructions

### 1. Install Dependencies

```bash
cd /Users/jaideep/Documents/AIProjects/TTS
pod install
```

After installation, open `TTS.xcworkspace` (not `TTS.xcodeproj`)

### 2. Configure Vonage Credentials

Edit `ViewController.swift` and replace the placeholder credentials:

```swift
private let vonageApiKey = "YOUR_API_KEY"
private let vonageSessionId = "YOUR_SESSION_ID"
private let vonageToken = "YOUR_TOKEN"
```

To get Vonage credentials:
1. Sign up at [Vonage Video API](https://www.vonage.com/communications-apis/video/)
2. Create a new project
3. Get your API Key, Session ID, and Token

### 3. Add Organization Images to Assets

1. Open `Assets.xcassets` in Xcode
2. Add images with the naming convention: `[OrganizationName]-Org`
   - Example: `Apple-Org`, `Google-Org`, `Microsoft-Org`
3. Ensure images are added to the TTS target

### 4. Configure Permissions

The app requires the following permissions (already configured in `Info.plist`):
- **Microphone**: For speech input
- **Speech Recognition**: For transcription
- **Camera** (if using video): For Vonage video publishing

Add to `Info.plist` if not present:
```xml
<key>NSMicrophoneUsageDescription</key>
<string>This app needs microphone access for speech recognition</string>
<key>NSSpeechRecognitionUsageDescription</key>
<string>This app needs speech recognition for live captions</string>
<key>NSCameraUsageDescription</key>
<string>This app needs camera access for video</string>
```

## Usage

1. Launch the app
2. Grant microphone and speech recognition permissions when prompted
3. The app will automatically start:
   - Speech recognition
   - Vonage video session
4. Speak naturally and mention organization names
5. When an organization is detected, its logo will appear as the video background

## Example

**User speaks:** "I work at Apple and use Google services"

**App behavior:**
1. Transcribes: "I work at Apple and use Google services"
2. Detects: "Apple" and "Google" as organizations
3. Loads and displays `Apple-Org` image (or `Google-Org` if detected last)
4. Applies the logo as video background using Vonage transformer

## Technical Details

### Speech Recognition
- Uses `SFSpeechRecognizer` with US English locale
- Continuous recognition with auto-restart
- Partial results displayed in real-time

### Natural Language Processing
- Uses `NLTagger` with `.nameType` scheme
- Identifies organization names (`.organizationName`)
- Options: `.omitWhitespace`, `.omitPunctuation`, `.joinNames`

### Vonage Video Transformers
- Custom transformer implementing `OTCustomVideoTransformer`
- Video frame processing using Core Image
- Background image compositing over video feed

### Supported Devices
- iOS 15.0+
- Apple A11 Bionic chipset or newer (for video transformers)
- Adequate processing resources required for stable transformer operation

## Limitations

1. **Simple Background Overlay**: Current implementation overlays the background image without person segmentation. For production use, integrate ML-based person segmentation (e.g., Vision framework) for true background replacement.

2. **Single Organization Display**: Only displays the most recently detected organization. For multiple organizations, implement a queue or priority system.

3. **Vonage Session**: Requires active Vonage session and credentials. For testing without video, you can disable Vonage initialization.

## Future Enhancements

- [ ] Person segmentation for true background replacement
- [ ] Support for multiple organization logos simultaneously
- [ ] Logo position/size customization
- [ ] Animation effects for logo transitions
- [ ] Cloud-based organization logo repository
- [ ] Support for other named entities (people, places)

## Dependencies

- **OpenTok** (~> 2.27): Vonage Video API SDK
- **VonageClientSDKVideoTransformers** (~> 2.27): Media Transformers library
- **Speech**: Apple Speech Recognition
- **NaturalLanguage**: Apple NLP framework
- **AVFoundation**: Audio/Video handling
- **CoreImage**: Image processing

## License

[Your License Here]

## Credits

Based on:
- [Vonage Media Processor Documentation](https://tokbox.com/developer/guides/vonage-media-processor/ios-swift)
- [OpenTok iOS SDK Samples](https://github.com/opentok/opentok-ios-sdk-samples-swift)
