"""
Gathers all the melody generation functions using the Pelofi grammar
Manipulates emphasis of notes based on volume
Also tests C as the target note but based on context

"""
import numpy as np
import pandas as pd
import pickle
from music21 import *

#organizes the artificial grammar (which is initially defined as a dictionary) into a pd.DataFrame
#matrix: a dictionary
def organize_matrix(matrix):
  matrix = pd.DataFrame(matrix, index = matrix.keys())
  return matrix

#Gives all the theoretical transition probabilities in the artificial grammar
#matrix: pd.DataFrame
def theo_trans_probs(matrix):
    list = []
    for column in matrix:
        for item in matrix.index:
            if matrix[column][item] != 0:
                list.append([str(item)+str(column), matrix[column][item]])

    df = pd.DataFrame(list, columns = ['Pitches', 'Transition probs'])
    df.set_index('Pitches')
    sorted_df = df.sort_values(by = 'Pitches')
    return sorted_df

#defining different transition matrices describing the artificial grammar

#some mistakes in the original matrix, this should be the one that has been corrected
matrix_pelofi_low = {
    'A3': [0, 0, 0, 0, 0, 0, 0], #probability of getting to a from starting points a, b, and c respectively
    'Bb3': [.6, 0, 0, 0, 0, 0, 0],
    'C4': [.2, .5, 0, 0, .2, 0, 0],
    'C#4': [0, 0, .6, 0, .2, .4, 0],
    'E4': [.2, .5, .2, 0, 0, 0, 0],
    'G4': [0, 0, .2, .4, .6, 0, 0],
    'A4':[0, 0, 0, .6, 0, .6, 1]
}
matrix_pelofi_low = organize_matrix(matrix_pelofi_low)
ttp_pelofi_low = theo_trans_probs(matrix_pelofi_low)

#same as above but with A3 and A4 switched
matrix_pelofi_high = {
    'A4': [0, 0, 0, 0, 0, 0, 0], 
    'Bb3': [.6, 0, 0, 0, 0, 0, 0],
    'C4': [.2, .5, 0, 0, .2, 0, 0],
    'C#4': [0, 0, .6, 0, .2, .4, 0],
    'E4': [.2, .5, .2, 0, 0, 0, 0],
    'G4': [0, 0, .2, .4, .6, 0, 0],
    'A3':[0, 0, 0, .6, 0, .6, 1]
}
matrix_pelofi_high = organize_matrix(matrix_pelofi_high)
ttp_pelofi_high = theo_trans_probs(matrix_pelofi_high)

####GENERATING MELODIES#############

"""
markov_melody generates a batch of melodies.
  highstart generates melodies that start on A4 and end on A3, lowstart does the inverse
  the intermediate notes follow the same grammar
num_melodies: number of melodies to be generated
matrix: one of the matrices above
returns a nested list: [[melody 1],[melody 2]] etc.
"""

def markov_melody_lowstart(num_melodies, matrix): #could also randomize lengths more later
  melody_list = []

  while len(melody_list) < num_melodies:
    #define the starting note
    results = ['A3']

    #appending new notes to the starting state until max number of notes reached
    #while len(results) < length:
    while 'A4' not in results:
      new_state = np.random.choice(matrix.index, p = matrix.loc[results[-1]])
      results.append(new_state)
    
    melody_list.append(results)
    file_name = "melody"+str(len(melody_list))+".pkl"
    open_file =open(file_name, "wb")
    pickle.dump(results, open_file)
    open_file.close()

  #melody_list = np.array(melody_list) 
    #can also change to pandas etc later for data analysis
  return melody_list

def markov_melody_highstart(num_melodies, matrix): #could also randomize lengths more later
  melody_list = []

  while len(melody_list) < num_melodies:
    #define the starting note
    results = ['A4']

    #appending new notes to the starting state until max number of notes reached
    #while len(results) < length:
    while 'A3' not in results:
      new_state = np.random.choice(matrix.index, p = matrix.loc[results[-1]])
      results.append(new_state)
    
    melody_list.append(results)
    file_name = "melody"+str(len(melody_list))+".pkl"
    open_file =open(file_name, "wb")
    pickle.dump(results, open_file)
    open_file.close()

  #melody_list = np.array(melody_list) 
    #can also change to pandas etc later for data analysis
  return melody_list
  

"""
to_midi_exposure takes the list of melodies generated above and converts into MIDI files for a set of exposure melodies (all notes the same length/volume)
setsize: the number of melodies to be converted (if continuing from markov generation above, it can be len(melody_list))
saves all the converted midi files
"""
def to_midi_exposure(setsize):
  for i in range(1,setsize+1):
    file = open('melody'+str(i)+".pkl", 'rb')
    melody1 = pickle.load(file)

    stream_current = stream.Stream()

    for j in melody1: 
      newnote = note.Note(j)
      stream_current.append(newnote)

      stream_current.write("midi", "stream"+str(i)+".mid")


  
