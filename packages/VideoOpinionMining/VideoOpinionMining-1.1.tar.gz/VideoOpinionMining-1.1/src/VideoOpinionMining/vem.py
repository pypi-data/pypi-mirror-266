import pandas as pd
import numpy as np
import math
import gdown
import matplotlib.pyplot as plt
import whisperx
import gc
import transformers
import webvtt
import os
import ffmpeg
import random
import logging
import torch
import torch.nn as nn
import torch.nn.functional as F
from moviepy.editor import *
import torchaudio
from sklearn.neighbors import kneighbors_graph
import networkx as nx
import cv2
import glob
import re
import math
from sentence_transformers import SentenceTransformer
from deepface import DeepFace
from src.models import Wav2Vec2ForSpeechClassification, HubertForSpeechClassification
from transformers import AutoConfig, Wav2Vec2FeatureExtractor
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from transformers import RobertaTokenizerFast, BertForSequenceClassification


class VEMProcessor:
    """
        Here is the main class that makes this module, VEMProcessor
    """
    def __init__(self):
        """
            To initialize it, pass the video fto be analyzed as an argument
        """
        self.segmenter = VideoSegmenter()

        self.opinion_model_transc = OpinionExtractionModel()
        self.opinion_model_transc.set_model(modality = "transcript")

        self.opinion_model_audio = OpinionExtractionModel()
        self.opinion_model_audio.set_model(modality = "audio")

        self.opinion_model_video = OpinionExtractionModel()
        self.opinion_model_video.set_model(modality = "video")

        self.opinion_extractor_transc = OpinionExtractor([],self.opinion_model_transc)
        self.opinion_extractor_audio = OpinionExtractor([],self.opinion_model_audio)
        self.opinion_extractor_video = OpinionExtractor([],self.opinion_model_video)

        self.multimodal_extractor = MultimodalOpinionExtractor([])

        self.emotion_map_generator = EmotionMapGenerator([])  # Adjust segment_block_size as needed

    def process_video(self, video_file, segment_block_size = 10):
        """
          Use this to run the models for all the modalities(transcript, audio, video and multimodal) and generate the heatmaps.

          Args:
            **video_file (mp4)**: video to be analized.
            **segment_block_size (int)**: size of the block used in each frame of the heatmap.

          Return:
            Nothing.

          In case you also want the dataframes generated with all the emotions, object_of_class.segmented_video contains it.

        """
        # Step 1: Segment the video
        self.segmented_video = self.segmenter.segment_video(video_file)
        
        # Step 2: Extract opinions
        self.opinion_extractor_transc = OpinionExtractor([],self.opinion_model_transc)
        self.opinion_extractor_audio = OpinionExtractor([],self.opinion_model_audio)
        self.opinion_extractor_video = OpinionExtractor([],self.opinion_model_video)

        self.opinion_extractor_transc.segmenter_result = self.segmented_video
        self.opinion_extractor_audio.segmenter_result = self.segmented_video
        self.opinion_extractor_video.segmenter_result = self.segmented_video
        
        self.opinion_extractor_transc.extract_opinions()
        self.opinion_extractor_audio.extract_opinions()
        self.opinion_extractor_video.extract_opinions()
        
        # Step 3: Extract multimodal opinions
        self.multimodal_extractor.segmented_with_emotion = self.segmented_video
        self.multimodal_extractor.extract_multimodal_opinions()

        # Step 4: Generate emotion map
        self.emotion_map_generator.segments_with_emotion = self.segmented_video
        self.emotion_map_generator.graph = self.multimodal_extractor.G_multimodal

        self.emotion_map_generator.generate_emotion_map("transcript",segment_block_size)
        self.emotion_map_generator.generate_emotion_map("audio",segment_block_size)
        self.emotion_map_generator.generate_emotion_map("video",segment_block_size)
        self.emotion_map_generator.generate_emotion_map("multimodal",segment_block_size)

