from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from marker.config.parser import ConfigParser

config = {
    "output_format": "markdown",
    "output_dir":"output",
    "use_llm": True,
    "disable_image_extraction": True,
    "llm_service": "marker.services.openai.OpenAIService",
    "openai_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "openai_model": "qwen-vl-max-latest",
    "openai_api_key": "sk-65417eb6629a4102858a35f3484878e5"
}


config_parser = ConfigParser(config)

converter = PdfConverter(
    config=config_parser.generate_config_dict(),
    artifact_dict=create_model_dict(),
    processor_list=config_parser.get_processors(),
    renderer=config_parser.get_renderer(),
    llm_service=config_parser.get_llm_service()
)

rendered = converter("/Users/darkringsystem/PycharmProjects/autogenTest/avatr.png")
text, _, images = text_from_rendered(rendered)
for k,v in images.items():
    text.replace(f"![]({k})","描述信息")
print(text)
print(images)