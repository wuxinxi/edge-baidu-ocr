import Foundation
import Vision
import AppKit

// macOS Apple Neural Engine 真实视觉 OCR 辅助器：
// 对任意纯图片 (.png/.jpg) 或无文字层扫描件 PDF 页面执行真实光学字符识别，输出 JSON 数组 [{bbox_1000, text}]
guard CommandLine.arguments.count > 1 else {
    print("[]")
    exit(0)
}

let imagePath = CommandLine.arguments[1]
let url = URL(fileURLWithPath: imagePath)
guard let img = NSImage(contentsOf: url),
      let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    print("[]")
    exit(0)
}

let req = VNRecognizeTextRequest()
req.recognitionLevel = .accurate
req.usesLanguageCorrection = true
req.recognitionLanguages = ["zh-Hans", "en-US"]

let handler = VNImageRequestHandler(cgImage: cg, options: [:])
do {
    try handler.perform([req])
    var items: [[String: Any]] = []
    for obs in (req.results ?? []) {
        guard let candidate = obs.topCandidates(1).first else { continue }
        let b = obs.boundingBox
        let x1 = max(0, min(1000, Int((b.minX * 1000.0).rounded())))
        let y1 = max(0, min(1000, Int(((1.0 - b.maxY) * 1000.0).rounded())))
        let x2 = max(0, min(1000, Int((b.maxX * 1000.0).rounded())))
        let y2 = max(0, min(1000, Int(((1.0 - b.minY) * 1000.0).rounded())))
        items.append([
            "bbox_1000": [x1, y1, x2, y2],
            "text": candidate.string,
            "confidence": candidate.confidence
        ])
    }
    let data = try JSONSerialization.data(withJSONObject: items, options: [])
    if let jsonStr = String(data: data, encoding: .utf8) {
        print(jsonStr)
    } else {
        print("[]")
    }
} catch {
    print("[]")
}