class VideoSegmenter:
    """
        Class responsible for extracting the transcription from the video, segmenting it in phrases with the
        timestamps and name of the parts contained in a dataframe
    """
    def __init__(self):
        logging.basicConfig(filename="newfile.log",
        format='%(asctime)s %(message)s',filemode='w')
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        pass

    def segment_video(self, video_file):
        """
        Receives an MP4 file and returns a list of video segments.
        Each segment is represented as a series in a dataframe: (start_time, end_time, transcript_text, segment_file.mp4)

        Args:
            **video_file (str)**: video to be analyzed.

        Return:
            Dataframe with all the segments.

        """
        os.makedirs(video_file[0:3] + "parts", exist_ok=True)

        # Segment the video and extract transcript for each segment
        # Store each segment with its start time, end time, transcript, and save it as a new file
        self.logger.info("Transcripting the video")
        dataframe = transcript(video_file)

        self.logger.info("Done")

        video = VideoFileClip(video_file)
        maximo = dataframe.shape[0]
        names = []
        self.logger.info("Segmenting the video")

        for i in range(0, maximo):
            #Usando os timestamps da transcricao, corto o video separando aproximadamente cada frase
            startPos = dataframe[0][i]
            endPos = dataframe[1][i]

            clip = video.subclip(startPos, endPos)

            part_name = video_file[0:3] + "parts/part_"+str(i)+".mp4"

            names.append(part_name)

            clip.write_videofile(part_name, codec='libx264', fps=video.fps)

        video.close()

        dataframe['segment_file'] = names
        dataframe.rename(columns={0:"Start",1:"End",2:"Transcript"})
        self.logger.info("Done")

        return dataframe
        pass
