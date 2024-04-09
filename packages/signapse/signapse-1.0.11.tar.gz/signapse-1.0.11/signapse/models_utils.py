import torch, cv2
import torch.nn as nn
import functools
from copy import deepcopy
import numpy as np


def edge_detecor(input_img, detector='Sobel', smooth=False, threshold = False):
    input_array = torch.clamp((input_img + 1) * 127.5, 0, 255).byte()
    np_img = input_array[0].cpu().numpy()
    if smooth:
        kernel_size = 5
        sigma = 0.3 * ((kernel_size - 1) * 0.5 - 1) + 0.8 
        np_img = cv2.GaussianBlur(np_img, (kernel_size,kernel_size), sigma)
        
    if detector== "Canny":
        edges = cv2.Canny(np_img, 1, 255, apertureSize = 5, L2gradient = True)
    else :              
        grad_x = cv2.Sobel(np_img, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(np_img, cv2.CV_64F, 0, 1, ksize=3)
        abs_grad_x = cv2.convertScaleAbs(grad_x)
        abs_grad_y = cv2.convertScaleAbs(grad_y)
        edges = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)
        
    if threshold:     
        _, edges = cv2.threshold(edges, np.min(edges), np.max(edges), cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    edge_tensor =  torch.tensor(edges, dtype=torch.float32) / 255.0 * 2.0 - 1.0
    return edge_tensor.unsqueeze(0)

def create_model(opt, ckpt):
    model = Pose2VidHDModel()
    model.initialize(opt)
    sum_model_parameters = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"model was created with {'{:,}'.format(sum_model_parameters)} trainable parameters")

    if opt.cuda:
        model = torch.nn.DataParallel(model, device_ids=opt.gpu_ids)
        model.module.init_from_checkpoint(ckpt)
    else:
        model.init_from_checkpoint(ckpt)

    return model

class BaseModel(torch.nn.Module):
    def name(self):
        return 'BaseModel'

    def initialize(self, opt):
        self.opt = opt
        self.gpu_ids = opt.gpu_ids
        self.Tensor = torch.cuda.FloatTensor if self.opt.cuda else torch.Tensor

    def forward(self):
        pass

    def init_from_checkpoint(self, ckpt_path):
        """
        Initialize the trainer from a given checkpoint file.

        This checkpoint file contains not only model parameters, but also
        scheduler and optimizer states, see `self._save_checkpoint`.

        :param ckpt_name: path to checkpoint
        """
        model_checkpoint = torch.load(ckpt_path, map_location= "cuda" if self.opt.cuda else "cpu")

        model_checkpoint = self.check_module_in_checkpoint(model_checkpoint)

        self.netG.load_state_dict(model_checkpoint["netG_state"])

        if self.opt.face_and_body:
            self.netG_face.load_state_dict(model_checkpoint["netG_face_stat"])

        if self.opt.hand_and_body:
            self.netG_hand.load_state_dict(model_checkpoint["netG_hand_state"])

    def check_module_in_checkpoint(self,model_checkpoint):
        # Check if the model parameter keys include "module" or not
        if not any([("module" in name) for name, param in list(self.netG.named_parameters())]):
            # If they don't contain "module", ensure the checkpoint doesn't have "module"
            model_checkpoint_copy = model_checkpoint.copy()
            model_checkpoint_copy["netG_state"] = {}
            for name, param in list(self.netG.named_parameters()):
                # If the parameter is correctly named, just copy it
                if name in model_checkpoint["netG_state"]:
                    model_checkpoint_copy["netG_state"][name] = model_checkpoint["netG_state"][name]
                else:
                    # If the parameter isn't correctly named, change it's name
                    model_checkpoint_copy["netG_state"][name] = model_checkpoint["netG_state"][f"module.{name}"]
            model_checkpoint = model_checkpoint_copy.copy()
        if self.opt.face_and_body:
            if not any([("module" in name) for name, param in list(self.netG.named_parameters())]):
                # If they don't contain "module", ensure the checkpoint doesn't have "module"
                model_checkpoint_copy = model_checkpoint.copy()
                model_checkpoint_copy["netG_face_stat"] = {}
                #for name, param in list(self.netG.named_parameters()):
                for name, param in list(self.netG_face.named_parameters()):
                    # If the parameter is correctly named, just copy it
                    if name in model_checkpoint["netG_face_stat"]:
                        model_checkpoint_copy["netG_face_stat"][name] = model_checkpoint["netG_face_stat"][name]
                    else:
                        # If the parameter isn't correctly named, change it's name
                        model_checkpoint_copy["netG_face_stat"][name] = model_checkpoint["netG_face_stat"][f"module.{name}"]
                model_checkpoint = model_checkpoint_copy.copy()
                
        if self.opt.hand_and_body:
            if not any([("module" in name) for name, param in list(self.netG.named_parameters())]):
                # If they don't contain "module", ensure the checkpoint doesn't have "module"
                model_checkpoint_copy = model_checkpoint.copy()
                model_checkpoint_copy["netG_hand_state"] = {}
                #for name, param in list(self.netG.named_parameters()):
                for name, param in list(self.netG_hand.named_parameters()):
                    # If the parameter is correctly named, just copy it
                    if name in model_checkpoint["netG_hand_state"]:
                        model_checkpoint_copy["netG_hand_state"][name] = model_checkpoint["netG_hand_state"][name]
                    else:
                        # If the parameter isn't correctly named, change it's name
                        model_checkpoint_copy["netG_hand_state"][name] = model_checkpoint["netG_hand_state"][f"module.{name}"]
                model_checkpoint = model_checkpoint_copy.copy()

        return model_checkpoint