"""
to_midi_fc generates forced choice melodies with higher volume on the target note, paired with a melody where the 
setsize: how many melodies to convert, usually len(melody_list)
target: note with high IC given the context given as a string
context: note preceding target given as string
returns ONLY the midi files of melodies where the specified context-note pair occurs
"""
#should change how the output melodies are numbered

def to_midi_fc(setsize, target, context):
  for number in range(1, setsize+1):
    target_found = False
    file = open('melody'+str(number)+'.pkl', 'rb')
    test_melody = pickle.load(file)

    #generates the first ('correct') melody
    stream_correct = stream.Stream()

    for i in range(len(test_melody)): 
      newnote = note.Note(test_melody[i])
      newnote.volume = volume.Volume(velocity=90)
      if test_melody[i] == target and test_melody[i-1] == context:        
        newnote.volume = volume.Volume(velocity=150) 
        target_found = True
      stream_correct.append(newnote)
    
    if target_found:
      #generates the second ('incorrect') melody
      stream_incorrect = stream.Stream()

      already_used = False
      for i in test_melody: 
        if i == context and already_used == False : 
          newnote = note.Note(i)
          newnote.volume = volume.Volume(velocity=150) 
          stream_incorrect.append(newnote)
          already_used = True
        else:
          newnote = note.Note(i)
          newnote.volume = volume.Volume(velocity=90) 
          stream_incorrect.append(newnote)

      r = note.Rest(duration = duration.Duration(4))
      stream_correct.append(r)
      stream_correct.append(stream_incorrect)
      stream_correct.write('midi', 'test_1correct'+str(number)+'.mid')
#---------------------------------------------------------------------------------------------------
"""
makes a set of melodies where the target note is either an eighth, quarter, half, or whole note.
setsize: number of melodies (for every melody the function will make a set of 4 corresponding melodies)
target: eiher a low- or high-IC note
saves converted midi files
"""

def to_midi_slider_duration(setsize, target, context):
  
  #i = 1
  for number in range(1, setsize+1):
    target_found = False
  #generates the first ('correct') melody
    file = open('melody'+str(number)+'.pkl', 'rb')
    test_melody = pickle.load(file) #could make a version without pickle but then the melodies can't be stored...

    notelengths = [0.5,1,2,4]
    
    for length in notelengths:
      stream_final = stream.Stream()
      for i in range(len(test_melody)): 
        
        if test_melody[i] == target and test_melody[i-1] == context:
          newnote = note.Note(test_melody[i],  duration = duration.Duration(length))
          target_found = True
        else:
          newnote = note.Note(test_melody[i], duration = duration.Duration(1))
        stream_final.append(newnote)
        

      if target_found == True:
        #stream_final.write('midi', 'test_interpret'+str(length)+'_'+str(i)+'.mid')
        stream_final.write('midi', 'slider_duration'+str(length)+'.mid')
        #i += 1


def to_midi_slider_volume(setsize, target, context):
  
  #i = 1
  for number in range(1, setsize+1):
    target_found = False
  #generates the first ('correct') melody
    file = open('melody'+str(number)+'.pkl', 'rb')
    test_melody = pickle.load(file) #could make a version without pickle but then the melodies can't be stored...

    volumes = [50, 90, 120, 150]
    
    for level in volumes:
      stream_final = stream.Stream()
      for i in range(len(test_melody)): 
        newnote = note.Note(test_melody[i],  duration = duration.Duration(1))
        if test_melody[i] == target and test_melody[i-1] == context:
          newnote.volume = volume.Volume(velocity=level)
          target_found = True
        stream_final.append(newnote)
        

      if target_found == True:
        #stream_final.write('midi', 'test_interpret'+str(length)+'_'+str(i)+'.mid')
        stream_final.write('midi', 'slider_volume'+str(level)+'.mid')
        #i += 1
#introducing stringmaker: a very, very stupid way (but it works! at least for linux) to batch convert midi to mp3 files by changing the string that is then fed into a cmd line
#title: a string giving the generic melody title of the midi file, e.g. 'test_correct' (number will be appended to it)
#length: how many melodies are being converted
#returns a big string with one line of command line code for each melody; copy paste into next section to run and convert
#example: stringmaker('test_incorrect', 5)

def stringmaker(title, length):
  newstring = ''
  for i in range(length+1):
    tempstring = '!fluidsynth -ni font.sf2 ' + title + str(i) + '.mid -F ' + title +str(i)+'.mp3 -r 44100'

    newstring = newstring+ '\n' +tempstring

  print(newstring)