#Criar 3, um para cada categoria
class OpinionExtractionModel:
    """
        Class to declare and store the models utilized for the transcript, audio and video classification
    """
    def __init__(self):
        logging.basicConfig(filename="newfile.log",
        format='%(asctime)s %(message)s',filemode='w')
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        pass
    # Como só o textual é personalizável por enquanto, só há argumentos para mudar ele
    def set_model(self, modality, encoder_text = None, emot_pipe = None):
        """
        Start the model to be utilized in each modality. In order to modify the video and audio, manual changes have to be made
        to this code, while the transcript model can be easily changed passing a pipeline and an encoder

        Args:
            **modality (str)**: modality that the model will analyze.

            **emot_pipe (pipeline)**: pass a pipeline in order to change the model being used to classify the emotions.

            **encoder_text (encoder)**: pass the encoder used in the pipeline passed.

        Return:
            Dataframe with all the segments.
        """
        self.modality = modality

        if(modality == "transcript"):
          self.logger.info("Setting up the transcript model")
          tokenizer_tr = AutoTokenizer.from_pretrained("unicamp-dl/translation-pt-en-t5")

          translator = AutoModelForSeq2SeqLM.from_pretrained("unicamp-dl/translation-pt-en-t5")

          self.transl_pipeline = pipeline('text2text-generation', model=translator, tokenizer=tokenizer_tr)

          if emot_pipe == None:
            self.emot_pipe = pipeline('sentiment-analysis',
                              model="bhadresh-savani/bert-base-go-emotion",
                              return_all_scores=True)
          self.encoder_text = encoder_text or SentenceTransformer("bhadresh-savani/bert-base-go-emotion")
          self.logger.info("Done")

        elif(modality == "audio"):
          self.logger.info("Setting up the audio model")
          model_name_or_path = "Rajaram1996/Hubert_emotion"

          self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
          self.config = AutoConfig.from_pretrained(model_name_or_path)
          self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_name_or_path)
          self.sampling_rate = self.feature_extractor.sampling_rate


          self.audio_model = HubertForSpeechClassification.from_pretrained(model_name_or_path, output_hidden_states=True).to(self.device)
          self.logger.info("Done")

        elif(modality == "video"):
          self.logger.info("Setting up the video model")
          self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
          self.logger.info("Done")

    def predict(self,instance_segment):
        """
        Apply the model instanciated to a single sentence

        Args:
            **instance_segment (series)**: sentence to be analyzed.

        Return:
            **emot(str)**: emotion with the highest score.

            **scor(float)**: highest score.

            **embeddings(List)**: embeddings of the segmente analyzed.
        """
        if(self.modality == "transcript"):

          translation = traduz(instance_segment[2], self.transl_pipeline)

          resp = emocao_provavel(translation, self.emot_pipe)

          text_embeddings = encoder_text_adj(translation,self.encoder_text)

          return resp[0], resp[1], text_embeddings

        elif(self.modality == "audio"):

          part_name = instance_segment["segment_file"]

          #Aplico o modelo
          temp = predict(part_name,self.sampling_rate, self.device, self.config, self.feature_extractor, self.audio_model)
          embeddings = (encoder_audio(part_name,self.sampling_rate, self.device, self.feature_extractor, self.audio_model))

          max_values = max(temp, key=lambda x:x['Score'])

          # A cada frase, atribuo a emocao mais provavel e sua probabilidade
          max_emotion = (max_values['Emotion'])
          max_emotion = max_emotion[(max_emotion.find('_')+ 1):]
          if max_emotion == 'sad':
            max_emotion = 'sadness'
          elif max_emotion == 'angry':
            max_emotion = 'anger'
          elif max_emotion == 'happy':
            max_emotion = 'joy'
          emot = max_emotion

          max_score = (max_values['Score'])
          scor = (float(max_score.replace("%","",1))/ 100)

          return emot, scor, embeddings

        elif(self.modality == "video"):
          # This n_frames could be passed via parameters to increase the number of frames of the video, increasing the time to run though.
          n_frames = 5

          video = VideoFileClip(instance_segment["segment_file"])
          clip = video.set_fps(n_frames)

          frames = clip.iter_frames()

          total = {}
          quant = 0

          for frame in frames:

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            #Se não tiver face, essa função uma tupla vazia

            if(len(faces) > 0):
              try:
                #Se não tiver face, essa função retorna uma excecao
                objs = DeepFace.analyze(frame, actions = ['emotion'])
                if(total == {}):
                  total = objs[0]['emotion']
                else:
                  for key, value in objs[0]['emotion'].items():
                    total[key] += value
                quant += 1
              except ValueError:
                continue
          for key, value in total.items():
            total[key] = value / quant
          if(quant == 0):
            emot = "no_face"
            scor = 0
          else:
            max_prob = max(total.values())
            max_emo = {i for i in total if total[i] == max_prob}

            #Max emo eh um set, converto para o formato certo em str
            max_emo = str(max_emo)
            max_emo = str(max_emo[2: -2])
            max_emo

            if max_emo == 'sad':
              max_emo = 'sadness'
            elif max_emo == 'angry':
              max_emo = 'anger'
            elif max_emo == 'happy':
              max_emo = 'joy'
            emot = max_emo
            scor = max_prob/(quant * 100)

          return emot, scor, None

#uso dos modelos acima
class OpinionExtractor:
    """
        Class responsible for applying the models to all the segments of the video
        Args:
            **segmenter_result (dataframe)**: sentences to be analyzed.

            **opinion_model (OpinionExtractionModel)**: Model responsible for the analysis.
    """
    def __init__(self, segmenter_result, opinion_model):
        self.segmenter_result = segmenter_result
        self.opinion_model = opinion_model

        logging.basicConfig(filename="newfile.log",
        format='%(asctime)s %(message)s',filemode='w')
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

    def extract_opinions(self):
        """
        Extract opinions from the segmented video segments.
        Add identified emotion to each segment using the opinion extraction model.
        """
        # Iterate through each segment, extract emotion using the model, and add it to the segment
        emot = []
        scor = []
        embeddings = []

        self.logger.info("Extracting opinion for the " + self.opinion_model.modality)

        for  i in range(self.segmenter_result.shape[0]):
          emo, sco, emb = self.opinion_model.predict(self.segmenter_result.iloc[i])
          emot.append(emo)
          scor.append(sco)
          embeddings.append(emb)
        self.segmenter_result[self.opinion_model.modality + '_label'] = emot
        self.segmenter_result[self.opinion_model.modality + '_prob'] = scor
        self.segmenter_result[self.opinion_model.modality + '_embeddings'] = embeddings

