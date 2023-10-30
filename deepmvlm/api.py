import torch
from torch.utils.model_zoo import load_url

from deepmvlm.model import MVLMModel
from deepmvlm.render3d import Render3D
from deepmvlm.predict2d import Predict2D

models_urls = {
    'MVLMModel_DTU3D-RGB':
        'https://shapeml.compute.dtu.dk/Deep-MVLM/models/MVLMModel_DTU3D_RGB_07092019_only_state_dict-c0255a70.pth',
    'MVLMModel_DTU3D-depth':
        'https://shapeml.compute.dtu.dk/Deep-MVLM/models/MVLMModel_DTU3D_Depth_19092019_only_state_dict-95b89b63.pth',
    'MVLMModel_DTU3D-geometry':
        'https://shapeml.compute.dtu.dk/Deep-MVLM/models/MVLMModel_DTU3D_geometry_only_state_dict-41851074.pth',
    'MVLMModel_DTU3D-geometry+depth':
        'https://shapeml.compute.dtu.dk/Deep-MVLM/models/MVLMModel_DTU3D_geometry+depth_20102019_15epoch_only_state_dict-73b20e31.pth',
    'MVLMModel_DTU3D-RGB+depth':
        'https://shapeml.compute.dtu.dk/Deep-MVLM/models/MVLMModel_DTU3D_RGB+depth_20092019_only_state_dict-e3c12463a9.pth'
}

class DeepMVLM:
    def __init__(self, config):
        self.config = config
        self.device, self.model = self._get_device_and_load_model_from_url()

    def _get_device_and_load_model_from_url(self):
        print('Initialising model')
        image_channels = self.config['image_channels']
        model = MVLMModel(image_channels=image_channels)

        print('Getting device')
        device, device_ids = self._prepare_device(self.config['n_gpu'])#####

        print('Loading checkpoint')
        model_dir = 'deepmvlm/models/'
        model_name = 'MVLMModel_DTU3D'
        name_channels = model_name + '-' + image_channels
        check_point_name = models_urls[name_channels]
        checkpoint = load_url(check_point_name, model_dir, map_location=device)

        if len(device_ids) > 1:
            model = torch.nn.DataParallel(model, device_ids=device_ids)

        model.load_state_dict(checkpoint)
        model = model.to(device)
        model.eval()
        return device, model
    
    def _prepare_device(self, n_gpu_use):
        n_gpu = torch.cuda.device_count()
        if n_gpu_use > 0 and n_gpu == 0:
            print("Warning: There\'s no GPU available on this machine,"
                                "prediction will be performed on CPU.")
            n_gpu_use = 0
        if n_gpu_use > n_gpu:
            print("Warning: The number of GPU\'s configured to use is {}, but only {} are available "
                                "on this machine.".format(n_gpu_use, n_gpu))
            n_gpu_use = n_gpu
        if n_gpu_use > 0 and torch.cuda.is_available() \
                and (torch.cuda.get_device_capability()[0] * 10 + torch.cuda.get_device_capability()[1] < 35):
            print("Warning: The GPU has lower CUDA capabilities than the required 3.5 - using CPU")
            n_gpu_use = 0
        device = torch.device('cuda:0' if n_gpu_use > 0 else 'cpu')
        list_ids = list(range(n_gpu_use))
        return device, list_ids
    
    def predict(self, file_name):
        render_3d = Render3D(self.config)
        image_stack, transform_stack = render_3d.render_3d_file(file_name)
        
        predict_2d = Predict2D(self.config, self.model, self.device)
        heatmap_maxima = predict_2d.predict_heatmaps_from_images(image_stack)

        print(heatmap_maxima.shape)