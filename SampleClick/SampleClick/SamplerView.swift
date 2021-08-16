//
//  SamplerView.swift
//  SampleClick
//
//  Created by Simon Herron on 21/7/25.
//

import Cocoa
import SwiftySound

class SamplerView: NSView {

    // Dynamics
    @IBOutlet weak var ppRep: NSTextField!
    @IBOutlet weak var pRep: NSTextField!
    @IBOutlet weak var mpRep: NSTextField!
    @IBOutlet weak var mfRep: NSTextField!
    @IBOutlet weak var fRep: NSTextField!
    @IBOutlet weak var ffRep: NSTextField!
    @IBOutlet weak var RpRep: NSTextField!
    @IBOutlet weak var RfRep: NSTextField!
    
    // Indicators
    @IBOutlet weak var pitchIndicator: NSTextField!
    @IBOutlet weak var dyIndicator: NSTextField!
    @IBOutlet weak var repIndicator: NSTextField!

    // Timer
    @IBOutlet weak var startTimerButton: NSButton!
    @IBOutlet weak var showTimerCheck: NSButton!
    @IBOutlet weak var timeIndicator: NSTextField!
   
    // Count-in
    @IBOutlet weak var countInPop: NSPopUpButton!
    @IBOutlet weak var delayField: NSTextField!
    @IBOutlet weak var autoAdvanceField: NSTextField!
    @IBOutlet weak var autoAdvanceCheck: NSButton!
    @IBOutlet weak var playButton: NSButton!
    
    // Instrument
    @IBOutlet weak var instrumentPop: NSPopUpButton!
    @IBOutlet weak var sessionName: NSTextField!
    @IBOutlet weak var pedalIndicator: NSTextField!
    @IBOutlet weak var pedalIndicatorLabel: NSTextField!
    
    let pitches = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    let naturalPitches = ["C", "D", "E", "F", "G", "A", "B"]
    let harpNaturals = ["C", "D", "F", "G", "A"]
    let dynamics = ["pp", "p", "mp", "mf", "f", "ff", "Rp", "Rf"]
    var dyFields = [NSTextField]()
    
    var masterClock = 0
    var pitchIndex = -1
    var theRep = -1
    var theDy = 0 // runs mod 8 because there are 8 dynamics labeled 0-7
    var theTimer: Timer?
    var goOn = false
    var redo = false
//    var firstSound = false
    var autoAdvance: Int? = nil
    
    var output: String = ""
    var outputFile = ""
    let appDir = "/Users/simonherron/Documents/Sampler/"
    var harpMode: (harp: Bool, flats: Bool)? = nil // harp: whether it's harp mode or not; flats: whether were on flats or naturals

    var soundArr: [Sound]?
    var soundNames: [String]?
    
    override func keyDown(with event: NSEvent) {
        goOn = (event.keyCode == 49) // space
        redo = (event.keyCode == 36) // return
        
        if event.keyCode == 0 {
            autoAdvanceCheck.setNextState()
            resetAutoAdvance()
        }
    }
    