###############################################################################
# Functions
###############################################################################
def weights_init(m):
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        m.weight.data.normal_(0.0, 0.02)
    elif classname.find('BatchNorm2d') != -1:
        m.weight.data.normal_(1.0, 0.02)
        m.bias.data.fill_(0)

def get_norm_layer():
    norm_layer = functools.partial(nn.InstanceNorm2d, affine=False)
    return norm_layer

# TODO: 20180929: Generator Input contains two images...
def define_G(opt, input_nc, output_nc, ngf, n_downsample_global=3, n_blocks_global=9, cuda=False):
    norm_layer = get_norm_layer()
    netG = GlobalGenerator(opt, input_nc, output_nc, ngf, n_downsample_global, n_blocks_global, norm_layer)
    if cuda:
        assert(torch.cuda.is_available())
        netG.cuda()
    netG.apply(weights_init)
    return netG


##############################################################################
# Generator
##############################################################################

class GlobalGenerator(nn.Module):
    def __init__(self, opt, input_nc, output_nc, ngf=64, n_downsampling=3, n_blocks=9, norm_layer=nn.BatchNorm2d):
        assert(n_blocks >= 0)
        super(GlobalGenerator, self).__init__()
        activation = nn.ReLU(True)

        self.n_downsampling = n_downsampling

        down_model = [nn.ReflectionPad2d(3), nn.Conv2d(input_nc, ngf, kernel_size=7, padding=0),
                      norm_layer(ngf), activation]

        # DOWNSAMPLING - down_model
        for i in range(n_downsampling):
            mult = 2 ** i
            down_model += [nn.Conv2d(ngf * mult, ngf * mult * 2, kernel_size=3, stride=2, padding=1),
                           norm_layer(ngf * mult * 2), activation]

        # RESNET - resnet_model
        resnet_model = []
        mult = 2 ** n_downsampling
        for i in range(n_blocks):
            resnet_model += [ResnetBlock(ngf * mult, norm_layer=norm_layer)]

        # UPSAMPLING - up_model
        up_model = []
        f_times = 2
        for i in range(n_downsampling):
            mult = 2 ** (n_downsampling - i)

            up_model += [nn.ConvTranspose2d(ngf * mult * f_times, int(ngf * mult / 2), kernel_size=3, stride=2, padding=1,
                                   output_padding=1),
                norm_layer(int(ngf * mult / 2)), activation]


        up_model += [nn.ReflectionPad2d(3), nn.Conv2d(ngf, output_nc, kernel_size=7, padding=0), nn.Tanh()]

        self.down_model = nn.Sequential(*down_model)
        self.resnet_model = nn.Sequential(*resnet_model)
        self.up_model = nn.Sequential(*up_model)
        self.controlnet = opt.cfg['model']['generator']['controlnet']
        self.alpha = opt.cfg['model']['generator']['control_alpha']
        if self.controlnet:
            self.conditional_model = deepcopy(self.down_model)
            zero_convs = [nn.Conv2d(ngf , ngf , kernel_size=1,  padding=0)]
            for i in range(n_downsampling-1):
                mult = 2**(i+1)
                zero_convs += [nn.Conv2d(ngf * mult, ngf * mult, kernel_size=1,  padding=0)]
            self.zero_convs = nn.Sequential(*zero_convs)

    def forward(self, input):

        # Skip Connections - need to have access to each of the down sampled features
        skip = 3 # Each block has 3 layers (Conv, Norm, ReLU)
        down_initial = 4
        
        if self.controlnet:         
            # TODO set new input as a condition
            cond_input = deepcopy(input)  ##                
            for i in range (5,7):
                edges_tensor = edge_detecor(cond_input[:,i,:,:]) # takes and return tensor [1,w,h]
                cond_input[:,i,:,:] = edges_tensor.to(cond_input.device)
            
            cond_dict = {"down_0":self.conditional_model[:down_initial](cond_input)}
            for i in range(self.n_downsampling):
                cond_dict[f"down_{i+1}"] = self.conditional_model[down_initial + skip*i:down_initial + skip + skip*i](cond_dict[f"down_{i}"]) 

        # DOWNSAMPLING - down_model
        # Initial down model is the first 4 layers - applied to input
        down_0 = self.down_model[:down_initial](input)
        down_dict = {"down_0":down_0}
        # Each set of 3 layers (Conv, Norm, ReLU) is recursively applied to the previous output
        for i in range(self.n_downsampling):
            # Importantly, the output of each down block is saved, as down_i, to be used in the upsampling blocks
            # Save these in a dictionary, key is down sampling block, value is the output of that downsampling block
            down_dict[f"down_{i+1}"] = self.down_model[down_initial + skip*i:down_initial + skip + skip*i](down_dict[f"down_{i}"])

        # RESNET - resnet_model
        # Resnet applied to the final downsampled features
        resnet = self.resnet_model(down_dict[f"down_{self.n_downsampling}"])

        # UPSAMPLING - up_model
        up = resnet
        # Concatenate the final downsampled features with the output of the Resnet block
        up = torch.cat((up,down_dict[f"down_{self.n_downsampling}"]),dim=1)

        # For each upsampling block, apply to previous output and downsampled features
        for i in range(self.n_downsampling):
            # Recursively apply each upsampling block (Conv, Norm, ReLU) to the total features
            up = self.up_model[skip * i:skip +  skip * i](up)
            if i != (self.n_downsampling - 1):
                # For each Up layer, the total features are a concatenation of the previous Up layer outputs and the corresponding Down layer output
                # Count down the saved downsampling outputs (down_i), from smallest to largest
                if self.controlnet:
                    alpha = self.alpha
                    up = torch.cat(((1-alpha)*up+ alpha*(self.zero_convs[self.n_downsampling - (1+i)](cond_dict[f"down_{self.n_downsampling - (i+1)}"])), down_dict[f"down_{self.n_downsampling - (i+1)}"]),dim=1)
                else:
                    up = torch.cat((up,down_dict[f"down_{self.n_downsampling - (i+1)}"]),dim=1)

        # Apply the final up block to the final output
        out = self.up_model[skip + skip * i:](up)

        return out

