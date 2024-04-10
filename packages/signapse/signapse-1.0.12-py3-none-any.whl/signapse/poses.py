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
    

    def get_all_frames(self, img_centre, min_size,total_frames):
        logging.info(f" Reading video frames --- ")
        logging.info(f"\n")                
        pose_tensor = torch.Tensor()
        if self.args.stop != -1:
            total_frames =  self.args.stop
       
        if self.args.num_workers > 1:
            ## extracting pose landmarks, scales and centres in parallel processing
            Non_interpolated_MP_results ,MP_scales, MP_centres = parallel_computing( \
                self.args.input_video_path, self.args.num_workers, img_centre, min_size, \
                    self.args.opt,total_frames)
        else:
            Non_interpolated_MP_results ,MP_scales, MP_centres = serial_computing( \
            self.args.input_video_path, img_centre, min_size,self.args.opt,total_frames)


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

