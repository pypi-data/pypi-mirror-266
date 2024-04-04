from optimum.intel import OVModelForSequenceClassification, OVWeightQuantizationConfig
from functools import wraps

class ModelLoader:
    def __init__(self, model_id):
        self.model_id = model_id
        self.quantization_config = OVWeightQuantizationConfig(bits=8, ratio=1.0)
        
    def faster_inference(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Load the model using OVModelForSequenceClassification
            model = OVModelForSequenceClassification.from_pretrained(self.model_id, export=True, compile=True, quantization_config=self.quantization_config)
            return model
        return wrapper
    
    def load_model(self):
        # Define the model loading function
        @self.faster_inference
        def inner_load_model():
            pass
        return inner_load_model()