# Define a resnet block
class ResnetBlock(nn.Module):
    def __init__(self, dim, norm_layer, activation=nn.ReLU(True)):
        super(ResnetBlock, self).__init__()
        self.conv_block = self.build_conv_block(dim, norm_layer, activation)

    def build_conv_block(self, dim, norm_layer, activation, ):
        conv_block = []
        p = 0
        conv_block += [nn.ReflectionPad2d(1)]

        conv_block += [nn.Conv2d(dim, dim, kernel_size=3, padding=p),
                       norm_layer(dim),
                       activation]

        conv_block += [nn.ReflectionPad2d(1)]

        conv_block += [nn.Conv2d(dim, dim, kernel_size=3, padding=p),
                       norm_layer(dim)]

        return nn.Sequential(*conv_block)

    def forward(self, x):
        out = x + self.conv_block(x)
        return out


class Pose2VidHDModel(BaseModel):
    def name(self):
        return 'Pose2VidHDModel'

    def init_loss_filter(self, use_gan_feat_loss, use_vgg_loss, use_flow_loss, use_TC, use_hand_disc, use_hand_enhancer,
                         use_hand_enhancer_adv, use_hand_classifier,
                         use_KLD, use_style_disc, use_style_encode):
        flags = (True, use_gan_feat_loss, use_vgg_loss, use_flow_loss, True, True, use_TC, use_hand_disc, use_hand_disc,
                 use_hand_disc,
                 use_hand_enhancer, use_hand_enhancer_adv, use_hand_enhancer_adv, use_hand_enhancer_adv,
                 use_hand_classifier,
                 use_KLD, use_style_disc, use_style_disc, use_style_disc, use_style_encode)

        def loss_filter(g_gan, g_gan_feat, g_vgg, g_flow, d_real, d_fake, g_TC, g_hand, d_hand_real, d_hand_fake,
                        g_HE_keypoints, d_HE_real, d_HE_fake, g_HE_D, g_HSA,
                        kld, g_style, d_style_real, d_style_fake, g_style_encode):
            return [l for (l, f) in
                    zip((g_gan, g_gan_feat, g_vgg, g_flow, d_real, d_fake, g_TC, g_hand, d_hand_real, d_hand_fake,
                         g_HE_keypoints, d_HE_real, d_HE_fake, g_HE_D, g_HSA,
                         kld, g_style, d_style_real, d_style_fake, g_style_encode), flags) if f]

        return loss_filter

    def initialize(self, opt):
        BaseModel.initialize(self, opt)
        torch.backends.cudnn.benchmark = True
        input_nc = opt.label_nc if opt.label_nc != 0 else opt.input_nc

        ##### define networks
        # Generator network
        # Add 3 channels for the style image concatenated to the front
        netG_input_nc = input_nc
        if self.opt.base_style:
            netG_input_nc += 3

        if self.opt.face_mesh:
            netG_input_nc += 1

        if self.opt.hand_and_body:
            if self.opt.hand_pose:
                self.hand_crop_nc = 42
            else:
                self.hand_crop_nc = 2
            netG_input_nc -= self.hand_crop_nc

        self.netG = define_G(opt, netG_input_nc, opt.output_nc, opt.ngf,
                                      opt.n_downsample_global, opt.n_blocks_global, cuda=opt.cuda)

        if self.opt.face_and_body:
            if self.opt.no_face_input:
                netG_face_input_nc = netG_input_nc
            else:
                netG_face_input_nc = netG_input_nc + 3
            self.netG_face = define_G(opt, netG_face_input_nc, opt.output_nc, opt.ngf_face,
                                      opt.n_downsample_global_face, opt.n_blocks_global_face, cuda=opt.cuda)

        if (self.opt.hand_and_body):
            netG_hand_input_nc = self.hand_crop_nc + 3
            self.netG_hand = define_G(opt, netG_hand_input_nc, opt.output_nc, opt.ngf_hand,
                                      opt.n_downsample_global_hand, opt.n_blocks_global_hand, cuda=opt.cuda)

    def forward(self, label, face):
        x1 = label.data[:, 0, ...]
        if self.opt.cuda:
            x1.cuda()

        if self.opt.hand_and_body:
            hand_crop = x1[:, -self.hand_crop_nc:]
            x1_no_hand_crop = x1[:, :-self.hand_crop_nc]
            y1 = self.netG.forward(x1_no_hand_crop)
        else:
            y1 = self.netG.forward(x1)

        if (self.opt.face_and_body):

            if (0 not in face):

                if not self.opt.no_face_input:
                    face_input = torch.cat((y1, x1), dim=1)
                elif self.opt.no_face_input:
                    face_input = x1

                face_tensor = face_input[:, :, face[0]:face[1], face[2]:face[3]]
                face_output = self.netG_face.forward(face_tensor)

                y1[:, :, face[0]:face[1], face[2]:face[3]] += face_output

                if not self.opt.no_face_output:
                    y1[:, :, face[0]:face[1], face[2]:face[3]] += face_output
                elif self.opt.no_face_output:
                    y1[:, :, face[0]:face[1], face[2]:face[3]] = face_output

        if self.opt.hand_and_body:
            if self.opt.HaB_all_image:
                hand_input = torch.cat((y1, hand_crop), dim=1)
                y1_hand = self.netG_hand.forward(hand_input)
                y1 = y1_hand

        return torch.squeeze(y1.detach())