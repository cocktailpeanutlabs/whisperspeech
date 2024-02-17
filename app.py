import gradio as gr
import io
import os
import re
import torch
import torchaudio
from pathlib import Path
from whisperspeech.pipeline import Pipeline

text_examples = [
    ["This is the first demo of Whisper Speech, a fully open source text-to-speech model trained by Collabora and Lion on the Juwels supercomputer.", None],
    ["World War II or the Second World War was a global conflict that lasted from 1939 to 1945. The vast majority of the world's countries, including all the great powers, fought as part of two opposing military alliances: the Allies and the Axis.", "https://upload.wikimedia.org/wikipedia/commons/7/75/Winston_Churchill_-_Be_Ye_Men_of_Valour.ogg"],
    ["<pl>To jest pierwszy test wielojęzycznego <en>Whisper Speech <pl>, modelu zamieniającego tekst na mowę, który Collabora i Laion nauczyli na superkomputerze <en>Jewels.", None],
    ["<en> WhisperSpeech is an Open Source library that helps you convert text to speech. <pl>Teraz także po Polsku! <en>I think I just tried saying \"now also in Polish\", don't judge me...", None],
    # ["<de> WhisperSpeech is multi-lingual <es> y puede cambiar de idioma <hi> मध्य वाक्य में"],
    ["<pl>To jest pierwszy test naszego modelu. Pozdrawiamy serdecznie.", None],
    # ["<en> The big difference between Europe <fr> et les Etats Unis <pl> jest to, że mamy tak wiele języków <uk> тут, в Європі"]
]

def parse_multilingual_text(input_text):
    pattern = r"(?:<(\w+)>)|([^<]+)"
    cur_lang = 'en'
    segments = []
    for i, (lang, txt) in enumerate(re.findall(pattern, input_text)):
        if lang: cur_lang = lang
        else: segments.append((cur_lang, f"  {txt}  ")) # add spaces to give it some time to switch languages
    if not segments: return [("en", "")]
    return segments

def generate_audio(pipe, segments, speaker, speaker_url, cps=14):
    if isinstance(speaker, (str, Path)): speaker = pipe.extract_spk_emb(speaker)
    elif speaker_url: speaker = pipe.extract_spk_emb(speaker_url)
    else: speaker = pipe.default_speaker
    langs, texts = [list(x) for x in zip(*segments)]
    print(texts, langs)
    stoks = pipe.t2s.generate(texts, cps=cps, lang=langs)[0]
    atoks = pipe.s2a.generate(stoks, speaker.unsqueeze(0))
    audio = pipe.vocoder.decode(atoks.to("cpu")) # <-- `atoks` needs to be on the CPU because the torch ops within vocoder aren't yet MPS compatible
    return audio


def whisper_speech_demo(multilingual_text, speaker_audio=None, speaker_url="", cps=14):
    if len(multilingual_text) == 0:
        raise gr.Error("Please enter some text for me to speak!")

    segments = parse_multilingual_text(multilingual_text)

    audio = generate_audio(pipe, segments, speaker_audio, speaker_url, cps)

    return (24000, audio.T.numpy())

    # Did not work for me in Safari:
    # mp3 = io.BytesIO()
    # torchaudio.save(mp3, audio, 24000, format='mp3')
    # return mp3.getvalue()

#pipe = Pipeline(torch_compile=not DEVEL)
pipe = Pipeline()
# warmup will come from regenerating the examples

with gr.Blocks() as demo:
    with gr.Row(equal_height=True):
        with gr.Column(scale=2):
            text_input = gr.Textbox(label="Enter multilingual text💬📝",
                                    value=text_examples[0][0],
                                    info="You can use `<en>` for English and `<pl>` for Polish, see examples below.")
            cps = gr.Slider(value=14, minimum=10, maximum=15, step=.25,
                            label="Tempo (in characters per second)")
            with gr.Row(equal_height=True):
                speaker_input = gr.Audio(label="Upload or Record Speaker Audio (optional)🌬️💬", 
                                     sources=["upload", "microphone"],
                                     type='filepath')
                url_input = gr.Textbox(label="alternatively, you can paste in an audio file URL:")
            gr.Markdown("  \n  ") # fixes the bottom overflow from Audio
            generate_button = gr.Button("Try Collabora's WhisperSpeech🌟")
        with gr.Column(scale=1):
            output_audio = gr.Audio(label="WhisperSpeech says…")

    with gr.Column():
        gr.Markdown("### Try these examples to get started !🌟🌬️")
        gr.Examples(
            examples=text_examples,
            inputs=[text_input, url_input],
            outputs=[output_audio],
            fn=whisper_speech_demo
        )

    generate_button.click(whisper_speech_demo, inputs=[text_input, speaker_input, url_input, cps], outputs=output_audio)

demo.launch()

