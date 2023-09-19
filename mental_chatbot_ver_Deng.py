
MODEL_ENGINE = "gpt-3.5-turbo"

# record a speech from input, and save it as wave
def Test_score(answers):
    counts = {"A": 0, "B": 0, "C": 0, "D": 0} 
    total_score = 0  

    for answer in answers:
        counts[answer] += 1 
        if answer == "A":
            total_score += 0
        elif answer == "B":
            total_score += 1
        elif answer == "C":
            total_score += 2
        elif answer == "D":
            total_score += 3
    return total_score

def Test_grade(number):
    if number >= 20:
        grade = "severe depression"
        treat = "Immediate initiation of pharmacotherapy and, if severe impairment or poor response to therapy, expedited referral to a mental health specialist for psychotherapy and/or collaborative management."
    elif number >= 15:
        grade = "moderatly severe depression"
        treat = "Active treatment with pharmacotherapy and/or psychotherapy."
    elif number >= 10:
        grade = "moderate depression"
        treat = "Treatment plan, considering counseling, follow-up and/or pharmacotherapy."
    elif number >= 5:
        grade = "mild depression"
        treat = "Watchful waiting; repeat PHQ-9 at follow-up."
    else:
        grade = "no depression"
        treat = "None"
        
    return grade, treat
            
def Speech_recording_with_silence_timeout(RECORD_SECONDS, WAVE_OUTPUT_FILENAME, SILENCE_TIMEOUT):
    # define audio recording parameters
    import pyaudio
    import wave
    import audioop
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    
    # initialize PyAudio
    audio = pyaudio.PyAudio()
    
    # open audio stream
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    
    print("Recording audio...")
    
    frames = []
    silence_counter = 0  # Counter for consecutive silence frames
    
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
        
        # Check if the audio data is silent
        is_silent = audioop.rms(data, 2) < 300  # Adjust the threshold as needed
        
        if is_silent:
            silence_counter += 1
        else:
            silence_counter = 0
        
        if silence_counter > int(SILENCE_TIMEOUT / (CHUNK / RATE)):
            break
    
    print("Audio recording complete!")
    
    # stop recording and close audio stream
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # save audio recording to WAV file
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    print("Audio file saved as", WAVE_OUTPUT_FILENAME)

def Get_response(prompt_full):
    """Returns the response for the given prompt using the OpenAI API."""
    completion = openai.ChatCompletion.create(
        model = MODEL_ENGINE,
        messages=prompt_full,
        max_tokens = 1024,
        temperature = 0.2,
    )
    return completion

# a simple way of text2voice    
def read_text1(text):
    
    import pyttsx3
    
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    
# use microsoft Azure cognitive to do text2voice    
def read_text_ms(text):

    import os
    import azure.cognitiveservices.speech as speechsdk
    
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=, region=) 
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    
    # The language of the voice that speaks.
    # speech_config.speech_synthesis_voice_name='zh-CN-liaoning' #'en-GB-BellaNeural'
    
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    
    # The language of the voice that speaks.
    speech_synthesis_voice_name='en-GB-SoniaNeural' # XiaomoNeural zh-CN-XiaoyiNeural
    ssml = """<speak version='1.0' xml:lang='en-GB' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='http://www.w3.org/2001/mstts'>
        <voice name="{}">
            {}
        </voice>
    </speak>""".format(speech_synthesis_voice_name, text)    
    # ssml = """<speak version='1.0' xml:lang='zh-CN' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='http://www.w3.org/2001/mstts'>
    #     <voice name="{}">
    #         <mstts:express-as role="Girl" style="affectionate" styledegree="2"> 
    #             {}
    #         </mstts:express-as>
    #     </voice>
    # </speak>""".format(speech_synthesis_voice_name, text)
    
    # Synthesize the SSML
    print("SSML to synthesize: \r\n{}".format(ssml))
    speech_synthesis_result = speech_synthesizer.speak_ssml_async(ssml).get()

    # speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
    
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")
            

    
import os
import openai
import re
from io import BytesIO
import requests
from PIL import Image
os.chdir('')

