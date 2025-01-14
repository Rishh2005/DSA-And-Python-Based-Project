import tkinter as tk
from tkinter import ttk
import pygame
import numpy as np

class DrumPad:
    def __init__(self):
        # Initialize pygame mixer for sound
        pygame.mixer.init(frequency=44100, channels=2)
        
        # Create the main window
        self.root = tk.Tk()
        self.root.title("Python Drum Pad")
        self.root.geometry("600x700")
        self.root.configure(bg='#121212')
        
        # Configure styles
        style = ttk.Style()
        style.configure('Pad.TButton', font=('Arial', 14), padding=20)
        
        # Sound setup - using sine waves at different frequencies
        self.sounds = {}
        self.generate_sounds()
        
        # Create title
        title = tk.Label(
            self.root,
            text="Drum Pad",
            font=('Arial', 24),
            bg='#121212',
            fg='white'
        )
        title.pack(pady=20)
        
        # Create pad container
        pad_frame = tk.Frame(self.root, bg='#121212')
        pad_frame.pack(padx=20, pady=20)
        
        # Define pad colors and notes
        self.pad_config = [
            ('Q', 'C4', '#FF6B6B'), ('W', 'D4', '#4ECDC4'), ('E', 'E4', '#45B7D1'), ('R', 'F4', '#F7B267'),
            ('A', 'G4', '#6B48FF'), ('S', 'A4', '#3DDC97'), ('D', 'B4', '#FF7F50'), ('F', 'C5', '#FF69B4'),
            ('Z', 'D5', '#7B68EE'), ('X', 'E5', '#20B2AA'), ('C', 'F5', '#FFA07A'), ('V', 'G5', '#00CED1'),
            ('1', 'A5', '#9370DB'), ('2', 'B5', '#32CD32'), ('3', 'C6', '#FF6347'), ('4', 'D6', '#1E90FF')
        ]
        
        # Create drum pads
        for i, (key, note, color) in enumerate(self.pad_config):
            row = i // 4
            col = i % 4
            
            pad = tk.Button(
                pad_frame,
                text=key,
                width=8,
                height=4,
                bg=color,
                fg='white',
                font=('Arial', 14, 'bold'),
                relief='raised'
            )
            pad.grid(row=row, column=col, padx=5, pady=5)
            pad.bind('<Button-1>', lambda e, note=note: self.play_sound(note))
            
        # Create effects button
        self.effects_on = False
        self.effects_button = tk.Button(
            self.root,
            text="Effects: OFF",
            bg='#4CAF50',
            fg='white',
            font=('Arial', 12),
            command=self.toggle_effects
        )
        self.effects_button.pack(pady=20)
        
        # Bind keyboard events
        self.root.bind('<KeyPress>', self.handle_keypress)
        
    def generate_sounds(self):
        """Generate sine wave sounds for each note"""
        sample_rate = 44100
        duration = 0.3
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Define frequencies for notes (simplified)
        frequencies = {
            'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
            'G4': 392.00, 'A4': 440.00, 'B4': 493.88, 'C5': 523.25,
            'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99,
            'A5': 880.00, 'B5': 658.77, 'C6': 1046.50, 'D6': 1174.66
        }
        
        for note, freq in frequencies.items():
            # Generate sine wave
            sound_wave = np.sin(2 * np.pi * freq * t)
            # Apply envelope
            envelope = np.exp(-3 * t)
            sound_wave = sound_wave * envelope
            # Normalize
            sound_wave = sound_wave * 0.3  # Reduce volume
            # Create stereo array and ensure it's C-contiguous
            stereo_wave = np.ascontiguousarray(np.vstack((sound_wave, sound_wave)).T)
            sound_wave_int = np.int16(stereo_wave * 32767)
            # Create pygame Sound object
            self.sounds[note] = pygame.sndarray.make_sound(sound_wave_int)
    
    def play_sound(self, note):
        """Play the sound for a given note"""
        if note in self.sounds:
            sound = self.sounds[note]
            if self.effects_on:
                # Apply a simple effect (volume variation)
                sound.set_volume(0.7)
            else:
                sound.set_volume(1.0)
            sound.play()
    
    def toggle_effects(self):
        """Toggle effects on/off"""
        self.effects_on = not self.effects_on
        if self.effects_on:
            self.effects_button.configure(text="Effects: ON", bg='#e91e63')
        else:
            self.effects_button.configure(text="Effects: OFF", bg='#4CAF50')
    
    def handle_keypress(self, event):
        """Handle keyboard input"""
        key = event.char.upper()
        for pad_key, note, _ in self.pad_config:
            if key == pad_key:
                self.play_sound(note)
                break
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = DrumPad()
    app.run()
