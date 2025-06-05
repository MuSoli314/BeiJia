# For prerequisites running the following sample, visit https://help.aliyun.com/document_detail/xxxxx.html

import os
import requests
from http import HTTPStatus

import dashscope
from dashscope.audio.asr import *

# 若没有将API Key配置到环境变量中，需将your-api-key替换为自己的API Key
# dashscope.api_key = "your-api-key"

# r = requests.get(
#     "https://dashscope.oss-cn-beijing.aliyuncs.com/samples/audio/paraformer/hello_world_female2.wav"
# )
# with open("asr_example.wav", "wb") as f:
#     f.write(r.content)


# class Callback(TranslationRecognizerCallback):
#     def on_open(self) -> None:
#         print("TranslationRecognizerCallback open.")

#     def on_close(self) -> None:
#         print("TranslationRecognizerCallback close.")

#     def on_event(
#             self,
#             request_id,
#             transcription_result: TranscriptionResult,
#             translation_result: TranslationResult,
#             usage,
#     ) -> None:
#         print("request id: ", request_id)
#         print("usage: ", usage)
#         if translation_result is not None:
#             print(
#                 "translation_languages: ",
#                 translation_result.get_language_list(),
#             )
#             english_translation = translation_result.get_translation("en")
#             print("sentence id: ", english_translation.sentence_id)
#             print("translate to english: ", english_translation.text)
#         if transcription_result is not None:
#             print("sentence id: ", transcription_result.sentence_id)
#             print("transcription: ", transcription_result.text)

#     def on_error(self, message) -> None:
#         print('error: {}'.format(message))

#     def on_complete(self) -> None:
#         print('TranslationRecognizerCallback complete')


# callback = Callback()

# translator = TranslationRecognizerChat(
#     model="gummy-chat-v1",
#     format="wav",
#     sample_rate=16000,
#     callback=callback,
# )

# translator.start()

# try:
#     audio_data: bytes = None
#     f = open("data/output.wav", 'rb')
#     if os.path.getsize("data/output.wav"):
#         audio_data = f.read()
#         if translator.send_audio_frame(audio_data):
#             print("send audio frame success")
#         # while True:
#         #     audio_data = f.read(12800)
#         #     if not audio_data:
#         #         break
#         #     else:
#         #         if translator.send_audio_frame(audio_data):
#         #             print("send audio frame success")
#         #         else:
#         #             print("sentence end, stop sending")
#         #             break
#     else:
#         raise Exception(
#             'The supplied file was empty (zero bytes long)')
#     f.close()
# except Exception as e:
#     raise e

# translator.stop()

translator = TranslationRecognizerRealtime(
    model="gummy-realtime-v1",
    format="wav",
    sample_rate=16000,
    translation_target_languages=["en"],
    translation_enabled=True,
    callback=None,
)
result = translator.call("data/output.wav")
if not result.error_message:
    print("request id: ", result.request_id)
    print("transcription: ")
    for transcription_result in result.transcription_result_list:
        print(transcription_result.text)
    print("translation[en]: ")

    for translation_result in result.translation_result_list:
        print(translation_result.get_translation('en').text)
else:
    print("Error: ", result.error_message)