    @IBAction func startTimerPressed(_ sender: Any) {
        if startTimerButton.title == "Start Session" {
            // Buttons
            startTimerButton.title = "End Session"
            sessionName.isEnabled = false
            instrumentPop.isEnabled = false
            playButton.isEnabled = true
            
            // Output
            sessionName.stringValue = getProperPath(forInstrument: instrumentPop.titleOfSelectedItem!, name: sessionName.stringValue)
            outputFile = appDir + instrumentPop.titleOfSelectedItem! + "/" + sessionName.stringValue + ".csv"
            let sustainLabel = instrumentPop.titleOfSelectedItem! == "Piano" ? "Sustain," : ""
            output = "Velocity,Repitition,\(sustainLabel)PitchIndex,Pitch,Time,Delete"
            
            // Indicators
            readIndicators()
            while dyFields[theDy].intValue == 0 { // in case there is a 0 in the pp field
                theDy = (theDy + 1) % 8
            }
            updateIndicators()
            
            
            // Controlling Bools
            goOn = false
            redo = false
            
            // Timer
            masterClock = 0
            theTimer = Timer.scheduledTimer(timeInterval: 1.0, target: self, selector: #selector(fireTimer), userInfo: nil, repeats: true)
        } else {
            theTimer!.invalidate()
            startTimerButton.title = "Start Session"
            sessionName.isEnabled = true
            instrumentPop.isEnabled = true
            playButton.isEnabled = false
        }
        
    }
    
    
    
    func getPitchIndex(input: String) -> Int {
        var comps = input.map({String($0)}) // splits into array of characters
        let theOctave = Int(comps.last!)!
        comps.removeLast()
        let thePitch = comps.joined()
        
        let thePitchClass: Int
        if harpMode!.harp {
            if harpMode!.flats { // whether we're doing the flats or the naturals of the harp
                thePitchClass = naturalPitches.firstIndex(of: comps[0])!
                return 7 * (theOctave + 1) + thePitchClass // 7 notes per octave in the natural scale
            } else {
                thePitchClass = harpNaturals.firstIndex(of: thePitch)!
                return 100 + 5 * (theOctave + 1) + thePitchClass // 5 notes per octave in the weird harp scale
            }
        } else { // normal chromatics
            thePitchClass = pitches.firstIndex(of: thePitch)!
            return 12 * (theOctave + 1) + thePitchClass
        }
    }
   
    @objc func fireTimer() {
        masterClock += 1
        
        timeIndicator.stringValue = getTime(seconds: masterClock)
        
        if goOn {
            theRep = (theRep + 1) % Int(dyFields[theDy].intValue) // increments theRep
            
            if theRep == 0 { // if theRep is back at 0, we have reached the end of the dynamic and move on to next one
                theDy = (theDy + 1) % 8
            }
            while dyFields[theDy].intValue == 0 {
                theDy = (theDy + 1) % 8
                if theDy == 0 { // && theRep == 0
                    pitchIndex += 1
                }
            }
            
            updateIndicators()

            playSound()
            goOn = false
        }

        if redo {
            output += "d" // for delete
            redo = false
            
            playSound()
        }
        
        if masterClock % 10 == 0 {
            do {
                try output.write(toFile: outputFile, atomically: true, encoding: String.Encoding.utf8)
            } catch {
                print(error)
            }
        }
        
        if autoAdvance != nil {
            autoAdvance! -= 1
            if autoAdvance == 0 {
                autoAdvance = nil
                goOn = true
                autoAdvance = Int(autoAdvanceField.stringValue)
            }
        } 
    }
    
    @IBAction func playPressed(_sender: Any) {
        playSound()
    }
    
    func playSound() {
        Sound.stopAll()
        soundArr![countInPop.indexOfSelectedItem].play()
            
        output += "\n\(dynamics[theDy]),\(theRep + 1),\(pedalIndicator.stringValue),\(pitchIndex),\(pitchIndicator.stringValue),\(masterClock + Int(delayField.stringValue)!),"
        
        resetAutoAdvance()
    }
    
    
    func updateIndicators() {
        repIndicator.stringValue = String(theRep + 1)
        dyIndicator.stringValue = dynamics[theDy]
        
        let pitchClass: String
        var octave: Int
        
        if harpMode!.harp {
            if harpMode!.flats { // flats
                pitchClass = naturalPitches[(pitchIndex % 7)] + "b"
                octave = (pitchIndex/12) // apparently this rounds down
                
            } else { // naturals
                pitchClass = harpNaturals[(pitchIndex - 100) % 5]
                octave = (pitchIndex - 100)/5 - 1
            }
        } else {
            pitchClass = pitches[(pitchIndex) % 12]
            octave = (pitchIndex/12) - 1 // apparently this rounds down
        }
        
        let pitch = pitchClass + String(octave)
        pitchIndicator.stringValue = pitch
    }

    func readIndicators() {
        harpMode = (instrumentPop.titleOfSelectedItem! == "Harp", pitchIndicator.stringValue.contains("b"))
        pitchIndex = getPitchIndex(input: pitchIndicator.stringValue)
        theDy = dynamics.firstIndex(of: dyIndicator.stringValue)!
        theRep = Int(repIndicator.stringValue)! - 1
    }
    
    override func draw(_ dirtyRect: NSRect) {
        super.draw(dirtyRect)
        

        // Drawing code here.
        dyFields = [ppRep, pRep, mpRep, mfRep, fRep, ffRep, RpRep, RfRep]
        
        countInPop.removeAllItems()
        instrumentPop.removeAllItems()
        instrumentPop.addItems(withTitles: ["Piano", "Organ", "Harp"])
        instrumentPop.selectItem(withTitle: "Organ")
        instrumentSelected("gesichtsbein")
    }
    
    override var acceptsFirstResponder: Bool {
        true
    }
    
    func populateSounds() {
        countInPop.addItems(withTitles: soundNames!)
        countInPop.selectItem(withTitle: "SampleClickShort")
    }
    
    @IBAction func showTimerToggle(_ sender: Any) {
        timeIndicator.isHidden = !timeIndicator.isHidden
    }
    
    func resetAutoAdvance() {
        if autoAdvanceCheck.state.rawValue == 1 {
            autoAdvance = Int(autoAdvanceField.stringValue)!
        } else {
            autoAdvance = nil
        }
    }
    
    @IBAction func instrumentSelected(_ sender: Any) {
        print("here")
        pedalIndicator.isHidden = !(instrumentPop.titleOfSelectedItem! == "Piano")
        pedalIndicatorLabel.isHidden = !(instrumentPop.titleOfSelectedItem! == "Piano")
        
        let theInstrument = instrumentPop.titleOfSelectedItem!
        sessionName.stringValue = getProperPath(forInstrument: theInstrument, name: theInstrument)
    }
    
    func getProperPath(forInstrument instrument: String, name: String) -> String {
        var name = name
        var increment = 0
        let instrDir = appDir + instrument
        let theFM = FileManager.default
        do {
            let contents = try theFM.contentsOfDirectory(atPath: instrDir)
            while contents.contains(name + ".csv") {
                increment += 1
                name = name + String(increment)
            }
        } catch {
            print(error)
        }
        
        return name
    }
    
    func getTime(seconds: Int) -> String {
      return "\(seconds / 3600):\((seconds % 3600) / 60):\((seconds % 3600) % 60)"
    }
}
