import gzip, cv2, torch
import pickle5 as pickle
import numpy as np
from pandas import Series
from scipy.ndimage import gaussian_filter1d
import signapse.constants as C


class INTERPLATION():
    def __init__(self):
        super(INTERPLATION,self).__init__() 
    
        # Interpolate over a numpy array
    def my_interpolate_1d_pandas(self,x):
        x[(x==0)] = np.nan
        return Series(x).interpolate(limit_direction='both').values 
    
    # Interpolate between MediaPipe tensors
    def interpolate_All_MP_Tensors(self,previous_MP_results_inter, no_zero_start=True):
        if no_zero_start:
            # Ensure there's no zeros at the beginning frame
            previous_MP_results_inter[0, 6:6 + 21] = previous_MP_results_inter[previous_MP_results_inter[:, 6 + 1, 0].nonzero()[0].item(),6:6 + 21]
            previous_MP_results_inter[0, 27:27 + 21] = previous_MP_results_inter[previous_MP_results_inter[:, 27 + 1, 0].nonzero()[0].item(),27:27 + 21]

        if len(previous_MP_results_inter.shape) ==2:
            previous_MP_results_inter[:,0], previous_MP_results_inter[:,1] = torch.from_numpy(self.my_interpolate_1d_pandas(previous_MP_results_inter[:,0])), \
                    torch.from_numpy(self.my_interpolate_1d_pandas(previous_MP_results_inter[:,1]))
        else:
            for i in range(previous_MP_results_inter.shape[1]):
                if (0 in previous_MP_results_inter[:,i]) or (previous_MP_results_inter[:,i].isnan().any()):
                    previous_MP_results_inter[:,i,0], previous_MP_results_inter[:,i,1] = torch.from_numpy(self.my_interpolate_1d_pandas(previous_MP_results_inter[:,i,0])), \
                        torch.from_numpy(self.my_interpolate_1d_pandas(previous_MP_results_inter[:,i,1]))
        return previous_MP_results_inter
    
    # Gaussian smoothing
    def smooth_keypoints(self,pose, i, dist):  
        if dist ==None:  
            if i < 6:
                sigma = 11       # body
            elif 6 <= i < 48:
                sigma = 1       # hands
            elif i in C.FCP:
                sigma = 3       # face contour 7
            elif i in C.EYP:
                sigma = 5       # eyes
            elif i in C.MOP:
                sigma = 0.1       # lips
            # elif i ==15 or i==36:   # this helps stabilize the wrist & hand connection
            #     sigma = 9
            # elif i in face_mesh_mop:
            #      sigma = 0.5  
            else:
                sigma = 1
        else:
            sigmas = np.linspace(1, 5, 5)
            sigma_idx = np.clip(np.round(dist * (len(sigmas) - 1)).astype(int), 0, len(sigmas) - 1)
            sigma = int(sigmas[sigma_idx])
            
        x = gaussian_filter1d(pose[:,0].cpu().numpy(),sigma)
        y = gaussian_filter1d(pose[:,1].cpu().numpy(),sigma)
        return np.concatenate((x[:, np.newaxis], y[:, np.newaxis]), axis=1)


class IMAGE_PROCESSING():
    def __init__(self):
        super(IMAGE_PROCESSING,self).__init__()
    
    def load_zipped_pickle(self,filename):
        with gzip.open(filename, 'rb') as f:
            loaded_object = pickle.load(f)
            return loaded_object
        
    def apply_norm(self,cropped_frame,img_centre,min_size):
        cropped_frame = cropped_frame[img_centre[1]:img_centre[1]+img_centre[3], img_centre[0]:img_centre[0]+img_centre[2]]
        return cv2.resize(cropped_frame, (min_size, min_size)) 
    
    def mouth_centering(self,pose,sigma=5):
        if len(pose.shape) ==3:
            centers = torch.mean(pose,dim=1)
            smoothed_centers = torch.zeros_like(centers)
            for i in range(2):
                smoothed_centers[:, i] = torch.tensor(gaussian_filter1d(centers[:, i], sigma))
            different = centers-smoothed_centers        
            centered_keypoints = pose - different.unsqueeze(1)             
        return centered_keypoints