class MultimodalOpinionExtractor:
    """
        Class responsible for applying the multimodal model to all the segments of the video after
        the audio and transcript classification have already been done
        Args:
            **segmented_with_emotion (dataframe)**: sentences to be analyzed with the audio and 
            transcript classification already been done.
            
    """
    def __init__(self, segmented_with_emotion):
        self.segmented_with_emotion = segmented_with_emotion
        url1 = 'https://drive.google.com/uc?id=1yJBHU8Zl4MuoQfJqkPgVDwJfYRJDPUAH'
        output = 'emotions_coord.xlsx'
        gdown.download(url1, output, quiet=False)
        self.emotions_coord = pd.read_excel(output)

    def extract_multimodal_opinions(self):
        """
        Extract multimodal opinions from the segmented video segments with already identified emotion.
        Add multimodal emotion to each segment using the opinion extraction model.
        """
        A_text = kneighbors_graph(np.array(self.segmented_with_emotion.transcript_embeddings.to_list()), 2, mode='connectivity')
        G_text = nx.Graph(A_text.toarray())

        A_audio = kneighbors_graph(np.array(self.segmented_with_emotion.audio_embeddings.to_list()), 2, mode='connectivity')
        G_audio = nx.Graph(A_audio.toarray())

        self.G_multimodal = nx.Graph()
        for edge in G_text.edges(): self.G_multimodal.add_edge(edge[0],edge[1])
        for edge in G_audio.edges(): self.G_multimodal.add_edge(edge[0],edge[1])

        t = []
        for index,row in self.segmented_with_emotion.iterrows():
          df_coord_text = generate_coord(row["transcript_label"],self.emotions_coord)
          coord_text = [float(df_coord_text[0]),float(df_coord_text[1])]
          self.G_multimodal.nodes[index]['text'] = np.array(coord_text)

          df_coord_audio = generate_coord(row["audio_label"],self.emotions_coord)
          coord_audio = [float(df_coord_audio[0]),float(df_coord_audio[1])]
          self.G_multimodal.nodes[index]['audio'] = np.array(coord_audio)

          t.append(np.linalg.norm(self.G_multimodal.nodes[index]['audio']-self.G_multimodal.nodes[index]['text']))

        for index,row in self.segmented_with_emotion.iterrows():
          self.G_multimodal.nodes[index]['pseudolabeling'] = 1.0 - (t[index]/np.max(t))

