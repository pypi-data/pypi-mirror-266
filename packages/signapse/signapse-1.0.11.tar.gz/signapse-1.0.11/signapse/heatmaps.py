import torch, copy, cv2, math
import numpy as np
import signapse.constants as C
from torchvision import transforms 
from torch.autograd import Variable
import mediapipe as mp
mp_face_mesh = mp.solutions.face_mesh


# Draw a line between two points using OpenCV, if they are positive points
def draw_line(im, joint1, joint2, c=(0, 0, 255),t=1,width=3,decimal_places=2):
    thresh = 0
    joint1 = (round(joint1[0].item(), decimal_places), round(joint1[1].item(), decimal_places))
    joint2 = (round(joint2[0].item(), decimal_places), round(joint2[1].item(), decimal_places))
    if joint1[0] > thresh and  joint1[1] > thresh and joint2[0] > thresh and joint2[1] > thresh:
        center = (int((joint1[0] + joint2[0]) / 2), int((joint1[1] + joint2[1]) / 2))
        length = int(math.sqrt(((joint1[0] - joint2[0]) ** 2) + ((joint1[1] - joint2[1]) ** 2))/2)
        angle = math.degrees(math.atan2((joint1[0] - joint2[0]),(joint1[1] - joint2[1])))
        cv2.ellipse(im, center, (width,length), -angle,0.0,360.0, c, -1)
        
        # joint1 = (int(joint1[0].item()), int(joint1[1].item()))
        # joint2 = (int(joint2[0].item()), int(joint2[1].item()))
        # cv2.line(im, joint1, joint2, c, 2)
        
def draw_line_nonan(im, joint1, joint2, c=(0, 0, 255),t=1, width=3):
    if not (joint1.isnan().any() or joint2.isnan().any()):
        draw_line(im, joint1, joint2, c, t, width)
        
def draw_face_mesh_small_tensor(frame,FM_tensor,connections=mp_face_mesh.FACEMESH_TESSELATION):
    for connection in connections:
        start_idx = connection[0]
        end_idx = connection[1]

        start = (FM_tensor[start_idx][0].item(),FM_tensor[start_idx][1].item())
        end = (FM_tensor[end_idx][0].item(), FM_tensor[end_idx][1].item())

        cv2.line(frame, start,end,color=(1, 1, 1), thickness=1)
    return frame
        
# Convert from a tensor representation to an image
def tensor2im(image_tensor, imtype=np.uint8, normalize=True):
    if isinstance(image_tensor, list):
        image_numpy = []
        for i in range(len(image_tensor)):
            image_numpy.append(tensor2im(image_tensor[i], imtype, normalize))
        return image_numpy
    image_numpy = image_tensor.cpu().float().numpy()
    if normalize:
        image_numpy = (np.transpose(image_numpy, (1, 2, 0)) + 1) / 2.0 * 255.0
    else:
        image_numpy = np.transpose(image_numpy, (1, 2, 0)) * 255.0
    image_numpy = np.clip(image_numpy, 0, 255)
    if image_numpy.shape[2] == 1 or image_numpy.shape[2] > 3:
        image_numpy = image_numpy[:,:,0]
    return image_numpy.astype(imtype)     
            
