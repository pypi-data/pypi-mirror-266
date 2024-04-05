import torch,logging
from signapse.compute import parallel_computing, serial_computing
from signapse.mp_utils import INTERPLATION, IMAGE_PROCESSING
import numpy as np
import signapse.constants as C

class POSE():
    def __init__(self, args):
        super(POSE,self).__init__()
        self.args=args   
        
    def face_mesh_landmarks_to_small_tensor(self,face_mesh_landmarks):
        FM_tensor = torch.stack([torch.tensor([landmark.x, landmark.y]) for landmark in face_mesh_landmarks.landmark])
        return FM_tensor
    # Given a MediaPipe output, convert it to a MediaPipe small tensor
    def results_to_small_tensor(self,data,face_points):
        # Pose landmarks
        if data.pose_landmarks is not None:
            pose_landmarks = torch.stack([torch.tensor([landmark.x, landmark.y]) for landmark in data.pose_landmarks.landmark])
            pose_results = pose_landmarks[11:17]
            hip_results = pose_landmarks[23:25]
        else:
            pose_results = torch.zeros((6,2))
            hip_results = torch.zeros((2,2))
        # Left hand landmarks
        if data.left_hand_landmarks is not None:
            LH_results = torch.stack([torch.tensor([landmark.x, landmark.y]) for landmark in data.left_hand_landmarks.landmark])
            #LH_results[0] = pose_landmarks[15]
        else:
            LH_results = torch.zeros((21,2))
            
        # Right hand landmarks
        if data.right_hand_landmarks is not None:
            RH_results = torch.stack([torch.tensor([landmark.x, landmark.y]) for landmark in data.right_hand_landmarks.landmark])
            #RH_results[0] = pose_landmarks[16]

        else:
            RH_results = torch.zeros((21, 2))
        # Face landmarks
        if data.face_landmarks is not None:
            face_landmarks = torch.stack([torch.tensor([landmark.x, landmark.y]) for landmark in data.face_landmarks.landmark])
            face_results = face_landmarks[list(face_points.keys())]
        else:
            face_results = torch.zeros((128, 2))

        # Make the hand wrist equal to the pose wrist
        LH_results[0] = pose_results[4]
        RH_results[0] = pose_results[5]
        all_results = torch.cat((pose_results, LH_results, RH_results, face_results,hip_results))

        return all_results
    
    # # Given a MediaPipe tensor, find the shoulder centre
    # def find_shoulder_centre_MP_small_tensor(self,MP_results_find):
    #     left_shoulder = MP_results_find[0]
    #     right_shoulder = MP_results_find[1]
    #     MP_x_centre = right_shoulder[0] + (left_shoulder[0] - right_shoulder[0]) / 2
    #     MP_y_centre = right_shoulder[1] + (left_shoulder[1] - right_shoulder[1]) / 2
    #     return (MP_x_centre,MP_y_centre)

    # # Given a MediaPipe tensor, find the shoulder length
    # def find_euc_shoulder_distance_MP_small_tensor(self,MP_results, res):
    #     left_shoulder = MP_results[0]
    #     right_shoulder = MP_results[1]    
    #     x_ = (left_shoulder[0]*res - right_shoulder[0]*res)**2
    #     y_ = (left_shoulder[1]*res - right_shoulder[1]*res)**2   
    #     euc_shoulder = math.sqrt(x_ + y_)
        
    #     ## Vertical scaling
    #     head_top_point = MP_results[MP_results[48:,1].argmax()+48] 
    #     head_bottom_point = MP_results[MP_results[48:,1].argmin()+48]
    #     x_ = (head_top_point[0]*res - head_bottom_point[0]*res)**2
    #     y_ = (head_top_point[1]*res - head_bottom_point[1]*res)**2
    #     euc_head = math.sqrt(x_ + y_)
    #     return euc_shoulder, euc_head
    
    # # Calculate the required scale and centre of a MediaPipe tensor
    # def get_scale_and_centre_small_tensor(self,MP_results_get,loadSize):
    #     euc_shoulder, euc_head = self.find_euc_shoulder_distance_MP_small_tensor(MP_results_get, loadSize)
    #     # optimum_shoulder should be 260 for Marcel
    #     #optimum_shoulder = 490#440 # Jay#490 #Marcel #260 #200 #210
    #     if euc_shoulder > 0 and euc_head > 0:
    #         x_scale =  1 #  optimum_shoulder / euc_shoulder
    #         MP_scales = [x_scale, x_scale]

    #         MP_x_centre, MP_y_centre = self.find_shoulder_centre_MP_small_tensor(MP_results_get)
    #         MP_x_centre = MP_x_centre * x_scale
    #         MP_y_centre = MP_y_centre * x_scale
    #         MP_centres = [MP_x_centre, MP_y_centre]
    #     else:
    #         MP_scales  = [0,0]
    #         MP_centres = [0,0]    
    #     return torch.tensor(MP_scales),torch.tensor(MP_centres)

    def get_all_frames(self, img_centre, min_size):
        logging.info(f" Reading video frames --- ")
        logging.info(f"\n")                
        pose_tensor = torch.Tensor()
        if self.args.stop != -1 and total_frames > self.args.stop:
            total_frames =  self.args.stop
       
        if self.args.num_workers > 1:
            ## extracting pose landmarks, scales and centres in parallel processing
            Non_interpolated_MP_results ,MP_scales, MP_centres, total_frames = parallel_computing( \
                self.args.input_video_path, self.args.num_workers, img_centre, min_size, \
                    self.args.opt)
        else:
            Non_interpolated_MP_results ,MP_scales, MP_centres, total_frames = serial_computing( \
            self.args.input_video_path, img_centre, min_size, \
                self.args.opt)


        # get missing frames
        missing = ((MP_centres.sum(dim=1)==0).nonzero())
        logging.info(f" {len(missing)} frame(s) are predicted out of {total_frames}")

        ## Interpolating scales and centres
        MP_scales = INTERPLATION().interpolate_All_MP_Tensors(MP_scales,no_zero_start=False)
        MP_centres = INTERPLATION().interpolate_All_MP_Tensors(MP_centres,no_zero_start=False) 
        MP_result = INTERPLATION().interpolate_All_MP_Tensors(Non_interpolated_MP_results,no_zero_start=False) 
        MP_scales = INTERPLATION().smooth_keypoints(MP_scales, 0, None) # 0 is the code for setting kernel 

        ## Scaling and Centring
        # with CF.ProcessPoolExecutor(max_workers=self.args.num_workers) as executor:
        #     for itm in (executor.map(scaling,MP_result,MP_scales,MP_centres,[self.args.signer]*len(MP_scales),[self.args.pro]*len(MP_scales))):
        #         pose_tensor = torch.cat((pose_tensor, itm.unsqueeze(0)), dim=0)
        pose_tensor = MP_result
        if not self.args.opt.face_mesh:
            pose_tensor[:,48:] = IMAGE_PROCESSING().mouth_centering(pose_tensor[:,48:], sigma=11)
          
        return pose_tensor, Non_interpolated_MP_results, MP_scales[0,0]
    
    def postprocessing(self, pose_tensor):
        logging.info(f"Postprocessing --- ")
        logging.info(f"\n")
        pose_tensor[:,48:] = IMAGE_PROCESSING().mouth_centering(pose_tensor[:,48:], sigma=19)
        
        # Gaussian smoothing
        if self.args.opt.face_mesh:
            # Smoothing points from 48:
            Points = pose_tensor[0,48:]  # compute the point distance based on frame 0
            pose_tensor[:,C.FACE_MESH_MOP] = IMAGE_PROCESSING().mouth_centering(pose_tensor[:,C.FACE_MESH_MOP], sigma=9)
            # Using the center points of the mouth [13,:] as the center of the face
            dist_to_centre = np.linalg.norm(Points - Points[13,:], axis=-1)
            dist_to_centre = dist_to_centre/np.max(dist_to_centre)
            smoothed_signal = np.array([INTERPLATION().smooth_keypoints(pose_tensor[:,i], i, dist_to_centre[i-48]) for i in range(pose_tensor.shape[1])])
            # smoothed_signal = pose_tensor
        else:
            dist_to_centre= np.zeros_like(pose_tensor[0,:,0])
            smoothed_signal = np.array([INTERPLATION().smooth_keypoints(pose_tensor[:,i], i, dist_to_centre[i]) for i in range(pose_tensor.shape[1])])
            
        smoothed_signal = torch.from_numpy(smoothed_signal).transpose(0,1)
        # if self.args.opt.signer=='Marcel':
        #     smoothed_signal[:,6:48,:] = pose_tensor[:,6:48,:]
            
        return smoothed_signal.to(self.args.GPU)