class EmotionMapGenerator:
    """
        Class responsible for generating the heatmaps visualization of the classifications.
        Args:
            **segmented_with_emotion (dataframe)**: sentences to be analyzed with the audio and 
            transcript classification already been done.

            **graph (networkx graph)**: graph generated by the multimodal model
            
    """
    def __init__(self, segments_with_emotion, graph = None):
        self.segments_with_emotion = segments_with_emotion
        self.graph = graph

        url1 = 'https://drive.google.com/uc?id=1yJBHU8Zl4MuoQfJqkPgVDwJfYRJDPUAH'
        output = 'emotions_coord.xlsx'
        gdown.download(url1, output, quiet=False)
        self.emotions_coord = pd.read_excel(output)

        logging.basicConfig(filename="newfile.log",
        format='%(asctime)s %(message)s',filemode='w')
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

    def generate_emotion_map(self, modality, segment_block_size = 5):
        # Divide segments into blocks
        # Calculate emotion distribution for each block
        # Generate emotion wheel for each block
        # Create a video showing the evolution of emotion map over time
        """
        Generate an emotion wheel for each block of segments in the format of mp4 and png.
        Args:
            **modality (string)**: for which modality is the heatmap to be created (the opinion excration of the
            respective modality have to be done befor)

            **segment_block_size (int)**: how many phrases are shown in the same frame of the heatmap.
        """
        if modality == 'multimodal':
          x = []
          y = []
          x_img = []
          y_img = []
          GCP(self.graph,mi=1,audio_weight=0.4, text_weight=0.6,max_iter=30)
          for index in self.segments_with_emotion.index:
            v = self.graph.nodes[index]['f']
            x.append(v[0])
            y.append(v[1])
            if (np.abs(v[0]) > 0.1 or np.abs(v[1]) > 0.1):
              x_img.append(v[0])
              y_img.append(v[1])
        else:
          df = get_labels(self.segments_with_emotion, modality)

          label = modality + '_label'

          df.loc[df[label] == 'no_face', [label]] = 'neutral'
          resp = list(df[label].apply(generate_coord, args = (self.emotions_coord,)))
          temp = pd.DataFrame.from_records(resp, columns=['x', 'y'])

          df = pd.concat([df, temp], axis=1)

          array_x = df['x'].to_numpy()
          x = array_x.tolist()
          array_y = df['y'].to_numpy()
          y = array_y.tolist()

          dfimage = df[df[label]!='neutral']
          dfimage = dfimage.reset_index(drop=True)

          array_x_img = dfimage['x'].to_numpy()
          x_img = array_x_img.tolist()
          array_y_img = dfimage['y'].to_numpy()
          y_img = array_y_img.tolist()


        vid_name = self.segments_with_emotion["segment_file"][0]
        vid_name = vid_name[0:3]
        os.makedirs("tempjpgs", exist_ok=True)
        os.makedirs(vid_name + "heatmaps", exist_ok=True)
        
        plot_heatmap(x_img, y_img, self.emotions_coord, modality, vid_name)


        id_ini = 0
        id_fim = segment_block_size
        atual = 1
        quant = self.segments_with_emotion.shape[0]
        tam = quant / segment_block_size

        for i in range(math.ceil(tam)):
            x_temp = np.array(x[id_ini: id_fim])
            y_temp = np.array(y[id_ini: id_fim])

            if all(val == 0 for val in x_temp) and all(val == 0 for val in y_temp):
              x_temp = np.array([0])
              y_temp = np.array([0])
            else:
              x_temp = [i for i,j in zip(x_temp,y_temp) if (i != 0 and j != 0)]
              y_temp = [j for i,j in zip(x[id_ini: id_fim],y_temp) if (i != 0 and j != 0)]

            plt.title("Emotions from " + str(id_ini) + " to " + str(id_fim-1) + " block")
            plt.savefig("tempjpgs/output" + str(atual) + ".jpg")
            plt.close()

            id_ini += segment_block_size
            id_fim += segment_block_size
            atual += 1
            if(id_fim > quant):
              id_fim = quant

        img_array = []
        for filename in sorted(glob.glob('tempjpgs/*.jpg') , key=numericalSort):
            img = cv2.imread(filename)
            height, width, layers = img.shape
            size = (width,height)
            img_array.append(img)
            os.remove(filename)

        os.rmdir("tempjpgs")

        rate = 1
        out = cv2.VideoWriter(vid_name +"heatmaps/"+ modality + '_heatmap.mp4',cv2.VideoWriter_fourcc(*'XVID'), rate, size)

        for i in range(len(img_array)):
          for j in range(2):
            out.write(img_array[i])

        out.release()

        myvideo = VideoFileClip(vid_name + "heatmaps/"+modality + '_heatmap.mp4')
        self.logger.info("Video created")

        return ipython_display(myvideo)

#Função para extrair do dicionario retornado pelo goemotions a emoção mais provável e sua probabilidade
def emocao_provavel(frase, emot_pipe):
    emotion_labels = emot_pipe(frase)

    maximo = emotion_labels[0][0]["score"]
    emocao = emotion_labels[0][0]["label"]

    for dict in emotion_labels[0]:
        if dict["score"] > maximo:
          maximo = dict["score"]
          emocao = dict["label"]

    return emocao, maximo