WAVE_OUTPUT_FILENAME = "chat1.wav"
RECORD_SECONDS = 60
SILENCE_TIMEOUT= 5

problems=['anhedonia','depressed emotion','sleeping problem','fatigue','eating behavior','self-worth impact','concentration','Motor or speech changes','Suicidal ideation']

openai.api_key = ''
USERNAME = "Client"
AI_NAME = "Psychotherapist"

answers=[]

# Speech_recording(RECORD_SECONDS, WAVE_OUTPUT_FILENAME) 
   
# # Note: you need to be using OpenAI Python v0.27.0 for the code below to work
# #  convert audio to text
# audio_file= open(WAVE_OUTPUT_FILENAME, "rb") #"/path/to/file/german.mp3"
# transcript0 = openai.Audio.transcribe("whisper-1", audio_file).text

# Set the initial prompt to include a personality and habits
import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
 
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion_with_backoff(**kwargs):
    return openai.Completion.create(**kwargs)
 
completion_with_backoff(model="text-davinci-003", prompt="Once upon a time,")

conversation_para = ('''Now you are playing the role of a professional psychotherapist. I am your client, and I will share my thoughts with you. I hope you can have a conversation with me, understand my feelings, and comfort me to make me feel better. Remember you just play the role of a therapist, don’t act a part of client to answer the questions by yourself!!! When I want to confide in you, please follow the topic and let me finish the process of sharing. You will constantly find different topics to converse with me. You are highly loyal to clients with a positive impression and understand and protect their privacy. We can have casual conversation in the first several rounds. After 5-10 dialogs, before the user has the intention to end a topic, you have to suggest that I take a mental health test in which you ask me 9 questions one by one. Ask questions one by one!!!Remember you just play the role of a therapist, don’t act a part of client to answer the questions by yourself!!! These 9 questions are: 1. Have you found little pleasure or interest in doing things? 2. Have you found yourself feeling down, depressed or hopeless? 3. Have you had trouble falling or staying asleep, or sleeping too much? 4. Have you been feeling tired or had little energy? 5. Have you had a poor appetite or been overeating? 6. Have you felt that you're a failure or let yourself or your family down? 7. Have you had some trouble concentrating on things like reading the paper or watching TV? 8. Have you been moving or speaking slowly, or been very fidgety, so that other people could notice? 9. Have you thought that you'd be better off dead or hurting yourself in some way? You need to ask question one after another, in this order. Do not change any words in the question. Do not have other chat or topics in the process of question and answers. The client will answer your question iteratively. After asking each question, you will need to wait for answer from client, remember and categorise the answer to one of the following options: A: No, not at all; B: On some days; C: On more than half the days; D: Nearly every day. After client answers each question, you don't tell the user that their answer consists of four options, A,B,C,D, let them answer freely. But you will need to provide the category of the answer in one of the 4 options. Before you ask the next question, please restate your judgement of users’ answer according to the following format “Your answer is: ()”. Fill the () with your judgement of my answer . Please do not provide your comments to the answer of client. ''')    
conversation_history = (''' ''')
#conversation_history = INITIAL_PROMPT + "\n"
print("transcript:", conversation_history)
read_text_ms(text = "Hi! Nice to meet you. How are you? What is your name")

