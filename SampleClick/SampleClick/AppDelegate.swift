//
//  AppDelegate.swift
//  SampleClick
//
//  Created by Simon Herron on 21/7/24.
//

import Cocoa
import SwiftySound

@main class AppDelegate: NSObject, NSApplicationDelegate {

    @IBOutlet var window: NSWindow!
    @IBOutlet weak var theSamplerView: SamplerView!
    
    
    func applicationDidFinishLaunching(_ aNotification: Notification) {
        // Insert code here to initialize your application
        print("app")
        
        theSamplerView.soundArr = [Sound]()
        theSamplerView.soundNames = [String]()
        let countInDir = "/Users/simonherron/Documents/Sampler/CountIns"
        let theFM = FileManager.default
//        let docDir = theFM.urls(for: .documentDirectory, in: .userDomainMask)
        do {
            let contents = try theFM.contentsOfDirectory(atPath: countInDir)
            for var i in contents {
                theSamplerView.soundArr!.append(Sound(url: URL(string: countInDir + "/" + i)!)!)
                i.removeLast(4)
                theSamplerView.soundNames!.append(i)
            }
        } catch {
            print(error)
        }
        
        theSamplerView.playButton.isEnabled = false
        theSamplerView.autoAdvanceCheck.state = .off
        theSamplerView.populateSounds()
    }

    func applicationWillTerminate(_ aNotification: Notification) {
        // Insert code here to tear down your application
    }
    
    
}


