import os
import numpy as np
import tensorflow as tf
from magenta.models.melody_rnn import melody_rnn_sequence_generator
from magenta.pipelines import dag_pipeline
from magenta.pipelines import note_sequence_pipelines
from magenta.pipelines import performance_pipelines
from magenta.pipelines import standard_pipelines
from magenta.protobuf import generator_pb2
from magenta.protobuf import music_pb2
from magenta.common import sequence_generator_bundle_file

# Load the Melody RNN model
bundle_file = 'path_to_your_model_bundle.mag'  # Replace with the path to your model bundle
generator_map = melody_rnn_sequence_generator.get_generator_map()
generator_details = generator_map['basic_rnn']
generator = melody_rnn_sequence_generator.MelodyRnnSequenceGenerator(
    generator_details, bundle_file=bundle_file)

# Function to generate music based on genre
def generate_music(genre, steps=64, temperature=1.0):
    # Define the start note sequence based on genre
    start_note_sequence = music_pb2.NoteSequence()
    start_note_sequence.ticks_per_quarter = 220
    
    if genre == 'classical':
        start_note_sequence.notes.add(pitch=60, start_time=0, end_time=1, velocity=80)
    elif genre == 'jazz':
        start_note_sequence.notes.add(pitch=64, start_time=0, end_time=1, velocity=80)
    elif genre == 'rock':
        start_note_sequence.notes.add(pitch=67, start_time=0, end_time=1, velocity=80)
    else:
        raise ValueError("Unsupported genre")

    # Generate the music
    generator_options = generator_pb2.GeneratorOptions()
    generator_options.args['temperature'].float_value = temperature
    generate_section = generator_pb2.GeneratorOptions.GenerateSection(
        start_step=0, end_step=steps)
    generator_options.generate_sections.append(generate_section)

    output_sequence = generator.generate(start_note_sequence, generator_options)
    return output_sequence

# Function to export the composition as a MIDI file
def export_to_midi(note_sequence, file_name):
    from magenta.music.midi_io import sequence_proto_to_midi_file
    sequence_proto_to_midi_file(note_sequence, file_name)

# Function for real-time playback
def play_midi(file_name):
    import pygame
    pygame.mixer.init()
    pygame.mixer.music.load(file_name)
    pygame.mixer.music.play()

# Main function
def main():
    genre = input("Enter the genre (classical, jazz, rock): ")
    steps = int(input("Enter the number of steps (default is 64): ") or 64)
    temperature = float(input("Enter the temperature (default is 1.0): ") or 1.0)

    composition = generate_music(genre, steps, temperature)
    file_name = f"{genre}_composition.mid"
    export_to_midi(composition, file_name)
    print(f"Composition saved as {file_name}")

    play_choice = input("Do you want to play the composition? (yes/no): ")
    if play_choice.lower() == 'yes':
        play_midi(file_name)

if __name__ == "__main__":
    main()