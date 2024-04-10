import os, gzip, torch, argparse, yaml
import pickle5 as pickle

def load_config(path="configs/default.yaml"):
    with open(path, 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)
    return cfg

# Load the options from a config file
class BaseOptions():
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.initialized = False

    def parse(self,args):
        self.initialized = True
        if not self.initialized:
            self.initialize()
        self.opt = self.parser.parse_args(args=[])
        self.opt.config_path = args.config_path
        # # load the options from the config
        self.load_cfg_options(self.opt)
        self.opt.GPU = args.GPU
        self.opt.gpu_ids = []
        self.opt.cuda = None
        if self.opt.GPU=='cuda':
            self.opt.cuda = self.opt.GPU
            self.opt.gpu_ids = [0]
            torch.cuda.set_device(0)

        return self.opt

    def load_cfg_options(self, opt):

        cfg = load_config(opt.config_path)
        self.opt.cfg = cfg
        self.opt.merge_crops = cfg["data"].get("merge_crops", False)
        self.opt.erusion = cfg["data"].get("erusion", False)
        # Set Resolution - 1024
        self.opt.loadSize = cfg["data"].get("loadSize", 1024)
        # Set input channels of heatmap - 169 for MediaPipe
        self.opt.label_nc = cfg["data"].get("input_nc", 169)
        # Set output channels - Image is just 3
        self.opt.output_nc = cfg["data"].get("output_nc", 3)
        self.opt.base_style = cfg["data"].get("base_style", True)        
        #self.opt.hand_crop_channels = cfg["data"].get("hand_crop_channels", 2)
        
        # Generator stuff
        if "generator" in cfg["model"]:
            self.opt.ngf = cfg["model"]["generator"].get("ngf", 64)
            self.opt.n_downsample_global = cfg["model"]["generator"].get("n_downsample_global", 4)
            self.opt.n_blocks_global = cfg["model"]["generator"].get("n_blocks_global", 9)
            ########## Basheer ############################
            self.opt.controlnet = cfg["model"]["generator"].get("controlnet", False)
            self.opt.control_alpha = cfg["model"]["generator"].get("control_alpha", 0.5)
            self.opt.controlnet_checkout = cfg["model"]["generator"].get("controlnet_checkout", '/home/basheer/Signapse/new/synthetic-signer/Jay/blue_Body_FH_EDGES/GAN_checkpoint.ckpt')
            ########## Basheer ############################

        if "face" in cfg["model"]:
            self.opt.ngf_face = cfg["model"]["face"].get("ngf", 64)
            self.opt.n_downsample_global_face = cfg["model"]["face"].get("n_downsample_global", 4)
            self.opt.n_blocks_global_face = cfg["model"]["face"].get("n_blocks_global", 9)

        self.opt.face_mesh = cfg["data"].get("face_mesh", False)
        self.opt.face_and_body = cfg["model"].get("face_and_body", False)
        self.opt.no_face_landmarks = cfg["model"].get("no_face_landmarks", False)
        self.opt.no_face_input = cfg["model"].get("no_face_input", False)
        self.opt.no_face_output = cfg["model"].get("no_face_output", False)
        self.opt.face_size = cfg["model"].get("face_size", 0.25)
        self.opt.actual_face_size = int(self.opt.loadSize * self.opt.face_size)

        ########## Basheer ############################
        self.opt.N2N = cfg["model"].get("N2N", False)
        self.opt.multi_frames = cfg["model"].get("multi_frames", False)
        self.opt.num_frames = cfg["model"].get("num_frames", 0)       
        self.opt.signer = cfg["data"].get("signer", "")
        self.opt.remove_body_pose = cfg["data"].get("remove_body_pose", False)
        self.opt.remove_hand_pose = cfg["data"].get("remove_hand_pose", False)
        self.opt.remove_face_pose = cfg["data"].get("remove_face_pose", False)
        self.opt.remove_hip_pose = cfg["data"].get("remove_hip_pose", False)
        
        self.opt.sam = cfg["data"].get("sam_pose", True)
        self.opt.skin_crop = cfg["data"].get("skin_crop", False)
        self.opt.hand_crop = cfg["data"].get("hand_crop", False)
        self.opt.face_crop = cfg["data"].get("face_crop", False)
        self.opt.skin_edge = cfg["data"].get("skin_edge", False)
        self.opt.hand_edge = cfg["data"].get("hand_edge", False)
        self.opt.face_edge = cfg["data"].get("face_edge", False)
        self.opt.crop_normalise = cfg["data"].get("crop_normalise", False)
        self.opt.smooth_face_crop = cfg["data"].get("smooth_face_crop", False)
        ########## Basheer ############################
        
        

        self.opt.hand_and_body = cfg["model"].get("hand_and_body", False)
        self.opt.HaB_all_image = cfg["model"].get("HaB_all_image", False)
        if "hand" in cfg["model"]:
            self.opt.ngf_hand = cfg["model"]["hand"].get("ngf", 64)
            self.opt.n_downsample_global_hand = cfg["model"]["hand"].get("n_downsample_global", 4)
            self.opt.n_blocks_global_hand = cfg["model"]["hand"].get("n_blocks_global", 9)
            
def load_zipped_pickle(filename):
    with gzip.open(filename, 'rb') as f:
        loaded_object = pickle.load(f)
        return loaded_object

def get_opt(args):
    if not args.main_path:
        sign_result_queue_url = args.sign_result_queue_url
        organisation_id = args.organisation_id
        args.output_video_path = f"./outputs/"
        args.face_points_path = f"./inputs/Face_Points.pkl"
        args.config_path = f"./{args.signer}/{args.GAN_folder}/GAN_config.yaml"
        args.ckpt_path = f"./{args.signer}/{args.GAN_folder}/GAN_checkpoint.ckpt"
        args.base_tensor_path = f"./inputs/GAN_base_tensor.pkl"
        opt = BaseOptions().parse(args)
        opt.face_points = load_zipped_pickle(args.face_points_path)
        args.opt = opt
    else:
        sign_result_queue_url = args.sign_result_queue_url
        organisation_id = args.organisation_id
        args.output_video_path = f"{args.main_path}/outputs/"
        args.face_points_path = f"{args.main_path}/inputs/Face_Points.pkl"
        args.config_path = f"{args.main_path}/{args.signer}/{args.GAN_folder}/GAN_config.yaml"
        args.ckpt_path = f"{args.main_path}/{args.signer}/{args.GAN_folder}/GAN_checkpoint.ckpt"
        args.base_tensor_path = f"{args.main_path}/inputs/GAN_base_tensor.pkl"
        opt = BaseOptions().parse(args)
        opt.face_points = load_zipped_pickle(args.face_points_path)
        args.opt = opt
        
    #args.sign_request_id = os.path.splitext(os.path.basename(args.input_video_path))[0]
    return args