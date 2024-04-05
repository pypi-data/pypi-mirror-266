from signapse.models_utils import create_model
import pickle5 as pickle
import gzip

class CROP_GAN():
    def __init__(self, args):
        super(CROP_GAN,self).__init__()
        self.args=args   
        
    def load_zipped_pickle(self,filename):
        with gzip.open(filename, 'rb') as f:
            loaded_object = pickle.load(f)
            return loaded_object

    #def get_CROP_GAN_model(self,opt,ckpt_path,base_tensor_path,face_points_path):
    def get_CROP_GAN_model(self):
        # Create the Pytorch model
        GAN_model = create_model(self.args.opt, ckpt=self.args.ckpt_path)
        # Load the zipped base tensor path (required for appearance)
        if self.args.opt.base_style:
            GAN_model.base_tensor = self.load_zipped_pickle(self.args.base_tensor_path)
        GAN_model.face_points = self.load_zipped_pickle(self.args.face_points_path)
        GAN_model.opt = self.args.opt
        # Determine whether to use cuda or not - given argument
        GAN_model.cuda_device = "cuda" if self.args.opt.cuda else "cpu"
        print(f"Cuda device: {GAN_model.cuda_device}")

        # Return the Pytorch model and MediaPipe Holistic model
        return GAN_model