while True:
    record_status=0
    if len(answers)!=9:
        record_status=1
        #if not os.path.isfile(WAVE_OUTPUT_FILENAME):
        #    Speech_recording(RECORD_SECONDS, WAVE_OUTPUT_FILENAME)
        Speech_recording_with_silence_timeout(RECORD_SECONDS, WAVE_OUTPUT_FILENAME, SILENCE_TIMEOUT) 
            
        # Note: you need to be using OpenAI Python v0.27.0 for the code below to work
        #  convert audio to text
        audio_file= open(WAVE_OUTPUT_FILENAME, "rb") #"/path/to/file/german.mp3"
        transcript = openai.Audio.transcribe("whisper-1", audio_file).text
        print("transcript:", transcript)
        
        if "End conversation" in transcript or "End conversation" in transcript:
            print("Terminate")
            read_text_ms(text = "OK，Let's end conversation."+f"{USERNAME}")
            break
    
        
        #audio_file= open(WAVE_OUTPUT_FILENAME, "rb") 
        #translate = openai.Audio.translate("whisper-1", audio_file)
        #print("translate:", translate.text)
        
        # check if the number of token is near the limit
        if len([elt.split() for elt in conversation_history])>4000:
            idx_n = [idx for idx, item in enumerate(conversation_history.lower()) if '\n' in item]
            # delete after third /n
            delete_n_previous = 6
            conversation_history = conversation_history[0:idx_n[0]:] +'\n'+ conversation_history[idx_n[delete_n_previous]+1::]
            print('conversation history shortened')
            
        # Update the conversation history
        conversation_history += f"{USERNAME}: {transcript}\n"
        
    # add system prompt
    prompt_current = conversation_para + conversation_history
    # full prompt
    prompt_full =[
                    {"role": "user", "content": prompt_current}
                ]
    completion = Get_response(prompt_full)
    response = completion.choices[0].message.content
    
    match1 = re.findall(r"Your answer .*? ([A-D])", response)
    match2 = re.findall(r"Your answer .*? \"([A-D])", response)
    match3 = re.findall(r"Your .*?: \(([A-D])", response)
    match4 = re.findall(r"your answer .*? ([A-D])", response)
    match5 = re.findall(r"your answer .*? \"([A-D])", response)
    match6 = re.findall(r"your .*?: \(([A-D])", response)


    if match1:
        answers.append(match1[0])
        print(Test_score(answers))
    elif match2:
        answers.append(match2[0])
        print(Test_score(answers))
    elif match3:
        answers.append(match3[0])
        print(Test_score(answers))
    elif match4:
        answers.append(match4[0])
        print(Test_score(answers))
    elif match5:
        answers.append(match5[0])
        print(Test_score(answers))
    elif match6:
        answers.append(match6[0])
        print(Test_score(answers))        
      
        
    # Update the conversation history
    conversation_history += f"{AI_NAME}: {response}\n" 
    
    if record_status==0:
        answers.append('end')
        
    if len(answers)==9:
        total_score=Test_score(answers)
        depression_grade, adviced_treat = Test_grade(total_score)
        d_indices = [i for i, ans in enumerate(answers) if ans == 'D']
        main_problem= [problems[i] for i in d_indices]
        main_problem_sen = ''
        if len(main_problem) != 0:
            main_problem_sen  = " And the test shows the client is experiencing problems in following fields: " + ', '.join(main_problem) + ". You might pay some attendtion to those fields."
        conversation_para = ('''You are a professional psychotherapist, and I am your client. In our conversation, I'll be sharing my thoughts and feelings with you. To start, I've recently taken a depression screening test, and the results indicate {}. Proposed treatment actions is: ''' + adviced_treat + main_problem_sen +  ''' Over the course of our next 5 exchanges, I would like us to have a genuine conversation. Begin by addressing my depression test results sensitively. Then, provide me with some appropriate advice based on the proposed treatment actions and my current mental state to help me feel better. As we chat, please empathize with my emotions and offer comfort and guidance. Rather than delving into the reasons behind the test results, let's focus on actionable steps for me moving forward. Don't make a long story, the points that need to be mentioned above can be separated into different rounds. Talk to me more and listen to my thoughts. It is best to keep the length of each dialogue within 100 words.Your approach is client-centered, and you prioritize building a positive rapport while respecting my privacy. Please avoid taking on the role of the client to answer questions yourself. If our discussion naturally concludes or if I don't have any further inquiries, feel free to politely close the conversation. Remember, you're the therapist, and I'm the client – I'll provide the responses. Looking forward to our conversation!''')    
        conversation_para = conversation_para.format(depression_grade)
        conversation_history = (''' ''')
        response = ('''      Thank you for your participant! I am calculating the test score......''')
       
    # Print the response
    print(f'{response}')   
    
    read_text_ms(text = response[len(AI_NAME)+1:])


    chat_log_file = "chat_log.txt"
    

    if not os.path.exists(chat_log_file):
        with open(chat_log_file, "w"):
            pass
    

    with open(chat_log_file, "a") as file:
        file.write(conversation_history)

