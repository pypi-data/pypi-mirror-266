import logging, torch, imageio, cv2, copy, os
import numpy as np
from pathlib import Path
from signapse.heatmaps import HEATMAPS


class GENERATOR():
    def __init__(self, args):
        super(GENERATOR,self).__init__()
        self.args=args 

    
    def mkdir_safe(self,path):
        Path(path).mkdir(parents=True, exist_ok=True)
        
    def set_new_shoulder_points(self,signer,remove_hip_pose,pose_tensor, tolerance=(20/1024)):
        if signer == 'Jay':
            logging.info('SETTING JAY SHOULDER TO ONE VALUE, video_utils line 100')
            pose_tensor[:,0,:] = torch.from_numpy(np.array([0.70364093, 0.44848727])).to(pose_tensor.device)
            pose_tensor[:,1,:] = torch.from_numpy(np.array([0.29054845, 0.46131581])).to(pose_tensor.device)
            if not remove_hip_pose:
                pose_tensor[:,-2,:] = torch.from_numpy(np.array([0.63351321, 1.00569902])).to(pose_tensor.device)
                pose_tensor[:,-1,:] = torch.from_numpy(np.array([0.37140189, 1.00468008])).to(pose_tensor.device)
        elif signer == 'Marcel':
            logging.info('SETTING JAY SHOULDER TO ONE VALUE, video_utils line 106')
            pose_tensor[:,0,:] = torch.from_numpy(np.array([0.72490184+tolerance, 0.41866337+tolerance])).to(pose_tensor.device)
            pose_tensor[:,1,:] = torch.from_numpy(np.array([0.2982856-tolerance,  0.41772193+tolerance])).to(pose_tensor.device)
            if not remove_hip_pose:
                pose_tensor[:,-2,:] = torch.from_numpy(np.array([0.63403587, 1.01317168])).to(pose_tensor.device)
                pose_tensor[:,-1,:] = torch.from_numpy(np.array([0.36255618, 1.00577158])).to(pose_tensor.device)
        return pose_tensor
    
    def import_crops(self,hand_crop,face_crop,sign_request_id, length):
        if hand_crop:
            hand_mask = np.load(f'./inputs/SAM_files/{sign_request_id}.npy')
        else:
            hand_mask = range(0,length)
            
        if face_crop:
            face_mask = np.load(f'./inputs/Face_files/{sign_request_id}.npy')
        else:
            face_mask = range(0,length)        
        return hand_mask, face_mask
    
    def apply_norm(self,cropped_frame,img_centre,min_size):
        cropped_frame = cropped_frame[img_centre[1]:img_centre[1]+img_centre[3], img_centre[0]:img_centre[0]+img_centre[2]]
        return cv2.resize(cropped_frame, (min_size, min_size))
        
    def create_pose_video_from_MP(self,img_centre,min_size,FPS,pose_tensor,GAN_model):
        pose_tensor = self.set_new_shoulder_points(self.args.signer,self.args.opt.remove_hip_pose,pose_tensor)      
        hand_mask, face_mask = self.import_crops(self.args.opt.hand_crop,self.args.opt.face_crop,self.args.sign_request_id, len(pose_tensor))
        
        # Create the output folder
        self.mkdir_safe(self.args.output_video_path)
        output_video_file = self.args.output_video_path + self.args.sign_request_id + ".mp4"
        output_video = imageio.get_writer(output_video_file, fps=float(FPS), codec='libx264')
        logging.info(f"Producing Video at {output_video_file}")
        logging.info(f"\n")
        logging.info(f"Generating Pose video --- ")
        input_video_path = self.args.input_video_path
        reader = imageio.get_reader(input_video_path)
        crops,maps=[],[]
        counter = 0
        for input_frame in reader:
            if (counter < self.args.start):
                    continue
            if counter % 25 == 0:
                logging.info("Frame: {}".format(counter))
                
            if counter >= self.args.stop:
                break
            # Crop the input image
            input_frame = self.apply_norm(input_frame,img_centre,min_size)
            # Extract the saved pose estimation result
            MP_results = copy.deepcopy(pose_tensor[counter])  
            
            heat_maps, hand_crops = HEATMAPS().get_heatmaps_crops(input_frame=input_frame,
                                                                MP_results_gen= MP_results,
                                                                GAN_model= GAN_model,  
                                                                opt=self.args.opt,
                                                                iii=counter,
                                                                hand_mask= hand_mask[counter],
                                                                face_mask= face_mask[counter]
                                                                )
                
            if self.args.opt.merge_crops:
                hand_crops = hand_crops.view((len(hand_crops)) // 2, 2, hand_crops.shape[1], hand_crops.shape[2]).sum(dim=1) + 1
                  
            if counter==0 and (self.args.opt.num_frames)>0:
                for _ in range(self.args.opt.num_frames):
                    maps.append(heat_maps)
                    crops.append(hand_crops)
                    
            maps.append(heat_maps)
            crops.append(hand_crops)
            
            if (self.args.opt.num_frames)>counter:
                mid_input_frame = copy.deepcopy(input_frame)
                continue
            
            if not self.args.opt.multi_frames:
                mid_input_frame = input_frame
        
            frame = HEATMAPS().generate_GAN_frame_maps_crops(mid_input_frame,
                                                           maps,
                                                           crops,
                                                           GAN_model= GAN_model,
                                                           opt=self.args.opt,
                                                           detailed_video=self.args.detailed_video                                                                                                
                                                           )
                
            

            # Write each generated frame to the output video
            output_video.append_data(frame)
            maps = maps[1:]
            crops =crops[1:]
            mid_input_frame = copy.deepcopy(input_frame)
            counter+=1
        
        if self.args.opt.multi_frames:
            # duplicate last frames as well 
            for _ in range(self.args.opt.num_frames):
                maps.append(heat_maps)
                crops.append(hand_crops)
                    
                frame = HEATMAPS().generate_GAN_frame_maps_crops(input_frame,
                                                            maps,
                                                            crops,
                                                            GAN_model= GAN_model,
                                                            opt=self.args.opt,
                                                            detailed_video=self.args.detailed_video                                                                                                
                                                            )
                output_video.append_data(frame)
                maps = maps[1:]
                crops =crops[1:]
        
        
        
        
        if self.args.opt.hand_crop:
            os.remove(f'./inputs/SAM_files/{self.args.sign_request_id}.npy')
        if self.args.opt.face_crop:
            os.remove(f'./inputs/Face_files/{self.args.sign_request_id}.npy')
        reader.close()
        output_video.close()
