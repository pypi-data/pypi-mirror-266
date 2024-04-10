import imageio, torch
import mediapipe as mp
import signapse.constants as C

class Model():
    def __init__(self):
        super(Model, self).__init__()
        self.mp_holistic = mp.solutions.holistic
              
    def model(self):
        PE_model = self.mp_holistic.Holistic(
            static_image_mode= False,
            model_complexity = 2,
            min_detection_confidence= 0.7,
            min_tracking_confidence = 0.7)
        return PE_model
    
class Video():
    def __init__(self, args):
        super(Video,self).__init__()
        self.args=args  
    
    def get_bounding_box(self, results, image_width, image_height):
        LEFT_SHOULDER = 11
        RIGHT_SHOULDER = 12
        
        # Extract the coordinates of the left and right shoulders landmarks
        left_shoulder_x = results.pose_landmarks.landmark[LEFT_SHOULDER].x * image_width
        left_shoulder_y = results.pose_landmarks.landmark[LEFT_SHOULDER].y * image_height
        right_shoulder_x = results.pose_landmarks.landmark[RIGHT_SHOULDER].x * image_width
        right_shoulder_y = results.pose_landmarks.landmark[RIGHT_SHOULDER].y * image_height
        
        # Calculate the center of the bounding box
        centre_x = (left_shoulder_x + right_shoulder_x) / 2
        centre_y = (left_shoulder_y + right_shoulder_y) / 2

        # Calculate the width of the bounding box
        shoulder_width = abs(right_shoulder_x - left_shoulder_x)
        bbox_width = int(c.SHOULDER_SCALE * shoulder_width)  # Multiplying by 3 might be excessive, adjust as needed
        bbox_width = min(bbox_width, image_width)  # Ensure bbox width doesn't exceed image width

        # Calculate the height of the bounding box
        bbox_height = bbox_width  # Make bounding box square
        bbox_height = min(bbox_height, image_height)  # Ensure bbox height doesn't exceed image height

        # Calculate the top-left corner coordinates of the bounding box
        bbox_x = max(int(centre_x - bbox_width / 2), 0)
        bbox_y = max(int(centre_y - bbox_height / 2), 0)

        return bbox_x, bbox_y, bbox_width, bbox_height
    
    
    def process_video(self):
        loadSize = self.args.opt.loadSize
        try:
            reader = imageio.get_reader(self.args.input_video_path)
            FPS = round(reader.get_meta_data()['fps'])
            total_frames = int((reader.get_meta_data()['fps']) * (reader.get_meta_data()['duration']))
            IMG_SHAPE = torch.tensor((reader.get_data(0).shape[1], reader.get_data(0).shape[0]))
            
            for frame_rgb in reader:                
                MP_results = Model().model().process(frame_rgb)
                image_height, image_width = frame_rgb.shape[:2]
                if image_height == loadSize and image_width == loadSize:
                    img_centre = (0, 0, loadSize, loadSize)
                    break
                elif MP_results.pose_landmarks:     
                    # Get the coordinates of the person's bounding box
                    img_centre = self.get_bounding_box(MP_results, image_width, image_height)
                    break
                else:
                    continue
            
            return img_centre, loadSize,  FPS, total_frames
        except Exception as e:
            raise ValueError('Cannot open the video file. Please check the input video path')
                 