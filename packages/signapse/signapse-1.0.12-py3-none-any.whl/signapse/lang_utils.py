import  torch,logging,imageio 
import mediapipe as mp
import numpy as np
from PIL import Image, ImageEnhance
logging.basicConfig(level=logging.INFO)

from signapse.lang_sam import LangSAM
import signapse.constants as C
from signapse.create import GENERATOR
from signapse.mp_utils import INTERPLATION, IMAGE_PROCESSING

mp_face_mesh = mp.solutions.face_mesh
face_mesh =  mp_face_mesh.FaceMesh(max_num_faces=1,
                                    static_image_mode=True,
                                    refine_landmarks=True,
                                    min_detection_confidence=0.8,
                                    min_tracking_confidence=0.8)
face_oval = list(mp_face_mesh.FACEMESH_FACE_OVAL)
face_mesh_mop = [num-176 for num in C.FACE_MESH_MOP]

class SAM_CROPS():
    def __init__(self, args):
        super(SAM_CROPS,self).__init__()
        self.args=args  
        
        
    def get_face_landmarks(self,image):
        image.flags.writeable = False
        results = face_mesh.process(image)
        image.flags.writeable = True    
        if results.multi_face_landmarks:
            data = results.multi_face_landmarks[0] 
            face_landmarks = np.array([[landmark.x, landmark.y] for landmark in data.landmark])
        else:
            face_landmarks = np.zeros((478,2))
        return face_landmarks
    
    def sam_masks(self,img_centre,frame_number):
        if (self.args.opt.face_crop) or (self.args.opt.hand_crop):
            model = LangSAM()
            GENERATOR(self.args).mkdir_safe("./inputs/SAM_files")
            GENERATOR(self.args).mkdir_safe("./inputs/Face_files")
            reader = imageio.get_reader(self.args.input_video_path)
            #frame_number = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if self.args.stop != -1 and frame_number > self.args.stop:
                frame_number = self.args.stop
            mask =  torch.Tensor()
            mask2=[]
            for i, frame in enumerate(reader): 
                if i < self.args.start:
                    continue     
                if i% 50==0:
                    logging.info("Frame: {}".format(i))
                
                frame = IMAGE_PROCESSING().apply_norm(frame,img_centre,self.args.opt.loadSize)
                image_pil = array2pil(frame,enhance=True)
                    
                    
                masks, _, _, _ = model.predict(image_pil, "hand", box_threshold=0.2, text_threshold=0.2, padding = None)
                if len(masks) ==0:
                    masks, _, _, _ = model.predict(image_pil, "hand", box_threshold=0.2, text_threshold=0.2, padding = None)            
                masks_hand = torch.sum(masks, dim=0)
                masks_hand[masks_hand>0] = 1  
                hand = masks_hand.unsqueeze(0)     
                mask = torch.cat((mask, hand.unsqueeze(0)), dim=0)   
                
                if self.args.opt.face_crop:
                    face_mask = self.get_face_landmarks(frame)    
                    mask2.append(face_mask)
                    
            ## interpolate face mesh
            if self.args.opt.face_crop:
                mask2 = INTERPLATION().interpolate_All_MP_Tensors(torch.from_numpy(np.array(mask2)),no_zero_start=False)
            if self.args.opt.smooth_face_crop:
                Points = mask2[0,48:]  # compute the point distance based on frame 0
                mask2[:,face_mesh_mop] = IMAGE_PROCESSING().mouth_centering(mask2[:,face_mesh_mop], sigma=9)
                # Using the center points of the mouth [13,:] as the center of the face
                dist_to_centre = np.linalg.norm(Points - Points[13,:], axis=-1)
                dist_to_centre = dist_to_centre/np.max(dist_to_centre)
                smoothed_signal = np.array([INTERPLATION().smooth_keypoints(mask2[:,i], i, dist_to_centre[i-48]) for i in range(mask2.shape[1])]) #dist_to_centre[i-48]
                mask2 = np.transpose(smoothed_signal, (1, 0, 2))

            np.save(f'./inputs/SAM_files/{self.args.sign_request_id}.npy',mask)
            np.save(f'./inputs/Face_files/{self.args.sign_request_id}.npy',mask2)

    
def array2pil(frame,enhance=False):
    if enhance:
        image_pil = Image.fromarray(frame.astype(np.uint8)).convert('RGB') 
        image_pil = ImageEnhance.Sharpness(image_pil).enhance(5)
    else:
        image_pil = Image.fromarray(frame.astype(np.uint8)).convert('RGB')      
    return image_pil
 
