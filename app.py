import io
import os

os.system("wget -P hubert/ https://huggingface.co/spaces/innnky/nanami/resolve/main/checkpoint_best_legacy_500.pt")
import gradio as gr
import librosa
import numpy as np
import soundfile
from inference.infer_tool import Svc
import logging

logging.getLogger('numba').setLevel(logging.WARNING)
logging.getLogger('markdown_it').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)

model = Svc("logs/44k/G_140000.pth", "configs/config.json", cluster_model_path="logs/44k/kmeans_10000.pt")



def vc_fn(sid, input_audio, vc_transform, auto_f0,cluster_ratio, noise_scale):
    if input_audio is None:
        return "You need to upload an audio", None
    sampling_rate, audio = input_audio
    # print(audio.shape,sampling_rate)
    duration = audio.shape[0] / sampling_rate
    if duration > 45:
        return "请上传小于45s的音频，需要转换长音频请本地进行转换", None
    audio = (audio / np.iinfo(audio.dtype).max).astype(np.float32)
    if len(audio.shape) > 1:
        audio = librosa.to_mono(audio.transpose(1, 0))
    if sampling_rate != 16000:
        audio = librosa.resample(audio, orig_sr=sampling_rate, target_sr=16000)
    print(audio.shape)
    out_wav_path = "temp.wav"
    soundfile.write(out_wav_path, audio, 16000, format="wav")
    print( cluster_ratio, auto_f0, noise_scale)
    out_audio, out_sr = model.infer(sid, vc_transform, out_wav_path,
                                   cluster_infer_ratio=cluster_ratio,
                                   auto_predict_f0=auto_f0,
                                   noice_scale=noise_scale
                                   )
    return "Success", (44100, out_audio.numpy())


app = gr.Blocks()
with app:
    with gr.Tabs():
        with gr.TabItem("Basic"):
            gr.Markdown(value="""
                SoVITS 4.0 在线 demo，基于 https://github.com/innnky/so-vits-svc/tree/4.0

                此 demo 为预训练底模在线 demo，使用数据：明前奶绿
                """)
            spks = list(model.spk2id.keys())
            sid = gr.Dropdown(label="音色", choices=["mqnl-covers-v3"], value="mqnl-covers-v3")
            vc_input3 = gr.Audio(label="上传音频（长度小于45秒）")
            vc_transform = gr.Number(label="变调（整数，可以正负，半音数量，升高八度就是12）", value=0)
            cluster_ratio = gr.Number(label="聚类模型混合比例，0-1之间，默认为0不启用聚类，能提升音色相似度，但会导致咬字下降（如果使用建议0.5左右）", value=0)
            auto_f0 = gr.Checkbox(label="自动f0预测，配合聚类模型f0预测效果更好,会导致变调功能失效（仅限转换语音，歌声不要勾选此项会究极跑调）", value=False)
            noise_scale = gr.Number(label="noise_scale 建议不要动，会影响音质，玄学参数", value=0.4)
            vc_submit = gr.Button("转换", variant="primary")
            vc_output1 = gr.Textbox(label="Output Message")
            vc_output2 = gr.Audio(label="Output Audio")
        vc_submit.click(vc_fn, [sid, vc_input3, vc_transform,auto_f0,cluster_ratio, noise_scale], [vc_output1, vc_output2])

    app.launch()