class HEATMAPS():
    def __init__(self):
        super(HEATMAPS,self).__init__()
        
    def get_face_crop(self,image,face_landmarks,box=False,gray = True):
        face_oval = list(mp_face_mesh.FACEMESH_FACE_OVAL)
        width, height = image.shape[1],image.shape[0]
        cropped_frame = np.zeros_like(image)

        if box:
            x_min, y_min = width, height
            x_max, y_max = 0, 0
            for landmark in face_landmarks:
                x, y = int(landmark[0] * width), int(landmark[1] * height)
                x_min = min(x_min, x)
                y_min = min(y_min, y)
                x_max = max(x_max, x)
                y_max = max(y_max, y)            
            cropped_frame[y_min:y_max, x_min:x_max] = image[y_min:y_max, x_min:x_max]
        else:
            routes_idx=[]
            p1 = [pair[0]for pair in face_oval]
            p2 = [pair[1]for pair in face_oval]
            #init_p1 = p1[0]
            init = p2[0]
            for _ in range(len(face_oval)):
                index = p1.index(init)
                init = p2[index]                
                routes_idx.append((p1[index],p2[index]))
            
            routes=[]
            for source_idx, target_idx in routes_idx:
                source = face_landmarks[source_idx]
                target = face_landmarks[target_idx]
                relative_source = (int(image.shape[1] * source[0]), int(image.shape[0] * source[1]))
                relative_target = (int(image.shape[1] * target[0]), int(image.shape[0] * target[1]))
                routes.append(relative_source)
                routes.append(relative_target) 

            mask = np.zeros((image.shape[0], image.shape[1]))                          
            mask = cv2.fillConvexPoly(mask,np.array(routes),1)
            mask = mask.astype(bool)
            cropped_frame[mask] = image[mask]
            if gray:
                cropped_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)
            return cropped_frame 
    
        
    def skin_detection(self,frame,signer):    
        space = cv2.cvtColor(frame, cv2.COLOR_RGB2YCrCb)
        if signer =="Marcel":
            lower_skin = np.array([60, 150, 77])   
            upper_skin = np.array([255, 190, 120])  
        elif signer =="Jay":
            lower_skin = np.array([30, 127, 77])   
            upper_skin = np.array([255, 190, 125]) 
        elif signer =="Rachel":
            lower_skin = np.array([128, 141, 107])   
            upper_skin = np.array([255, 190, 120]) 
            # lower_skin = np.array([30, 130, 90])   
            # upper_skin = np.array([255, 190, 125])    
        else:
            raise TypeError("Please set the signer into Marcel, Rachel or Jay. Skin_detection function in utils.py") 
        
        mask = cv2.inRange(space, lower_skin, upper_skin)
        # remove noise
        #mask = cv2.erode(mask, np.ones((3,3), np.uint8), iterations=2)
        mask = cv2.dilate(mask, np.ones((5,5), np.uint8), iterations=1)
        skin = cv2.cvtColor(cv2.bitwise_and(frame, frame, mask=mask), cv2.COLOR_BGR2GRAY)
        return skin 
    
    def get_edge(self,cropped_frame):                
        blurred = cropped_frame #cv2.GaussianBlur(cropped_frame, (3, 3), 0)
        
        grad_x = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
        abs_grad_x = cv2.convertScaleAbs(grad_x)
        abs_grad_y = cv2.convertScaleAbs(grad_y)
        cropped_frame = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)  
        return cropped_frame

    def Rachel_hair_removal(self,face,hand,skin):
        face[face !=0] = 1
        hand[hand !=0] = 1
        mask = hand + face
        mask[mask > 1] = 1
        mask = cv2.dilate(mask[0], np.ones((5,5), np.uint8), iterations=1)
        mask = cv2.erode(mask, np.ones((5,5), np.uint8), iterations=1)[np.newaxis,...]
        return mask * skin

    def crop_hand_gray_normalised(self,signer,frame,hand,face_mask,SAM_hand=False, SAM_face=False, SAM_skin=False,SAM_hand_edge = False, SAM_face_edge = False, SAM_skin_edge = False):
        if SAM_hand:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            hand = (gray*hand).astype('uint8')[0]    
            if SAM_hand_edge:
                hand = self.get_edge(hand)                      
            hand = np.expand_dims(hand,axis=0)/255
                    
        if SAM_face:
            face = self.get_face_crop(frame,face_mask)            
            if SAM_face_edge:
                face = self.get_edge(face)
            face = np.expand_dims(face,axis=0)/255
            
        if SAM_skin:
            skin = self.skin_detection(frame,signer)
            if SAM_skin_edge:
                skin = self.get_edge(skin)                   
            skin = np.expand_dims(skin,axis=0)/255
            
        if SAM_hand and SAM_face and SAM_skin:
            skin = self.Rachel_hair_removal(face,hand,skin)
            return skin 
            
        if SAM_hand and SAM_face:
            return (np.concatenate((hand, face)))
        elif SAM_skin:
            return skin  
        elif SAM_hand:
            return hand
        elif SAM_face:
            return face  
        else:    
            raise TypeError("Please set the correct flags for SAM hand and face masks")


    def get_heatmaps_crops(self,input_frame,MP_results_gen,GAN_model, opt,iii=0, hand_mask=None,face_mask=None):
        resolution = opt.loadSize
        MP_results_gen = MP_results_gen*resolution 

        # First, create a HeatMap representation from the MediaPipe tensor
        results_pose = MP_results_gen[:6]
        results_LH = MP_results_gen[6:27]
        results_RH = MP_results_gen[27:48]
        results_face = MP_results_gen[48:176]
        results_hip = MP_results_gen[176:]

        face_connections = C.FACE_CONNECTIONS_SAM
        heat_map_dim = 5 + 40 + len(face_connections) + 3
        heat_map = np.zeros((heat_map_dim, resolution, resolution), np.uint8)
        

        # MP Body
        draw_line_nonan(heat_map[0], (results_pose[0]), (results_pose[1]), c=(1, 1, 1), t=1, width=1)
        # Left
        draw_line_nonan(heat_map[1], (results_pose[0]), (results_pose[2]), c=(1, 1, 1), t=1, width=1)
        # draw_line_nonan(heat_map[2], (results_pose[2]), (results_pose[4]), c=(1, 1, 1), t=1, width=1)
        draw_line_nonan(heat_map[2], (results_pose[2]), (results_LH[0]), c=(1, 1, 1), t=1, width=1)
        # Right
        draw_line_nonan(heat_map[3], (results_pose[1]), (results_pose[3]), c=(1, 1, 1), t=1, width=1)
        # draw_line_nonan(heat_map[4], (results_pose[3]), (results_pose[5]), c=(1, 1, 1), t=1, width=1)
        draw_line_nonan(heat_map[4], (results_pose[3]), (results_RH[0]), c=(1, 1, 1), t=1, width=1)

        # MP Hands
        for i in range(5):
            draw_line_nonan(heat_map[4 + 4 * i + 1], (results_LH[0]), (results_LH[i * 4 + 1]), c=(1, 1, 1), t=1, width=1)
            draw_line_nonan(heat_map[4 + 4 * i + 2], (results_LH[i * 4 + 1]), (results_LH[i * 4 + 2]), c=(1, 1, 1), t=1, width=1)
            draw_line_nonan(heat_map[4 + 4 * i + 3], (results_LH[i * 4 + 2]), (results_LH[i * 4 + 3]), c=(1, 1, 1), t=1, width=1)
            draw_line_nonan(heat_map[4 + 4 * i + 4], (results_LH[i * 4 + 3]), (results_LH[i * 4 + 4]), c=(1, 1, 1), t=1, width=1)

        for i in range(5):
            draw_line_nonan(heat_map[24 + 4 * i + 1], (results_RH[0]), (results_RH[i * 4 + 1]), c=(1, 1, 1), t=1, width=1)
            draw_line_nonan(heat_map[24 + 4 * i + 2], (results_RH[i * 4 + 1]), (results_RH[i * 4 + 2]), c=(1, 1, 1), t=1, width=1)
            draw_line_nonan(heat_map[24 + 4 * i + 3], (results_RH[i * 4 + 2]), (results_RH[i * 4 + 3]), c=(1, 1, 1), t=1, width=1)
            draw_line_nonan(heat_map[24 + 4 * i + 4], (results_RH[i * 4 + 3]), (results_RH[i * 4 + 4]), c=(1, 1, 1), t=1, width=1)

        ## FACE
        for c, connection in enumerate(face_connections):
            new_connection = (GAN_model.face_points[connection[0]], GAN_model.face_points[connection[1]])
            draw_line_nonan(heat_map[45 + c], (results_face[new_connection[0]]), (results_face[new_connection[1]]), c=(1, 1, 1), t=1, width=1)

        # MP Hip
        draw_line(heat_map[169], results_hip[0],  results_hip[1], c=(1, 1, 1), t=1, width=1)
        draw_line(heat_map[170], results_hip[0], results_pose[0], c=(1, 1, 1), t=1, width=1)
        draw_line(heat_map[171], results_hip[1], results_pose[1],  c=(1, 1, 1), t=1, width=1)
        # draw_line(heat_map[170], results_pose[0], results_hip[0], c=(1, 1, 1), t=1, width=1)
        # draw_line(heat_map[171], results_pose[1], results_hip[1], c=(1, 1, 1), t=1, width=1)
        
        
        face = None
        
        if GAN_model.opt.face_mesh:
            face_mesh_tensor = MP_results_gen[176:]
            face_middle = face_mesh_tensor.squeeze().mean(dim=0).int()

            face_mesh_np = draw_face_mesh_small_tensor(np.zeros((GAN_model.opt.loadSize, GAN_model.opt.loadSize)),
                                                    (face_mesh_tensor.squeeze()).round().int())
            face_mesh_tensor_heat_map = torch.tensor(face_mesh_np).unsqueeze(0).float()
            if GAN_model.opt.no_face_landmarks:
                heat_map = heat_map[:45]
            heat_map = torch.cat((torch.tensor(heat_map).float(), face_mesh_tensor_heat_map), dim=0)

            face = torch.tensor([int(face_middle[1] - GAN_model.opt.actual_face_size / 2),
                                int(face_middle[1] + GAN_model.opt.actual_face_size / 2),
                                int(face_middle[0] - GAN_model.opt.actual_face_size / 2),
                                int(face_middle[0] + GAN_model.opt.actual_face_size / 2)])
        else:
            face_coord = torch.tensor(heat_map)[45:].sum(dim=0)
            if face_coord.any():
                face_top = face_coord.nonzero()[0]
                face_bottom = face_coord.nonzero()[-1]
                face_middle = ((face_top + face_bottom) / 2).int()
            face = torch.tensor([int(face_middle[1] - GAN_model.opt.actual_face_size / 2),
                                int(face_middle[1] + GAN_model.opt.actual_face_size / 2),
                                int(face_middle[0] - GAN_model.opt.actual_face_size / 2),
                                int(face_middle[0] + GAN_model.opt.actual_face_size / 2)])
        
        if not torch.is_tensor(heat_map):
            heat_map = torch.tensor(heat_map)
            
        heat_map_2 = copy.copy(heat_map)     

        # set poses       
        heat_map =[]
        if not opt.remove_body_pose:
            heat_map.append(heat_map_2[:5])    
                
        if not opt.remove_hand_pose:
            heat_map.append(heat_map_2[5:45]) 
            
        if not opt.remove_face_pose:
            heat_map.append(heat_map_2[45:169])
                                
        if not opt.remove_hip_pose:
            heat_map.append(heat_map_2[169:172])
                        
        heat_map = np.concatenate(heat_map, axis=0)

        # face_mesh
        if opt.face_mesh:
            heat_map = np.concatenate((heat_map, heat_map_2[-1:]), axis=0) 
        
        if opt.sam:
            # do sam
            cropped_hand = self.crop_hand_gray_normalised(opt.signer,input_frame,hand_mask,face_mask,SAM_hand=opt.hand_crop, SAM_face=opt.face_crop, SAM_skin=opt.skin_crop, \
                SAM_hand_edge = opt.hand_edge, SAM_face_edge = opt.face_edge, SAM_skin_edge = opt.skin_edge)
                
            # Normalisation
            if opt.crop_normalise:
                handcrop_transform = transforms.Compose([transforms.Normalize((0.5,), (0.5,))])
                if opt.hand_crop and opt.face_crop and opt.skin_crop:
                    cropped_hand[0] = np.array(handcrop_transform(torch.from_numpy(cropped_hand[0].astype('float16')).unsqueeze(dim=0)))
                elif opt.hand_crop and opt.face_crop:
                    cropped_hand[1] = np.array(handcrop_transform(torch.from_numpy(cropped_hand[1].astype('float16')).unsqueeze(dim=0)))
                    cropped_hand[0] = np.array(handcrop_transform(torch.from_numpy(cropped_hand[0].astype('float16')).unsqueeze(dim=0)))
                elif opt.hand_crop:
                    cropped_hand[0] = np.array(handcrop_transform(torch.from_numpy(cropped_hand[0].astype('float16')).unsqueeze(dim=0)))
                elif opt.face_crop:
                    cropped_hand[1] = np.array(handcrop_transform(torch.from_numpy(cropped_hand[1].astype('float16')).unsqueeze(dim=0)))
                else:
                    cropped_hand[0] = np.array(handcrop_transform(torch.from_numpy(cropped_hand[0].astype('float16')).unsqueeze(dim=0)))
            if not torch.is_tensor(cropped_hand):
                cropped_hand = torch.tensor(cropped_hand) 

        # After you've created heatmap label, Concetenate the base image tensor on to the front
        if not torch.is_tensor(heat_map):
            heat_map = torch.tensor(heat_map)            

        return heat_map,cropped_hand
    
    # Convert a heatmap representation to an image
    def convert_limb_heatmap(self,heat_map,imtype=np.uint8):
        heat_map = np.array(heat_map)
        full_heatmap = np.zeros((heat_map.shape[1], heat_map.shape[2]), imtype)
        for frame in heat_map:
            full_heatmap = np.add(full_heatmap,frame)  #full_heatmap + frame
        full_heatmap = ((full_heatmap != 0) == False)*255
        return full_heatmap.astype(imtype)
    
    
    def get_pose_image(self,opt,input_frame,generated,heat_map,crops):
        if opt.hand_crop and opt.face_crop:
            if opt.multi_frames:
                total_maps_per_sample = (len(heat_map)//((opt.num_frames*2)+1)) - len(crops[0])
                input_label = self.convert_limb_heatmap(heat_map[opt.num_frames*total_maps_per_sample:(opt.num_frames+1)*total_maps_per_sample,:,:]).reshape((heat_map.shape[1], heat_map.shape[2], 1))
            else:             
                input_label = self.convert_limb_heatmap(heat_map[:-2]).reshape((heat_map.shape[1], heat_map.shape[2], 1))

            if  opt.crop_normalise:
                if opt.erusion:
                    hand = (crops[0][0].numpy() +1 ) * 255
                    if not opt.merge_crops:
                        body = (crops[0][1].numpy() +1 ) * 255
                else:
                    hand = crops[0][0].numpy() * 255
                    if not opt.merge_crops:
                        body = crops[0][1].numpy() * 255
                hand[hand==0]=255
                if not opt.merge_crops:
                    body[body==0]=255
                if opt.merge_crops:
                    input_label[:,:,0] = (input_label[:,:,0]) + (255 - (hand).astype(np.uint8)) 
                else:                
                    input_label[:,:,0] = (input_label[:,:,0]) + (255 - (hand).astype(np.uint8))  + (255-(body).astype(np.uint8)) 
            else:            
                input_label[:,:,0] = input_label[:,:,0] + (heat_map[-2]*255).numpy().astype(np.uint8) + (heat_map[-1]*255).numpy().astype(np.uint8)
                
        elif opt.hand_crop or opt.face_crop or opt.skin_crop:
            if opt.N2N:
                input_label = self.convert_limb_heatmap(heat_map).reshape((heat_map.shape[1], heat_map.shape[2], 1))
            elif opt.multi_frames:
                total_maps_per_sample = (len(heat_map)//((opt.num_frames*2)+1)) - len(crops[0])
                input_label = self.convert_limb_heatmap(heat_map[opt.num_frames*total_maps_per_sample:(opt.num_frames+1)*total_maps_per_sample,:,:]).reshape((heat_map.shape[1], heat_map.shape[2], 1))
            else:
                input_label = self.convert_limb_heatmap(heat_map[:-1]).reshape((heat_map.shape[1], heat_map.shape[2], 1))
            if opt.crop_normalise:
                if opt.hand_crop or opt.skin_crop:
                    hand = (crops[0].numpy() +1 ) * 255               
                    hand[hand==0]=255                    
                    input_label[:,:,0] = input_label[:,:,0] + (255 - (hand).astype(np.uint8))
                else :
                    if opt.erusion:
                        body = (crops[1].numpy() +1 ) * 255
                    else:
                        body = crops[1].numpy() * 255                    
                    body[body==0]=255
                    input_label[:,:,0] = input_label[:,:,0] + (255-(body).astype(np.uint8)) 
            else:            
                input_label[:,:,0] = input_label[:,:,0] + (heat_map[-1]*255).numpy().astype(np.uint8)          

        else:                    
            input_label = self.convert_limb_heatmap(heat_map).reshape((heat_map.shape[1], heat_map.shape[2], 1))
                
        input_label = np.concatenate((input_label, input_label, input_label), axis=2)
        pose_image = np.ascontiguousarray(input_label)[:, :opt.loadSize]
        pose_image = cv2.cvtColor(pose_image, cv2.COLOR_BGR2RGB)
        input_frame = cv2.resize(input_frame, dsize=(opt.loadSize, opt.loadSize),
                                    interpolation=cv2.INTER_CUBIC)
        output_frame = np.concatenate((input_frame, pose_image, generated), axis=1)

        return output_frame

    def generate_GAN_frame_maps_crops(self,input_frame,maps,crops,GAN_model,opt,detailed_video=False):    
        if crops[0] == None:
            heat_map = np.concatenate(maps, axis=0)  
        else:
            heat_map = np.concatenate((np.concatenate(maps, axis=0), np.concatenate(crops, axis=0)), axis=0)  
               
        # After you've created heatmap label, Concetenate the base image tensor on to the front
        if not torch.is_tensor(heat_map):
            heat_map = torch.tensor(heat_map)
            
        if GAN_model.opt.base_style:
            torch_label = torch.cat((GAN_model.base_tensor, heat_map.float().unsqueeze(0)), dim=1).unsqueeze(0)
        else:
            torch_label = heat_map.float().unsqueeze(0).unsqueeze(0)
        # After you've created the full heatmap label, pass it through to the GAN model
        with torch.no_grad():
            gen = GAN_model.forward(Variable(torch_label),face=None)
            if len(gen) > 3:
                output_frame = []
                #for i in range(0, gen.shape[0], 3):
                    #generated = gen[i:i+3]
                n = int((len(gen)/3) / 2)
                generated = gen[3*n:3*(n+1)]
                generated = np.ascontiguousarray(tensor2im(generated))
                if detailed_video:  
                    output_frame = self.get_pose_image(opt,input_frame,generated,maps[n],crops[n])  
                else:
                    output_frame = generated 
                
            else:
                generated = np.ascontiguousarray(tensor2im(gen))
                if detailed_video:      
                    output_frame = self.get_pose_image(opt,input_frame,generated,heat_map,crops)  
                else:
                    output_frame = generated       

        #cv2.imwrite(f'/home/basheer/Signapse/new/synthetic-signer/Rachel_image/{iii}.jpg',pose_image)
        return output_frame     
    
