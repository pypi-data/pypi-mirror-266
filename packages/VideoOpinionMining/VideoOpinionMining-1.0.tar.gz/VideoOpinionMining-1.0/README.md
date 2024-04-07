# Video Opinion Mining

Esse projeto consiste na elaboração de um método capaz de extrair emoções em tempo real de um vídeo, organizando-as em um mapa de calor sobre as dimensões de arousal-valence.

Ele contém uma classe principal, VEMProcessor que com um simples comando já classifica o vídeo quanto à opinião extraída das faces presentes no vídeo, do áudio das falas e da transcrição desse áudio, já gerando mapas de calor para as três categorias e um multimodal envolvendo o áudio e a transcrição.

Também possui outras 5 classes que podem ser customizadas para alterar o processo de extração de opiniões ou a geração do mapa de calor.
<ul>
  <li>VideoSegmenter
    <ul>
      <li>Transforma um arquivo mp4 em um dataframe do Pandas contendo 
      cada frase do vídeo, suas timestamps e o segmento do vídeo que contém a frase</li>
    </ul>
  </li>
  <li>OpinionExtractionModel
    <ul>
      <li>Contém os modelos que serão usados para realizar a extração de opinião da trancrição, áudio e vídeo</li>
    </ul>
  </li>
  <li>OpinionExtractor
    <ul>
      <li>Responsável por aplicar os modelos em cada segmento de vídeo</li>
    </ul>
  </li>
  <li>MultimodalOpinionExtractor
    <ul>
      <li>Extrai opiniões multimodais das classificações já realizadas pelo extrator de opinião da transcrição e do áudio</li>
    </ul>
  </li>
  <li>EmotionMapGenerator
    <ul>
      <li>Gera um heatmap com o dataframe desde que ele tenha sido classificado quanto as emoções. Isso pode ser feito para qualquer modalidade</li>
    </ul>
  </li>
</ul>