#Funcoes auxiliares para a geração do heatmap

def get_labels(dataframe, modality = "all"):
    """
      Returns the dataframe with all phrases, classificated or not. With
      modality, you can select to show only the classification for the
      modality selected in case of multiple classifications. Doesn't work
      for multimodal since there is no classification
    """
    if(modality == "transcript"):
      return dataframe[[0,1,2,'transcript_label','transcript_prob']]
    elif(modality == "audio"):
      return dataframe[[0,1,2,'audio_label','audio_prob']]
    elif(modality == "video"):
      return dataframe[[0,1,2,'video_label','video_prob']]
    return dataframe

numbers = re.compile(r"(\d+)")
def numericalSort(value):
  parts = numbers.split(value)
  parts[1::2] = map(int, parts[1::2])
  return parts
def generate_coord(label, coords):
    index = coords.loc[coords['Emotion'] == label].index[0]
    x = coords.iloc[index]['X']
    y = coords.iloc[index]['Y']
    return (x,y)
def kde_quartic(d,h):
    dn=d/h
    P=(15/16)*(1-dn**2)**2
    return P
def plot_heatmap(x, y, emotions_coord, modality, vid_name):
    #Definindo tamanho do grid e do raio(h)
    grid_size=0.02
    h=0.5

    #Tomando valores de máximos e mínimos de X e Y.
    x_min=-1
    x_max=1
    y_min=-1
    y_max=1

    #Construindo grid
    x_grid=np.arange(x_min-h,x_max+h,grid_size)
    y_grid=np.arange(y_min-h,y_max+h,grid_size)
    x_mesh,y_mesh=np.meshgrid(x_grid,y_grid)

    #Determinando ponto central do grid
    xc=x_mesh+(grid_size/2)
    yc=y_mesh+(grid_size/2)

    intensity_list=[]
    for j in range(len(xc)):
        intensity_row=[]
        for k in range(len(xc[0])):
            kde_value_list=[]
            for i in range(len(x)):
                #Calculando distância
                d=math.sqrt((xc[j][k]-x[i])**2+(yc[j][k]-y[i])**2)
                if d<=h:
                    p=kde_quartic(d,h)
                else:
                    p=0
                kde_value_list.append(p)
            #Soma os valores de intensidade
            p_total=sum(kde_value_list)
            intensity_row.append(p_total)
        intensity_list.append(intensity_row)

    #Saída do Heatmap
    plt.figure(figsize=(7,7))

    intensity=np.array(intensity_list)
    plt.pcolormesh(x_mesh,y_mesh,intensity,cmap='YlOrRd') #https://matplotlib.org/stable/tutorials/colors/colormaps.html


    #fig, ax = plt.subplots()

    x_emo = emotions_coord.X.to_list()
    y_emo = emotions_coord.Y.to_list()
    plt.scatter(x_emo, y_emo)


    for i, row in emotions_coord.iterrows():
        plt.annotate(row['Emotion'], (x_emo[i], y_emo[i]))

    plt.xlim(-1, 1)
    plt.ylim(-1,1)

    ax = plt.gca()
    ax.add_patch(plt.Circle((0, 0), 1, color='black', fill=False))
    plt.axvline(x = 0, color = 'black', label = 'Arousal')
    plt.axhline(y = 0, color = 'black', label = 'Valence')

    #plt.colorbar()

    plt.plot(x,y,'x',color='white')
    plt.savefig(vid_name + "heatmaps/" + modality + "heatmap.png")

#Funcoes auxiliares para a transcricao
def transcript(video, method = "whisperx", min_time = 1):
    """
      Transform the audio of a video into a dataframe with it's phrases in text form separated by time frames
    """
    bashCommand = "whisperx --compute_type float32 --output_format vtt " + video
    os.system(bashCommand)

    dataframe = set_vtt(video.replace("mp4", "vtt"))

    dataframe = dataframe[dataframe.apply(lambda x: time_diff(x[1], x[0]), axis=1) > min_time]
    dataframe.reset_index(inplace = True, drop = True)

    return dataframe

def set_vtt(arquivo):
    """
      Alternate form to load a video dataframe via it's vtt, which can be generated previously with the whisper transcription
    """
    L = []

    for caption in webvtt.read(arquivo):
        L.append([caption.start,caption.end,str(caption.text)])

    dataframe = pd.DataFrame(L)
    return dataframe

def traduz(frase, pten_pipeline):
    """
      Translate the phrases from portuguese to english in order to use the text classification model
    """
    traducao = pten_pipeline(frase)
    traducao = list(traducao[0].values())
    return traducao[0]

def time_diff(fim, init):

      time_fim = to_seconds(fim)
      time_init = to_seconds(init)

      return time_fim - time_init

def speech_file_to_array_fn(path, sampling_rate):
    speech_array, _sampling_rate = torchaudio.load(path)
    resampler = torchaudio.transforms.Resample(_sampling_rate, sampling_rate)
    speech = resampler(speech_array).squeeze().numpy()
    return speech

def encoder_text_adj(sentence, encoder):
    return encoder.encode([sentence])[0]

#Funcoes auxiliares para a funcionalidade audio

def predict(path, sampling_rate, device, config, feature_extractor, model):
    speech = speech_file_to_array_fn(path, sampling_rate)
    inputs = feature_extractor(speech, sampling_rate=sampling_rate, return_tensors="pt", padding=True)
    inputs = {key: inputs[key].to(device) for key in inputs}

    with torch.no_grad():
        logits = model(**inputs).logits

    scores = F.softmax(logits, dim=1).detach().cpu().numpy()[0]
    outputs = [{"Emotion": config.id2label[i], "Score": f"{round(score * 100, 3):.1f}%"} for i, score in
               enumerate(scores)]
    return outputs

    # extrai os embeddings da predição feita
def encoder_audio(path, sampling_rate, device, feature_extractor, model, mean_pool=True):
    speech = speech_file_to_array_fn(path, sampling_rate)
    inputs = feature_extractor(speech, sampling_rate=sampling_rate, return_tensors="pt", padding=True)
    inputs = {key: inputs[key].to(device) for key in inputs}

    with torch.no_grad():
        out = model(**inputs).hidden_states[-1]
        if mean_pool:
            return np.array(torch.mean(out, dim=1).cpu())[0]
        else:
            return np.array(out.cpu())[0]
        
#Funcoes auxiliares para a funcionalidade multimodal
def GCP(G, max_iter=100, audio_weight=0.2, text_weight=0.8, mi=1, min_diff=0.05):

  # inicializando
  L_nodes = []
  for n in G.nodes():
    G.nodes[n]['f'] = np.average([G.nodes[n]['text'],G.nodes[n]['audio']],axis=0,weights=[text_weight, audio_weight])
    L_nodes.append(n)


  for i in range(0,max_iter):
    random.shuffle(L_nodes)

    # propagando
    diff = 0
    for node in L_nodes:

      f_new = np.array([0.0, 0.0])
      count = 0
      for neighbor in G.neighbors(node):
        f_new += G.nodes[neighbor]['f']
        count += 1

      f_new /= count

      f_pseudolabeling = np.average([G.nodes[node]['text'],G.nodes[node]['audio']],axis=0,weights=[text_weight, audio_weight])
      pl = G.nodes[node]['pseudolabeling']*mi
      f_new = f_pseudolabeling*pl + f_new*(1-pl)
      diff += np.linalg.norm(G.nodes[node]['f']-f_new)
      G.nodes[node]['f']=f_new


    print("Iteration #"+str(i+1)+" Q(F)="+str(diff))
    if diff <= min_diff: break

#Funcoes uteis
def to_seconds(horario):

  horario_separado = horario.split(":")
  seconds = 3600*int(horario_separado[0]) + 60*int(horario_separado[1]) + float(horario_separado[2])

  return seconds
